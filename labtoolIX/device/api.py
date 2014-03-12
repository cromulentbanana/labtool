from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie import fields, http
from tastypie.authorization import DjangoAuthorization, Authorization
from tastyapi.exceptions import JsonBadRequest
from tastyapi.resources import ValidatingModelResource
from tastyapi.authentication import DefaultAuthentication

from django.db.models import Q
from django.conf.urls import url
from device.models import Bootmode, Device, DeviceClass, PowerPort, ConsolePort, SwitchPort, Vlan, Link


class BootmodeResource(ModelResource):
	deviceClasses = fields.ToManyField("device.api.DeviceClassResource", "deviceClasses")

	class Meta:
		queryset = Bootmode.objects.all()
		resource_name = 'bootmode'
		filtering = {
			'id': ALL,
			'name': ALL,
			'is_destructive': ALL,
			'deviceClasses': ALL_WITH_RELATIONS,
		}
		ordering = ['name']
		list_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
		authentication = DefaultAuthentication()
		authorization = DjangoAuthorization()


class DeviceResource(ModelResource):
	deviceClasses = fields.ToManyField("device.api.DeviceClassResource", "deviceClasses")
	power = fields.ToOneField("device.api.PowerPortResource", "power", null=True)
	console = fields.ToOneField("device.api.ConsolePortResource", "console", null=True)
	bootmode = fields.ForeignKey("device.api.BootmodeResource", "bootmode", null=True)

	class Meta:
		queryset = Device.objects.all()
		resource_name = 'device'
		filtering = {
			'id': ALL,
			'name': ALL,
			'model': ALL,
			'deviceClasses': ALL_WITH_RELATIONS,
			'power': ALL_WITH_RELATIONS,
			'console': ALL_WITH_RELATIONS,
		}
		ordering = ['name', 'model']
		list_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
		authentication = DefaultAuthentication()
		authorization = DjangoAuthorization()

	def dehydrate(self, bundle):
		bundle.data['is_reserved'] = bundle.obj.isReserved()
		bundle.data['free_until'] = bundle.obj.isFreeUntil()
		bundle.data['reserved_until'] = bundle.obj.isReservedUntil()
		return bundle

	def hydrate(self, bundle):
		# preserve 'round-trippable' data, as tastypie docs suggest
		if 'is_reserved' in bundle.data:
			del(bundle.data['is_reserved'])
		if 'free_until' in bundle.data:
			del(bundle.data['free_until'])
		if 'reserved_until' in bundle.data:
			del(bundle.data['reserved_until'])
		return bundle

class DeviceClassResource(ModelResource):
	class Meta:
		queryset = DeviceClass.objects.all()
		resource_name = 'deviceclass'
		filtering = {
			'id': ALL,
			'name': ALL,
		}
		ordering = ['name']
		list_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
		authentication = DefaultAuthentication()
		authorization = DjangoAuthorization()

class PowerPortResource(ModelResource):
	device = fields.ToOneField("device.api.DeviceResource", "device")

	class Meta:
		queryset = PowerPort.objects.all()
		resource_name = 'powerport'
		filtering = {
			'id': ALL,
			'name': ALL,
			'device': ALL_WITH_RELATIONS,
		}
		ordering = ['name']
		list_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
		authentication = DefaultAuthentication()
		authorization = DjangoAuthorization()

class ConsolePortResource(ModelResource):
	device = fields.ToOneField("device.api.DeviceResource", "device")

	class Meta:
		queryset = ConsolePort.objects.all()
		resource_name = 'consoleport'
		filtering = {
			'id': ALL,
			'name': ALL,
			'device': ALL_WITH_RELATIONS,
		}
		ordering = ['name']
		list_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
		authentication = DefaultAuthentication()
		authorization = DjangoAuthorization()

class SwitchPortResource(ModelResource):
	device = fields.ToOneField("device.api.DeviceResource", "device")
	vlans = fields.ToManyField("device.api.VlanResource", "vlans")

	class Meta:
		queryset = SwitchPort.objects.all()
		resource_name = 'switchport'
		filtering = {
			'id': ALL,
			'name': ALL,
			'device': ALL_WITH_RELATIONS,
			'mac': ALL,
			'vlans': ALL_WITH_RELATIONS,
		}
		ordering = ['name', 'mac']
		list_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
		authentication = DefaultAuthentication()
		authorization = DjangoAuthorization()

class VlanResource(ModelResource):
	class Meta:
		queryset = Vlan.objects.all()
		resource_name = 'vlan'
		filtering = {
			'id': ALL,
			'name': ALL,
			'number': ALL_WITH_RELATIONS,
		}
		ordering = ['name']
		list_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
		authentication = DefaultAuthentication()
		authorization = DjangoAuthorization()

class LinkResource(ValidatingModelResource):
	switchPortA = fields.ToOneField(SwitchPortResource, "switchPortA")
	switchPortB = fields.ToOneField(SwitchPortResource, "switchPortB")

	class Meta:
		queryset = Link.objects.all()
		resource_name = 'link'
		filtering = {
			'id': ALL,
			'switchPortA': ALL_WITH_RELATIONS,
			'switchPortB': ALL_WITH_RELATIONS,
		}
		list_allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
		authentication = DefaultAuthentication()
		authorization = DjangoAuthorization()

	def get_object_list(self, bundle):
		objects = super(LinkResource, self).get_object_list(bundle)
		switchPort = bundle.request.GET.get("switchPort", None)
		if switchPort:
			return objects.filter(Q(switchPortA=switchPort)|Q(switchPortB=switchPort))
		return objects


class LinklistResource(LinkResource):
	class Meta:
		queryset = Link.objects.all()
		resource_name = 'linklist'
		filtering = {}
		list_allowed_methods = ['get']
		authentication = DefaultAuthentication()
		authorization = DjangoAuthorization()

	def dehydrate(self, bundle):
		switchPortA = SwitchPortResource().get_via_uri(bundle.data['switchPortA'], request=bundle.request)
		switchPortB = SwitchPortResource().get_via_uri(bundle.data['switchPortB'], request=bundle.request)

		bundle.data.update({
			'switchPortA': {
				'id': switchPortA.id,
				'name': switchPortA.name
			},
			'switchPortB': {
				'id': switchPortB.id,
				'name': switchPortB.name
			},
			'deviceA': {
				'id': switchPortA.device.id,
				'name': switchPortA.device.name
			},
			'deviceB': {
				'id': switchPortB.device.id,
				'name': switchPortB.device.name
			},
		})

		return bundle

	def get_object_list(self, request):
		objects = super(LinkResource, self).get_object_list(request)
		device = request.GET.get("device", None)
		if device:
			#return objects.filter(Q(switchPortA__device=device)).order_by('switchPortA__name')
			return objects.filter(Q(switchPortA__device=device)|Q(switchPortB__device=device))
		return objects

class DevicePowerControlResource(ModelResource):
	class Meta:
		queryset = Device.objects.all()
		resource_name = 'powercontrol'
		list_allowed_methods = ['post']
		authentication = DefaultAuthentication()
		authorization = DjangoAuthorization()

	def prepend_urls(self):
		return [
			#url(r"^(?P<resource_name>%s)/(?P<username>[\w\d_.-]+)/$" % self._meta.resource_name),
			url(r"^device/(?P<pk>\w[\w/-]*)/(?P<resource_name>%s)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
		]

	def post_detail(self, request, pk, **kwargs):
		device = None
		try:
			device = self.cached_obj_get(request, pk=pk)
		except Device.DoesNotExist:
			return http.HttpNotFound()
		# check command
		command = request.POST.get("command", "powercycle")
		if command not in ("on", "off", "powercycle"):
			raise JsonBadRequest("Power command '%s' is not supported. Choose from 'on', 'off' and 'powercycle'" % command)

		# check permissions
		if not request.user.is_superuser or not device.isCurrentlyReservedByUser(request.user):
			raise JsonBadRequest("The device %s is not reserved by you and you are not a superuser." % device.name)

		# do the cycling
		try:
			if command == "on":
				device.on()
			elif command == "off":
				device.off()
			elif command == "powercycle":
				device.powercycle()
			else:
				raise NotImplementedError("You should never see this")
		except UnboundLocalError as e:
			raise JsonBadRequest("The device could not be powercycled: %s" % str(e))


class DeviceConsoleResource(ModelResource):
	class Meta:
		queryset = Device.objects.all()
		resource_name = 'console'
		list_allowed_methods = ['get']
		authentication = DefaultAuthentication()
		authorization = DjangoAuthorization()

	def prepend_urls(self):
		return [
			#url(r"^(?P<resource_name>%s)/(?P<username>[\w\d_.-]+)/$" % self._meta.resource_name),
			url(r"^device/(?P<pk>\w[\w/-]*)/(?P<resource_name>%s)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
		]

	def get_detail(self, request, pk, **kwargs):
		device = None
		try:
			device = self.cached_obj_get(request, pk=pk)
		except Device.DoesNotExist:
			return http.HttpNotFound()

		# check permissions
		if not request.user.is_superuser and not device.isCurrentlyReservedByUser(request.user):
			raise JsonBadRequest("The device %s is not reserved by you and you are not a superuser." % device.name)

		# do the cycling
		# FIXME: @bernd return a device url or something like that
		#        e.g. [telnet|ssh|foo]://$host:$port/
		raise JsonBadRequest("NotImplementedError: We cannot give you any console as this part of labtool has not yet been implemented.")


class DeviceBootmodeResource(DeviceResource):
	class Meta:
		queryset = Device.objects.all()
		resource_name = 'bootmode'
		list_allowed_methods = ['patch']
		authentication = DefaultAuthentication()
		authorization = Authorization()

	def prepend_urls(self):
		return [
			url(r"^device/(?P<pk>\w[\w/-]*)/(?P<resource_name>%s)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
		]

	def update_in_place(self, request, original_bundle, new_data):
		print("PING")
		if "bootmode" not in new_data:
			raise JsonBadRequest("You haven't supplied a bootmode.")

		# ensure we only have bootmode in new_data
		new_data = {'bootmode': new_data['bootmode']}

		# check permissions
		if not request.user.is_superuser or not original_bundle.obj.isCurrentlyReservedByUser(request.user):
			raise JsonBadRequest("The device %s is not reserved by you and you are not a superuser." % original_bundle.obj.name)

		# call original update_in_place method
		super(DeviceBootmodeResource, self).update_in_place(request, original_bundle, new_data)
