import datetime
#import dateutil.parser

from tastypie.resources import ALL, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.exceptions import ImmediateHttpResponse, NotFound
from tastypie.http import HttpUnauthorized
from reservation.models import Reservation
from tastyapi.exceptions import JsonGenericBadRequest
from tastyapi.authentication import DefaultAuthentication
from tastyapi.resources import ValidatingModelResource
from tastypie.authorization import Authorization
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import utc
from tastypie.http import HttpBadRequest

from device.api import DeviceResource
from tastyapi.errorgen import generic_error
from errorgen import res_errno_dict
from tastyapi.custom_serializer import StrictDateSerializer

class ReservationResource(ValidatingModelResource):
	user = fields.ToOneField("tastyapi.api.UserResource", "user")
	extends = fields.ToOneField("reservation.api.ReservationResource", "extends", null=True)
	devices = fields.ToManyField("device.api.DeviceResource", "devices")

	class Meta:
		serializer = StrictDateSerializer()
		queryset = Reservation.objects.all()
		resource_name = 'reservation'
		filtering = {
			'id': ALL,
			'user': ALL_WITH_RELATIONS,
			'startTime': ALL,
			'endTime': ALL,
			'extends': ALL_WITH_RELATIONS,
			'devices': ALL_WITH_RELATIONS,
		}
		ordering = ['user', 'startTime', 'endTime']
		list_allowed_methods = ['get', 'post', 'put', 'patch', 'delete']
		authentication = DefaultAuthentication()
		authorization = Authorization() # RW for everybody
		always_return_data = True

	def get_object_list(self, request):
		objects = super(ReservationResource, self).get_object_list(request)
		scope = request.GET.get("scope", None)
		if scope:
			now = datetime.datetime.utcnow().replace(tzinfo=utc)
			if scope == "current":
				return objects.filter(startTime__lte=now, endTime__gte=now)
			elif scope == "future":
				return objects.filter(startTime__gt=now)
			elif scope == "past":
				return objects.filter(endTime__lte=now)
			elif scope == "not_past":
				return objects.filter(endTime__gt=now)
			else:
				return objects.none()
		else:
			return objects

	def _ensureCorrectUser(self, bundle):
		""" Ensure correct reservation ownership.

		 - handle "foruser" parameter, can be used by admins to add
		   reservations for user users
		 - override user parameter, if set, with current authed user
		"""
		bundle.data['real_user'] = bundle.request.user

		if "foruser" in bundle.data:
			if bundle.request.user.is_superuser:
				bundle.data['user'] = bundle.data['foruser']
			else:
				raise ImmediateHttpResponse(HttpUnauthorized(generic_error(
							res_errno_dict["FORUSER_ADMIN_ONLY"],
							"Admins Only",
							"Only a superuser can perform actions for another user.")))
		else:
			bundle.data['user'] = {'pk': bundle.request.user.pk}

		# ensure that no user writes the extends part
		if "extends" in bundle.data:
			del(bundle.data['extends'])

		return bundle

	def _isReservableByUser(self, user, devices, bundle):
		unreservable = filter(lambda dev: not dev.canBeReservedByUser(user), devices)
		if len(unreservable) > 0:
			errormsg = generic_error(
							res_errno_dict["DEV_NOT_ALLOWED"],
							"Insufficient Access for Device",
							"You are not allowed to reserve the following devices: %s" % (", ".join(map(str, unreservable))),
							{'unreservable_devices': unreservable})
			response = self.create_response(bundle.request, errormsg, response_class=HttpBadRequest)
			raise ImmediateHttpResponse(response)

		return True


	def obj_create(self, bundle, **kwargs):
		bundle = self._ensureCorrectUser(bundle)

		# check if user is allowed to reserve devices
		#	for this to work we pre-hydrate the bundle
		#	to get all devices

		dr = DeviceResource()
		devices = map(lambda uri: dr.get_via_uri(uri, request=bundle.request), bundle.data["devices"])
		self._isReservableByUser(bundle.data['real_user'], devices, bundle)

		# NOTE: Uncomment this to set time for past reservation attempts to now
		#if 'startTime' in bundle.data:
		#	# for convenience, set startpoint to now if in the past
		#	now = datetime.datetime.utcnow().replace(tzinfo=utc)
		#	try:
		#		startTime = dateutil.parser.parse(bundle.data['startTime'])
		#		if startTime < now:
		#			print("replacing stuff for your convenience")
		#			bundle.data['startTime'] = str(now)
		#	except ValueError:
		#		pass
		return super(ReservationResource, self).obj_create(bundle, **kwargs)

	def obj_update(self, bundle, **kwargs):
		bundle = self._ensureCorrectUser(bundle)
		return super(ReservationResource, self).obj_update(bundle, **kwargs)

	def obj_delete(self, bundle, **kwargs):
		""" Delete reservation, but with some constraints.

		 - only reservations that have not started can be deleted
		 - superuser can delete for otherusers with foruser?
		"""
		obj = kwargs.pop('_obj', None)

		if not hasattr(obj, 'delete'):
			try:
				obj = self.obj_get(bundle, **kwargs)
			except ObjectDoesNotExist:
				raise NotFound(generic_error(res_errno_dict["RESERVATION_404"], "Reservation not found", "Could not find reservation."))

		# check user
		if obj.user != bundle.request.user and not bundle.request.user.is_superuser:
			raise JsonGenericBadRequest(res_errno_dict["NOT_YOUR_RESERVATION"], "Not Your Reservation", "This reservaton does not belong to you and you are not a superuser.")

		# we only can end not started or running reservations
		now = datetime.datetime.utcnow().replace(tzinfo=utc)
		if obj.endTime <= now:
			raise JsonGenericBadRequest(res_errno_dict["NO_RES_IN_PAST"], "Reservation in the Past", "The end of this reservation lies in the past, therefore it cannot be terminated.")

		if obj.startTime < now:
			obj.delete()
		else:
			# reservation is running, set end time to now
			obj.endTime = now
			obj.save()


	def obj_delete_list(self, **kwargs):
		""" Disable bulk delete.

		This is, because we'd have to reimplement the obj_delete functionality.
		If needed, this function can be reactivated, if secured correctly.
		"""
		raise NotImplementedError("Deleting object lists is not supported by this resource.")
