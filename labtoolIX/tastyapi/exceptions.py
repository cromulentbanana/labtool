from tastypie.exceptions import BadRequest
from helper import mapResources
from tastyapi.errorgen import generic_error
import json

class JsonBadRequest(BadRequest):
	def __init__(self, message, *args, **kwargs):
		if type(message) != dict:
			message = {'message': message}
		else:
			message = mapResources(message)
		message = json.dumps(message)
		super(JsonBadRequest, self).__init__(message, *args, **kwargs)

class JsonGenericBadRequest(BadRequest):
	def __init__(self, errno, title, message, extra=None, *args, **kwargs):
		message = generic_error(errno, title, message, extra)
		super(JsonGenericBadRequest, self).__init__(message, *args, **kwargs)
