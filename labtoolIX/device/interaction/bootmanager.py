
""" This Module sets the bootmode on a remote or local bootserver


"""

from django.conf import settings
import subprocess

def exec_script(script,device_str,bootmode_str):
	print "executing %s '%s' '%s'" % (script,device_str,bootmode_str)
	subprocess.call([script, device_str, bootmode_str ])
	# FIXME: execute subprocess!


def set_bootmode(device,bootmode):

	try:
		if settings.BOOTMODESCRIPT:
			exec_script(settings.BOOTMODESCRIPT,device.name,bootmode.name)
		else:
			print "ERROR: Cannot set bootmode, BOOTMODESCRIPT not configured in settings"
	except AttributeError:
		print "ERROR: Please add BOOTMODESCRIPT to settings!"

