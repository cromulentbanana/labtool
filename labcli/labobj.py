from __future__ import print_function
from resthandler import RestHandler

from helper import lazytimeparse

class Reservation(RestHandler):
	restFields = ['startTime', 'endTime', 'devices', 'user', 'comment', 'extends', 'resource_uri', 'id']
	api_url = "/api/reservation/"

	def __init__(self, startTime, endTime, devices, user, comment="", extends=None, resource_uri=None, id=None):
		self.data = {
			'startTime': lazytimeparse(startTime),
			'endTime': lazytimeparse(endTime),
			'devices': devices,
			'user': user,
			'comment': comment,
			'extends': extends,
			'resource_uri': resource_uri,
			'id': int(id) if id else None,
		}

	def __str__(self):
		return "Reservation from %s to %s for %d device(s) reserved by %s" % (self.startTime, self.endTime, len(self.devices), self.user)

	@staticmethod
	def get_reservations(scope='current', resolve_links=True):
		reservationsMeta = Reservation._getJsonResource("/api/reservation/?limit=0&scope=%s" % (scope,))
		reservations = reservationsMeta["objects"]
	
		if resolve_links:
			# get all devices and user
			reservations = Reservation.resolveLinks(reservations, "devices")
			reservations = Reservation.resolveLinks(reservations, "user")

		return reservations
RestHandler.add_serialization_class(Reservation)

class Device(RestHandler):
	restFields = ['name', 'bootmode', 'comment', 'console', 'deviceClasses', 'model', 'power', 'reserved_until', 'free_until', 'is_reserved', 'id', 'resource_uri']
	restPhonyFields = ['reserved_until', 'free_until', 'is_reserved']
	api_url = "/api/device/"

	def __init__(self, name, bootmode, comment, console, deviceClasses, model, power, free_until=None, reserved_until=None, is_reserved=None, resource_uri=None, id=None):
		self.data = {
			'name': name,
			'bootmode': bootmode,
			'comment': comment,
			'console': console,
			'deviceClasses': deviceClasses,
			'model': model,
			'power': power,
			'resource_uri': resource_uri,
			'id': int(id) if id else None,
			'reserved_until': lazytimeparse(reserved_until),
			'free_until': lazytimeparse(free_until),
			'is_reserved': is_reserved,
		}

	def __str__(self):
		return "Device %s (Model %s)" % (self.name, self.model)

	@staticmethod
	def get_devices(resolve_links=True):
		devices = Device._getJsonResource("/api/device/?limit=0")["objects"]

		if resolve_links:
			devices = Device.resolveLinks(devices, "bootmode")
			devices = Device.resolveLinks(devices, "deviceClasses")

		return devices

	def _powercontrol(self, cmdstr):
		print("foo", "%spowercontrol/?command=%s" % (self.resource_uri,cmdstr))
		return self._getJsonResourceSimple("%spowercontrol/?command=%s" % (self.resource_uri,cmdstr), method='POST')

	def powercycle(self):
		return self._powercontrol("powercycle")

	def on(self):
		return self._powercontrol("on")

	def off(self):
		return self._powercontrol("off")

	def set_bootmode(self, bootmode):
		if isinstance(bootmode, Bootmode):
			bootmode = bootmode.resource_uri

		return self._getJsonResourceSimple("%sbootmode/" % self.resource_uri, method='PATCH', data={'bootmode': bootmode})

	def get_console_uri(self):
		return self._getJsonResource("%sconsole/" % self.resource_uri)

RestHandler.add_serialization_class(Device)

class User(RestHandler):
	restFields = ['username', 'email', 'is_active', 'is_staff', 'is_superuser', 'resource_uri', 'id']
	api_url = "/api/user/"

	def __init__(self, username, email, is_active, is_staff, is_superuser, resource_uri=None, id=None):
		self.data = {
			'username': username,
			'email': email,
			'is_active': is_active,
			'is_staff': is_staff,
			'is_superuser': is_superuser,
			'resource_uri': resource_uri,
			'id': int(id) if id else None,
		}

	def __str__(self):
		return "User %s" % self.username
RestHandler.add_serialization_class(User)

class Bootmode(RestHandler):
	restFields = ['name', 'description', 'deviceClasses', 'resource_uri', 'id']
	api_url = "/api/bootmode/"

	def __init__(self, name, description, deviceClasses, resource_uri=None, id=None):
		self.data = {
			'name': name,
			'description': description,
			'deviceClasses': deviceClasses,
			'resource_uri': resource_uri,
			'id': int(id) if id else None,
		}

	def __str__(self):
		return "Bootmode %s" % self.name

RestHandler.add_serialization_class(Bootmode)

class DeviceClass(RestHandler):
	restFields = ['name', 'description', 'resource_uri', 'id']
	api_url = "/api/deviceclass/"

	def __init__(self, name, description, resource_uri=None, id=None):
		self.data = {
			'name': name,
			'description': description,
			'resource_uri': resource_uri,
			'id': int(id) if id else None,
		}

	def __str(self):
		return "Deviceclass %s" % self.name
RestHandler.add_serialization_class(DeviceClass)

def get_reservations():
	reservations = Reservation.get_reservations()
	print(reservations)
	for r in reservations:
		print("Reservation %s; User %s" % (r.id, r.user.username))
		for device in r.devices:
			print("\t%s" % device)

	print("-------------")
	for device in Device.get_devices():
		print(device, device.deviceClasses)
		print("Device %s, bootmode %s, classes %s" % (device.name, device.bootmode, ",".join(map(str, device.deviceClasses))))
