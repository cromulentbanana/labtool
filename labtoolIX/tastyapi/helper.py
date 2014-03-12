import importlib

# mapping (strings are used to prevent cyclic imports)
_mapping_resolved = False
resourceMapping = {
	"reservation.models.Reservation": "tastyapi.urls.reservationResource",
	"device.models.Device": "tastyapi.urls.deviceResource",
	"device.models.DeviceClass": "tastyapi.urls.deviceClassResource",
	"device.models.PowerPort": "tastyapi.urls.powerportResource",
	"device.models.ConsolePort": "tastyapi.urls.consoleportResource",
	"device.models.SwitchPort": "tastyapi.urls.switchportResource",
	"device.models.Vlan": "tastyapi.urls.vlanResource",
	"device.models.Link": "tastyapi.urls.linkResource",
	"django.contrib.auth.models.User": "tastyapi.urls.UserResource",
	"tastypie.models.ApiKey": "tastyapi.urls.apiKeyResource",
}

def _getObjFromStr(objstr):
	""" Get an object from a string.

	To avoid import cycles some objects need to
	be loaded lazy. Therefore they are only specified
	by string and imported when needed. This helper
	function provices this functionality.
	"""
	moduleBits = objstr.split('.')
	modulePath, objName = '.'.join(moduleBits[:-1]), moduleBits[-1]
	module = importlib.import_module(modulePath)

	return getattr(module, objName)

def _resolveMapping():
	""" Resolve strings to classes/objects """
	global resourceMapping, _mapping_resolved
	_mapping = resourceMapping
	resourceMapping = {}

	for (k, v) in _mapping.iteritems():
		resourceMapping[_getObjFromStr(k)] = _getObjFromStr(v)

def mapResources(data, mapping=None):
	""" Map Django ORM classes to API resource links.

	Sometimes the tastypie serializers just don't cut it.
	Then we need kittens. And also this helper function.

	In default state, tastypie's default serialize-preparation
	function converts ``unknown'' objects by calling str on
	them. We forestall this by using mapResources,
	which searches through lists and dicts to
	convert all objects to resource uris it recognizes.
	"""
	# check if mapping was resolved
	global _mapping_resolved, resourceMapping
	if not _mapping_resolved:
		_resolveMapping()
		_mapping_resolved = True

	if mapping == None:
		mapping = resourceMapping

	if type(data) in mapping:
		obj = mapping[type(data)]
		return obj.get_resource_uri(data)

	if isinstance(data, (list, tuple)):
		return [mapResources(item, mapping) for item in data]
	elif isinstance(data, dict):
		return dict((key, mapResources(val, mapping)) for (key, val) in data.iteritems())
	else:
		return data
