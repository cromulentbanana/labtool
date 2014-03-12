import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import utc
from django.core.exceptions import ValidationError
from durationfield.db.models.fields.duration import DurationField

from tastyapi.errorgen import generic_error
from errorgen import res_errno_dict

class Reservation(models.Model):
	""" Reservation for a number of devices """
	user = models.ForeignKey(User)
	extends = models.ForeignKey("Reservation", blank=True, null=True, default=None)
	comment = models.TextField(blank=True)

	devices = models.ManyToManyField("device.Device")
	startTime = models.DateTimeField()
	endTime = models.DateTimeField()

	@staticmethod
	def runningReservations():
		""" Return all currently running reservations """
		now = datetime.datetime.utcnow().replace(tzinfo=utc)
		return Reservation.objects.filter(startTime__lte=now).filter(endTime__gte=now)

	def is_running(self):
		now = datetime.datetime.utcnow().replace(tzinfo=utc)
		return (self.startTime <= now and self.endTime >= now)

	def is_terminated(self):
		now = datetime.datetime.utcnow().replace(tzinfo=utc)
		return (self.endTime <= now)
		
	def terminate(self, *args, **kwargs):
		""" End reservation of active, otherwise raise error """
		if not self.is_running():
			raise ValidationError("Only running reservations can be terminated.")
		else:
			now = datetime.datetime.utcnow().replace(tzinfo=utc)
			self.endTime = now
			self.save(*args, **kwargs)

	def check_consistency(self, ignoreOverlappingExtend=False):
		# check for broken time
		if self.startTime >= self.endTime:
			return generic_error(
						res_errno_dict["START_BEFORE_END"],
						"Reservation Time Error",
						"The reservations starttime must be before its endtime.")

		# disallow reservations in the past with a time window of one minute
		now = datetime.datetime.utcnow().replace(tzinfo=utc)
		if (now - self.startTime).total_seconds() >= 60:
			if self.id:
				# this is an update ==> check if time has changed
				oldRes = Reservation.objects.get(id=self.id)
				# sometimes we have some mixup with times with and without microseconds
				if abs(oldRes.startTime-self.startTime).total_seconds() >= 1:
					return generic_error(
								res_errno_dict["NO_RES_IN_PAST"],
								"Reservation in the Past",
								"You cannot change a reservation starting time to a time in the past.")
			else:
				# disallow new reservations with a time in the past
				return generic_error(
							res_errno_dict["NO_RES_IN_PAST"],
							"Reservation in the Past",
							"You cannot create a reservation in the past.")

		# do not self-extend!
		if self.extends and self.extends.id == self.id:
			return generic_error(
						res_errno_dict["NO_SELF_EXTENDING"],
						"Self-Extending Disallowed",
						"A reservation cannot extend itself.")

		# check if all devices are reservable
		if self.id:
			if self.devices.count() <= 0:
				return generic_error(
							res_errno_dict["EMPTY_RESERVATION"],
							"Empty Reservation",
							"A reservation must contain at least one device.")


			# handle conflicting reservations
			unreservable = []
			nonConflictingRes = [self.id]
			if self.extends and self.extends.id and ignoreOverlappingExtend:
				nonConflictingRes.append(self.extends.id)

			for device in self.devices.all():
				res = device.getConflictingReservations(self.startTime, self.endTime)

				# we have to filter out our own reseration as we are updating ourself
				res = filter(lambda r: r.id not in nonConflictingRes, res)

				if len(res) > 0:
					unreservable.append((device, res))

			if len(unreservable) > 0:
				msg = ["reservation for device %s conflicts with reservation(s) %s" %
						(dev, ", ".join(map(lambda x: str(x.id), res))) for dev, res in unreservable]
				return generic_error(
							res_errno_dict["CONFLICTING_RESERVATION"],
							"Conflict With Other Reservation",
							"Could not reserve all devices: %s" % (", ".join(msg).capitalize(),),
							{
								'conflicting': {
									'devices': map(lambda x: x[0], unreservable),
									'reservations': map(lambda x: x[1], unreservable),
									'pairs': unreservable,
								}
							})

		return None


	def clean(self, ignoreOverlappingExtend=False):
		super(Reservation, self).clean()

		msgdict = self.check_consistency(ignoreOverlappingExtend)
		if msgdict:
			raise ValidationError(msgdict['message'])


	def addDevices(self, startTime, devices):
		""" Add new devices to this reservation.

		This is done by splitting up the reservation in two reservations. The
		first reservation will end right before the second, new reservation.
		The new reservation will include all devices from the first reservation
		and its extend field will point to the first reservation.

		returns new reservation
		"""
		# create new reservation
		newRes = Reservation()
		newRes.user = self.user
		newRes.startTime = startTime
		newRes.endTime = self.endTime
		newRes.extends = self
		newRes.save()

		newRes.devices.add(*(list(self.devices.all()) + devices))
		# check if reservation is okay "that way"
		newRes.clean(ignoreOverlappingExtend=True)

		# old reservation "ends" one second before new
		self.endTime = startTime - datetime.timedelta(0, 1)
		self.save()
		newRes.save()

		return newRes

	def save(self, *args, **kwargs):
		# ensure model consistency
		if kwargs.pop('full_clean', True):
			self.full_clean()

		super(Reservation, self).save(*args, **kwargs)

	def __unicode__(self):
		return u"%s reserved %s from %s to %s" % (
			self.user.username,
			", ".join(map(lambda x: x.name, self.devices.all())),
			self.startTime,
			self.endTime
		)

class ReservationGroup(models.Model):
	name = models.CharField(max_length=30)
	reservation_time = DurationField()
	reservable_classes = models.ManyToManyField("device.DeviceClass")

	def __unicode__(self):
		return self.name

