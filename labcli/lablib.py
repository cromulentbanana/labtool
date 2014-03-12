from __future__ import print_function

import urlparse
import sys

from helper import gen_table, strtodatetime, tznow
from labobj import Reservation, Device, User, Bootmode, DeviceClass
from config import DATETIME_FMTSTR

def _get_device(device):
		devobj = Device.find(name=device)
		if len(devobj) != 1:
			print("Device '%s' could not be found" % device, file=sys.stderr)
			sys.exit(1)
		return devobj[0]

def show_reservations(scope):
	reservations = Reservation.get_reservations(scope)
	table = gen_table(["id", "start time", "end time", "user/devices"])
	for res in reservations:
		userdev = [res.user.username] + ["  %s" % dev.name for dev in res.devices]
		table.add_row([res.id, res.startTime.strftime(DATETIME_FMTSTR), res.endTime.strftime(DATETIME_FMTSTR), "\n".join(userdev)])
	print(table)

def show_devices(show_free_only=True):
	devices = Device.get_devices()
	table = gen_table(["Device", "Model"])
	table.hrules = False
	for dev in devices:
		if show_free_only and dev.is_reserved:
			continue
		table.add_row([dev.name, dev.model])
	print(table)

def reserve(starttime, endtime, devicestrs, comment=""):
	starttime = strtodatetime(starttime, "starttime")
	endtime = strtodatetime(endtime, "endtime")
	devices = []
	for dev in devicestrs:
		devices.append(_get_device(dev).resource_uri)
	myuser = User.find(name=User.labUser)[0]
	res = Reservation(starttime, endtime, devices, myuser.resource_uri, comment)

	retmsg = res.save()
	if type(retmsg) == dict:
		if 'messages' in retmsg:
			for message in retmsg['messages']:
				print("Error:", message, file=sys.stderr)
		else:
			print(retmsg['message'], file=sys.stderr)
		sys.exit(1)
	else:
		print("Successfully reserved all devices and created reservation %d" % retmsg.id)

def extend_reservation(resid, endtime):
	endtime = strtodatetime(endtime)

	reservation = Reservation.get_objects(id=resid)
	if len(reservation) != 1:
		print("Could not find reservation with id '%s'" % resid, file=sys.stderr)
		sys.exit(1)
	reservation = reservation[0]
	reservation.endTime = endtime
	errmsg = reservation.save()
	if type(errmsg) == dict:
		print(errmsg['message'], file=sys.stderr)
		sys.exit(1)
	else:
		print("Reservation %s extended until: %s" % (reservation.id, endtime.strftime(DATETIME_FMTSTR)))

def end_reservation(resid):
	reservation = Reservation.get_objects(id=resid)
	if len(reservation) != 1:
		print("Could not find reservation with id '%s'" % resid, file=sys.stderr)
		sys.exit(1)
	reservation = reservation[0]
	errmsg = reservation.delete()
	if type(errmsg) == dict:
		# try to set endtime to now
		now = tznow()
		reservation.endTime = now
		errmsg = reservation.save()
		if type(errmsg) == dict:
			print(errmsg['message'], file=sys.stderr)
			sys.exit(1)
		else:
			print("Reservation %s terminated by setting endtime to %s" % (reservation.id, now.strftime(DATETIME_FMTSTR)))
	else:
		print("Reservation %s terminated" % reservation.id)

def powercycle(device):
	devobj = _get_device(device)
	errmsg = devobj.powercycle()
	print(errmsg)
	if errmsg:
		print(errmsg['message'], file=sys.stderr)
		sys.exit(1)
	else:
		print("Successfully powercycled device '%s'" % device)

def access_serial_console(device):
	devobj = _get_device(device)
	# check if we can get to the console

	uri = devobj.get_console_uri()
	if type(uri) == dict and 'message' in uri:
		print("Error:", uri['message'], file=sys.stderr)
		sys.exit(1)
	print("Api returned '%s' - the rest of this operation is currently a stub" % (uri,))
	print("urlparts: ", urlparse.urlparse(uri))


def get_bootmode(device):
	devobj = _get_device(device)
	if devobj.bootmode:
		name = Bootmode.from_uri(devobj.bootmode).name
	else:
		name = "<unset>"
	print("Bootmode for device '%s' is currently: %s" % (devobj.name, name))

def set_bootmode(device, bootmode):
	devobj = _get_device(device)
	bootmodeRaw = Bootmode.find(name=bootmode)
	if len(bootmodeRaw) != 1:
		print("Could not find bootmode '%s'" % bootmode, file=sys.stderr)
		sys.exit(1)
	bootmode = bootmodeRaw[0]

	errmsg = devobj.set_bootmode(bootmode)
	if errmsg:
		print(errmsg['message'], file=sys.stderr)
		sys.exit(1)
	else:
		print("Successfully set boot mode of '%s' to '%s'" % (devobj.name, bootmode.name))

def list_bootmodes(device=None):
	modes = []
	if device:
		devobj = _get_device(device)
		if len(devobj.deviceClasses) == 0:
			print("The device '%s' has not any serverclass associated with it, therefore it doesn't have any special bootmodes." % devobj.name, file=sys.stderr)
			sys.exit(1)

		classes = DeviceClass.get_apilink_list(devobj.deviceClasses)
		for clazz in classes:
			bootmodes = Bootmode.get_objects(deviceClasses=clazz.id, resolve_links=False)
			modes.extend([mode.name for mode in bootmodes])
		modes = list(set(modes))
	else:
		bootmodes = Bootmode.get_objects()
		modes = [mode.name for mode in bootmodes]
	print("The following bootmodes are available")
	for mode in modes:
		print("    %s" % mode)
