import datetime

from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.timezone import utc
from interaction import powercontroller,bootmanager

class NaturalOrderManager(models.Manager):
	use_for_related_fields = True
	""" Adds option to order_by a field_name, but in natural order, i.e. Foo1 -> Foo2 -> Foo10 """

	def order_natural(self, field_name=None):
		""" Order naturally by field_name.
		Uses primary key if no field_name given.
		Works by first sorting by LENGTH(field_name), so only makes sense
		if the part before the number is the same on all entries.
		"""
		field_name = field_name if field_name else self.model._meta.pk.name
		return self.extra(select={'natural_order_length':('LENGTH(%s)'%field_name)}).order_by(field_name).order_by('natural_order_length')
		
		#The CAST version only works with PostgreSQL
		#cast = "CAST(substring(%s FROM '^[0-9]+') AS INTEGER)" % field_name
		#return self.extra(
		#		select={'natural_order': cast}
		#	).order_by('natural_order')

class Bootmode(models.Model):
	""" Bootmodes (TFTP) allowed for certain device classes"""
	name = models.CharField(max_length=100, unique=True)
	is_destructive = models.BooleanField(default=False, null=False, blank=False)
	deviceClasses = models.ManyToManyField("DeviceClass")
	description = models.TextField(blank=True)

	def __unicode__(self):
		return self.name


class Device(models.Model):
	""" Physical device in our racks """
	name = models.CharField(max_length=100, unique=True)
	model = models.CharField(max_length=100, blank=True)
	deviceClasses = models.ManyToManyField("DeviceClass")
	comment = models.TextField(blank=True)

	power = models.OneToOneField("PowerPort", blank=True, null=True, related_name='powersDevice')
	console = models.OneToOneField("ConsolePort", blank=True, null=True, related_name='consolidatesDevice')

	bootmode = models.ForeignKey("BootMode", blank=True, null=True)

	def __init__(self, *args, **kwargs):
		super(Device, self).__init__(*args, **kwargs)
		if self.bootmode:
			self.old_bootmode_pk = self.bootmode.pk
		else:
			self.old_bootmode_pk = None

	def save(self, *args, **kwargs):
		""" it this device has a bootmode, ensure calling the hook on changes """
		if self.bootmode:
			if self.old_bootmode_pk != self.bootmode.pk:
				""" if this hook throws an exception, we will not save - is this wanted? """
				bootmanager.set_bootmode(self,self.bootmode)
		super(Device, self).save(*args, **kwargs)
		if self.bootmode:
			""" only when save succeeded update locally: """
			self.old_bootmode_pk = self.bootmode.pk

	def isReservable(self, begin, end):
		""" Check if a device is reservable for a certain timeslot. """
		return len(self.getConflictingReservations(begin, end)) == 0

	def isReserved(self):
		""" Check if a device is currently reserved """
		now = datetime.datetime.utcnow().replace(tzinfo=utc)
		return not self.isReservable(now, now)

	def getConflictingReservations(self, begin, end):
		""" Find a conflicting reservation for a certain timeslot. """
		if begin > end:
			raise ValueError("Beginning of reservation must be before end of reservation.")

		qs = self.reservation_set.filter(~(Q(startTime__gt=end) | Q(endTime__lt=begin)))
		return qs

	def canBeReservedByUser(self, user):
		""" Return true if this user is allowed to reserve this type of device """
		if user.is_superuser:
			return True
		return self.deviceClasses.filter(reservationgroup__userprofile__user=user).count() > 0

	def isCurrentlyReservedByUser(self, user):
		""" Check if a device is currently reserved by a user. """
		now = datetime.datetime.utcnow().replace(tzinfo=utc)
		res = self.getConflictingReservations(now, now)
		if res.count() < 1 or res[0].user != user:
			return False
		return True

	def isFreeUntil(self):
		""" Return until when a device is free.

		Returns None when device is not free or free until forever. In this
		case use isFree() to determine which case it is.
		"""
		now = datetime.datetime.utcnow().replace(tzinfo=utc)
		if self.isReserved():
			return None

		nextRes = self.reservation_set.filter(startTime__gte=now).order_by('startTime')

		if nextRes.count() < 1:
			return None

		return nextRes[0].startTime

	def isReservedUntil(self):
		""" Find out until when a device is reserved """
		cdate = datetime.datetime.utcnow().replace(tzinfo=utc)
		returnDate = None

		cres = self.reservation_set.filter(startTime__lte=cdate, endTime__gte=cdate)
		while cres.count() > 0:
			cdate = cres[0].endTime + datetime.timedelta(0, 1)
			returnDate = cdate
			cres = self.reservation_set.filter(startTime__lte=cdate, endTime__gte=cdate)
			print " !=> ", cdate, cres

		return returnDate

	def __unicode__(self):
		return self.name

	def get_possible_links(self):
		""" Returns list of device's switchPorts, extended by information on a Link if it has one.
		Returns a list suitable for a Form's initial data """
		from django.forms.models import model_to_dict
		formset_data = []
		for port in self.switchports.order_natural('name'):
			# Check if there is a link for this port
			link = Link.objects.select_related('switchPortA','switchPortB','switchPortA__device','switchPortB__device').filter(Q(switchPortA=port)|Q(switchPortB=port)).all()[:1]
			if link:
				link = link[0]
				data = model_to_dict(link)
				data['instance'] = link
				# Switch order so that the current device always comes first
				data['switchPortA'] = link.switchPortA if link.switchPortA == port else link.switchPortB
				data['switchPortB'] = link.switchPortB if link.switchPortA == port else link.switchPortA
			else:
				data = {'switchPortA': port }
			formset_data.append(data)
		return formset_data

	def _get_interaction_device(self):
		''' Find out what kind of device we are and return a proper interaction instance '''
		# TODO: put this in django settings?
		#interaction_devices = ['PowerStrip', 'PowerSwitch', 'ILOM', 'XENDom0']
		if self.deviceClasses.filter(name__exact='PowerStrip'):
			return powercontroller.PowerStrip(unicode(self.name))
		elif self.deviceClasses.filter(name__exact='PowerSwitch'):
			return powercontroller.PowerSwitch(unicode(self.name))
		elif self.deviceClasses.filter(name__exact='ILOM'):
			return powercontroller.ILOMSNMP(unicode(self.name))
		elif self.deviceClasses.filter(name__exact='XENDom0'):
			return powercontroller.ILOMSNMP(unicode(self.name))
		else:
			raise UnboundLocalError('No power class associated with %s' % unicode(self.name))

	def on(self, socketId=None):
		""" Switch on the powerdevice of this device """
		if self.deviceClasses.filter(name__exact='PowerDevice') and socketId:
			idev = self._get_interaction_device()
			return idev.power_on(socketId)
		else:
			try:
				power_device = self.power.device
				return power_device.on(self.power.socketId)
			except AttributeError:
				raise UnboundLocalError('No power device associated with %s' % unicode(self.name))

	def off(self, socketId=None):
		""" Switch off the powerdevice of this device """
		if self.deviceClasses.filter(name__exact='PowerDevice') and socketId:
			idev = self._get_interaction_device()
			return idev.power_off(socketId)
		else:
			try:
				power_device = self.power.device
				return power_device.off(self.power.socketId)
			except AttributeError:
				raise UnboundLocalError('No power device associated with %s' % unicode(self.name))

	def powercycle(self, socketId=None):
		""" Powercycle the powerdevice of this device """
		if self.deviceClasses.filter(name__exact='PowerDevice') and socketId:
			idev = self._get_interaction_device()
			return idev.power_cycle(socketId)
		else:
			try:
				power_device = self.power.device
				return power_device.powercycle(self.power.socketId)
			except AttributeError:
				raise UnboundLocalError('No power device associated with %s' % unicode(self.name))

	def isrunning(self, socketId=None):
		""" Return the powerdevice state of this device """
		if self.deviceClasses.filter(name__exact='PowerDevice') and socketId:
			idev = self._get_interaction_device()
			return idev.power_state(socketId)
		else:
			try:
				power_device = self.power.device
				return power_device.isrunning(self.power.socketId)
			except AttributeError:
				raise UnboundLocalError('No power device associated with %s' % unicode(self.name))

	def getValidBootmodes(self):

		bootmodes = set()

		for dc in self.deviceClasses.all():
			bms = Bootmode.objects.filter(deviceClasses__in=[dc.id])
			for b in bms:
				bootmodes.add(b)

		return list(bootmodes)

	def setBootmode(self, bootmode_str):
		""" This method updates the bootmode in the model, 
			the symlink on the bootserver will be changed
			in the save() method, so no inconsistencies can happen """

		#FIXME: throw error instead of returning None
		try:
			bootmode = Bootmode.objects.get(name__exact=bootmode_str)
			if bootmode in self.getValidBootmodes():
				self.bootmode = bootmode
			else:
				return None
		except Bootmode.DoesNotExist:
			return None


		return self.bootmode


class DeviceClass(models.Model):
	""" Classes for identifiying capabilities of devices (or other stuff!). """
	name = models.CharField(max_length=100)
	description = models.TextField(blank=True)

	def __unicode__(self):
		return self.name


class PowerPort(models.Model):
	""" Port that can cycle one power socket """
	device = models.ForeignKey("Device")
	socketId = models.IntegerField()

	def __unicode__(self):
		return u"PowerSocket %d on %s" % (self.socketId, self.device.name)


class ConsolePort(models.Model):
	""" Port for a console on a device"""
	device = models.ForeignKey("Device")
	portId = models.IntegerField()

	def __unicode__(self):
		return u"ConsolePort %d on %s" % (self.portId, self.device.name)


class SwitchPort(models.Model):
	""" Physical switchport """
	name = models.CharField(max_length=100)
	device = models.ForeignKey("Device", related_name='switchports')
	mac = models.CharField(
		max_length=21, blank=True,
		validators=[RegexValidator(regex="^(?:(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}|)$")]
	)
	vlans = models.ManyToManyField("Vlan", blank=True)

	objects = NaturalOrderManager()

	def __unicode__(self):
		return "%s:%s" % (self.device, self.name)


class Vlan(models.Model):
	""" Vlans in the network """
	number = models.IntegerField()
	name = models.CharField(max_length=100)
	comment = models.TextField()

	def __unicode__(self):
		return u"Vlan %d (%s)" % (self.number, self.name)


class Link(models.Model):
	""" Link between two SwitchPorts """
	switchPortA = models.ForeignKey("SwitchPort", related_name='linkA_set')
	switchPortB = models.ForeignKey("SwitchPort", related_name='linkB_set')
	comment = models.TextField(blank=True)

	def check_consistency(self):
		""" Consistency checks, mostly used by restapi.

		Wraps validate_unique() and transforms it into a
		serializer-suitable format.
		"""
		try:
			self.validate_unique()
		except ValidationError, e:
			if "switchPortA" in e.message_dict or "switchPortB" in e.message_dict:
				# we got conflicting links, filter out Nones and convert to a unique set
				conflictingLinks = set( filter(lambda x: x is not None, self._getConflictingLinks()) )
				return {
					'message': ", ".join(map(lambda x: ", ".join(x), e.message_dict.values())),
					'conflictingLinks': conflictingLinks,
				}
			else:
				return {
					'message': ", ".join(map(lambda x: ", ".join(x), e.message_dict))
				}

		return None

	def _getConflictingLinks(self):
			linksA = Link.objects.filter(
				(~Q(id=self.id)) &
				(Q(switchPortA=self.switchPortA) |
				Q(switchPortA=self.switchPortB))
			)
			linksB = Link.objects.filter(
				(~Q(id=self.id)) &
				(Q(switchPortB=self.switchPortA) |
				Q(switchPortB=self.switchPortB))
			)

			return (
				linksA[0] if len(linksA) > 0 else None,
				linksB[0] if len(linksB) > 0 else None,
			)

	def validate_unique(self, exclude=None):
		super(Link, self).validate_unique(exclude)

		if not exclude or not ("switchPortA" in exclude and "switchPortB" in exclude):
			# check if there is any other link pointing to one of the devices
			linkA, linkB = self._getConflictingLinks()

			if linkA or linkB:
				# uh oh..

				def genLinkError(device, link):
					otherDevice = link.switchPortB if device == link.switchPortA else link.switchPortA
					return "Port %s is already referenced by another link to %s" % (device, otherDevice)

				vdict = {}
				if linkA:
					vdict["switchPortA"] = [genLinkError(self.switchPortA, linkA)]

				if linkB:
					vdict["switchPortB"] = [genLinkError(self.switchPortB, linkB)]

				raise ValidationError(vdict)

	def __unicode__(self):
		return "%s:%s <--> %s:%s" % (
			self.switchPortA.device, self.switchPortA.name,
			self.switchPortB.device, self.switchPortB.name,
		)

	def save(self, *args, **kwargs):
		# ensure model consistency
		if kwargs.pop('full_clean', True):
			self.full_clean()

		super(Link, self).save(*args, **kwargs)
