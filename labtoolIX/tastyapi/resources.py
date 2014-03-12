from tastypie.resources import ModelResource
from django.core.exceptions import ValidationError
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpBadRequest
from tastyapi.helper import mapResources


class ValidatingModelResource(ModelResource):
	""" Extended, validating ModelResource.

		This ModelResource ensures that on object creation full_clean()
		is called. If full_clean() fails, the object is deleted and the
		full_clean() ValidationError is propagated.

		This is needed because save() is not called by the api with
		ManyToMany relationships.
	"""

	def obj_create(self, bundle, **kwargs):
		bundle.obj = self._meta.object_class()

		for key, value in kwargs.items():
			setattr(bundle.obj, key, value)

		bundle = self.full_hydrate(bundle)

		errormsg = None
		try:
			# Save FKs just in case.
			self.save_related(bundle)

			# Save the main object.
			bundle.obj.save()

			# Now pick up the M2M bits.
			m2m_bundle = self.hydrate_m2m(bundle)
			self.save_m2m(m2m_bundle)

			# check if this is still a valid object
			if hasattr(bundle.obj, "check_consistency"):
				# custom consistency checking function available
				errormsg = bundle.obj.check_consistency()
			else:
				bundle.obj.full_clean()
		except ValidationError as e:
			errormsg = {'message': "Your request was aborted because you tried to create an inconsistent object: %s" % ", ".join(e.messages), 'messages': e.messages}

		if errormsg:
			if bundle.obj.id:
				bundle.obj.delete()

			# map resources to REST API locations
			errormsg = mapResources(errormsg)

			response = self.create_response(bundle.request, errormsg, response_class=HttpBadRequest)
			raise ImmediateHttpResponse(response)

		return bundle
