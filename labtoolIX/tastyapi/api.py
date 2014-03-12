from django.contrib.auth.models import User
from django.conf.urls import url
from django.core.exceptions import ObjectDoesNotExist
from tastypie.exceptions import ImmediateHttpResponse, NotFound, BadRequest,HttpResponse
from tastypie.models import ApiKey
from tastypie import http
from tastypie.http import HttpUnauthorized
from tastypie.resources import ModelResource, ALL
from tastyapi.authentication import DefaultAuthentication
from tastypie.authorization import Authorization
from tastypie import fields
#FIXME: from account.adminhelpers import enable_user,disable_user

import random
import string

class UserResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'user'
		excludes = ['password', 'last_login']
		filtering = {
			'username': ALL,
		}
		#list_allowed_methods = ['get', 'post', 'put', 'patch', 'delete']
		list_allowed_methods = ['get']
		authentication = DefaultAuthentication()
		authorization = Authorization()

	def get_object_list(self, request):
		objects = super(UserResource, self).get_object_list(request)
		#if not request.user.is_superuser:
		#	objects = objects.filter(pk=request.user.pk)
		return objects

class UserActiveResource(ModelResource):
	class Meta:
		queryset = User.objects.all()
		resource_name = 'active'
		list_allowed_methods = ['post']
		authentication = DefaultAuthentication()
		authorization = Authorization()

	def prepend_urls(self):
		return [
			url(r"^user/(?P<pk>\w[\w/-]*)/(?P<resource_name>%s)/(?P<command>enable|disable|)/?$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
		]

	def post_detail(self, request, pk, command, **kwargs):
		user = None
		try:
			user = self.cached_obj_get(request, pk=pk)
		except User.DoesNotExist:
			return http.HttpNotFound()

		# check permissions
		if not request.user.is_superuser:
			raise BadRequest("Only a superuser can disable users")

		if command == "disable":
			try:
				raise Exception("Not implemented any more!")
				msg=None
#FIXME:				msg = disable_user(user)
			except Exception,e:
				raise BadRequest("Disabling of user '%s' failed! (%s)" % (user,e))
			raise ImmediateHttpResponse(HttpResponse(msg))

		elif command == "enable":
			try:
#FIXME:				msg = enable_user(user)
				raise Exception("Not implemented any more!")
				msg=None
			except Exception,e:
				raise BadRequest("Enabling user '%s' failed! (%s)" % (user,e))
			raise ImmediateHttpResponse(HttpResponse(msg))
		else:
			raise BadRequest("User command '%s' is not supported. Choose from 'enable' and 'disable'" % command)


class ApiKeyResource(ModelResource):
	user = fields.ToOneField("tastyapi.api.UserResource", "user")

	class Meta:
		queryset = ApiKey.objects.all()
		resource_name = 'apikey'
		list_allowed_methods = ['get', 'post', 'delete']
		authentication = DefaultAuthentication()
		authorization = Authorization()
		always_return_data = True

	def get_object_list(self, request):
		objects = super(ApiKeyResource, self).get_object_list(request)
		objects = objects.filter(user=request.user)
		return objects

	def obj_create(self, bundle, **kwargs):
		# check for old object
		try:
			obj = ApiKey.objects.get(user=bundle.request.user)
			if not bundle.data.get("force", None):
				raise BadRequest("You already have an ApiKey. If you want to replace your key with a new one, specify that with force=1.")
			obj.delete()
		except ObjectDoesNotExist:
			pass

		# delete all sent data
		for key in bundle.data.keys():
			del(bundle.data[key])

		newkey = "".join([random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for x in range(48)])
		bundle.data['user'] = {'pk': bundle.request.user.pk}
		bundle.data['key'] = newkey

		return super(ApiKeyResource, self).obj_create(bundle, **kwargs)

	def obj_delete(self, request=None, **kwargs):
		""" Delete an ApiKey """
		obj = kwargs.pop('_obj', None)

		if not hasattr(obj, 'delete'):
			try:
				obj = self.obj_get(request, **kwargs)
			except ObjectDoesNotExist:
				raise NotFound("A model instance matching the provided arguments could not be found.")

		if obj.user != request.user and not request.user.is_superuser:
			raise ImmediateHttpResponse(HttpUnauthorized("This apikey does not belong to you and you are not a superuser."))

		obj.delete()

	def obj_delete_list(self, request=None, **kwargs):
		""" Disable bulk delete.

		This is, because we'd have to reimplement the obj_delete functionality.
		If needed, this function can be reactivated, if secured correctly.
		"""
		raise NotImplementedError("Deleting object lists is not supported by this resource.")

