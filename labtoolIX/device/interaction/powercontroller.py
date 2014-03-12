""" This Module contains powercontrol functionality for physical devices.

* TODO: SUN ILOM
* TODO: GUDE PowerSwitch
* TODO: XenDom0
* TODO: XenDomU
* TODO: PowerStrip

To access the devices power control functionality we heavily rely on python
modules for ssh and snmp support. Nothing will work without a working
network connection though.

Each of the classes supports functionality to power on/off/cycle a device
and to get information about its current power status. Future classes should
also implement this to allow consistent usage patterns of this module.

"""

# stdlib imports
import re
import time
import os

# 3rd party lib imports
import ConfigParser
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902

# currently in the same dir as this script
# TODO: make this configurable in settings.py
CONFIGFILE = os.path.dirname(__file__) + '/power.cfg'

# functions
def _SNMP_get(oid, target, community='public', port=161, use_v1=False):
	# variable setup
	cmdGen = cmdgen.CommandGenerator()
	if not use_v1:
		community = cmdgen.CommunityData(unicode(community))
	else:
		community = cmdgen.CommunityData(unicode(community), mpModel=0)

	destination = cmdgen.UdpTransportTarget((target, port))
	retrieve_mib = cmdgen.MibVariable(oid)

	# actual network snmp call
	# FIXME: This probably needs a try catch block
	errorIndication, errorStatus, errorIndex, varBinds = \
			cmdGen.getCmd(community,
							destination,
							retrieve_mib,
							lookupNames=True, lookupValues=True)

	if errorIndication:
		print(errorIndication)
		# FIXME: Print the stuff to logfile
		return False
	elif errorStatus:
		print('%s at %s' % (errorStatus.prettyPrint(),
							errorIndex and varBinds[int(errorIndex) - 1] \
							or '?'))
		return False
	else:
		return varBinds[0][1]


def _SNMP_set(oid, value, target, community='private', port=161, use_v1=False):
# variable setup
	cmdGen = cmdgen.CommandGenerator()
	if not use_v1:
		community = cmdgen.CommunityData(unicode(community))
	else:
		community = cmdgen.CommunityData(unicode(community), mpModel=0)

	destination = cmdgen.UdpTransportTarget((target, port))
	oidValue = ((_format(oid)), value)

	# FIXME: This probably needs a try catch block
	errorIndication, errorStatus, errorIndex, varBinds = \
		cmdGen.setCmd(community, destination, oidValue)

	if errorIndication:
		print(errorIndication)
		# FIXME: Print the stuff to logfile
		return False
	elif errorStatus:
		print('%s at %s' % (errorStatus.prettyPrint(),
							errorIndex and varBinds[int(errorIndex) - 1] \
							or '?'))
		return False
	else:
		return True


def _format(oid):
		"""Format a numerical OID string in the form of 1.3.4.1.2.1 into a tuple"""
		if isinstance(oid, str):
			if re.search('(\d+\.)+\d+', oid):
				tmp = list()
				for ii in oid.split('.'):
					tmp.append(int(ii))
				return tuple(tmp)
		else:
			return oid

		return None


class ILOMSNMP:
	''' Manages SNMP Access to SUN Fire ILOMs

	This class contains wrapper functions for SNMP access to a
	Sun Fire ILOM >v3.0. Currently it is only meant to handle power management.

	Requires the CONFIGFILE global constant to be set to a valid ConfigParse
	compatible config file.

	@author Bernd May <bm@dv-team.de>

	@param target: A unicode string of an ILOM SP hostname or IP address

	@method power_off:   switches off the SYS target of the ILOM SP
	@method power_on:	switches on the SYS target of the ILOM SP
	@method power_cycle: switches off and on the SYS target of the ILOM SP

	@raises ValueError
	'''

	def __init__(self, target):
		''' Creates a configured instance '''
		self.target = unicode(target)
		if CONFIGFILE:
			self._readConfig()
		else:
			raise ValueError('No %s found in path:' % CONFIGFILE)

	def power_off(self, port_id):
		""" Contacts the ILOM via SNMP and switches it off """
		retval = _SNMP_set(self.ILOM_SNMP_POWER,
							self.ILOM_SNMP_POWER_STATES['off'],
							self.target)
		if retval:
			return retval
		else:
			return False

	def power_on(self, port_id):
		""" Contacts the self.ILOM via SNMP and switches it on """
		retval = _SNMP_set(self.ILOM_SNMP_POWER,
							self.ILOM_SNMP_POWER_STATES['on'],
							self.target)
		if retval:
			return retval
		else:
			return False

	def power_cycle(self, port_id):
		""" Contacts the self.ILOM via SNMP and power cycles it"""
		retval = _SNMP_set(self.ILOM_SNMP_POWER,
							self.ILOM_SNMP_POWER_STATES['cycle'],
							self.target)
		if retval:
			return retval
		else:
			return False

	def power_state(self, port_id):
		""" Contacts the self.ILOM via SNMP and gets its current power state"""
		retval = _SNMP_get(self.ILOM_SNMP_POWER, self.target)
		if retval:
			return retval == self.ILOM_SNMP_POWER_STATES['on']
		else:
			return False

	def _readConfig(self):
		# Set Configparser to module default CONFIGFILE
		conf_parse = ConfigParser.SafeConfigParser()
		conf_parse.read(CONFIGFILE)
		# SNMP Configuration
		self.ILOM_SNMP_POWER = conf_parse.get('ILOM', 'power_oid')
		self.ILOM_SNMP_POWER_STATES = \
			dict(on=rfc1902.Integer(conf_parse.get('ILOM', 'power_on')),
					off=rfc1902.Integer(conf_parse.get('ILOM', 'power_off')),
					cycle=rfc1902.Integer(conf_parse.get('ILOM', 'power_cycle')))


class PowerStrip:
	'''Manages SNMP commands for a "Infratec 8 Port power strip"

	This class is an SNMP command wrapper that currently allows to
	get the power state and power off,on,cycle the power ports.
	Ports are numbered from 1-8.

	The SNMP OID configuration and necessary integer values can be found in
	the CONFIGFILE global constant (power.cfg adjacient to this file).

	@author Bernd May <bm@dv-team.de>

	@param string target: unicode string of hostname or IP of power switch

	@method power_off(port_id):   switches off target power port
	@method power_on(port_id):	 switches on target power port
	@method power_cycle(port_id): switches off and on the target power port
	@method power_state(port_id): return On(True) or Off(False) state of port

	@raises ValueError
	'''

	def __init__(self, target):
		''' Return initialized instance '''
		self.target = unicode(target)
		if CONFIGFILE:
			self._readConfig()
		else:
			raise ValueError('No %s found in path:' % CONFIGFILE)

	def _readConfig(self):
		''' Read configuration from POWER_STRIP section of CONFIGFILE '''

		# Set Configparser to module default CONFIGFILE
		conf_parse = ConfigParser.SafeConfigParser()
		conf_parse.read(CONFIGFILE)
		# SNMP Configuration
		self.SNMP_COMMUNITY = conf_parse.get('POWER_STRIP', 'snmp_community')
		self.POWER_OID_BASE = conf_parse.get('POWER_STRIP', 'power_oid_base')
		self.POWER_STATES = dict(
								on=rfc1902.Integer(
									conf_parse.get('POWER_STRIP', 'power_on')),
								off=rfc1902.Integer(
									conf_parse.get('POWER_STRIP', 'power_off')))
		self.CYCLE_INTERVAL = int(conf_parse.get('POWER_STRIP', 'cycle_interval'))
		self.PORT_MAX_NUM = int(conf_parse.get('POWER_STRIP', 'port_max_num'))
		self.POWER_OID_STATES = self.POWER_OID_BASE + '.' + conf_parse.get('POWER_STRIP', 'power_oid_state')
		self.POWER_OID_CYCLE_INTERVAL = self.POWER_OID_BASE + '.' + conf_parse.get('POWER_STRIP', 'power_oid_interval')
		self.POWER_OID_CYCLE = self.POWER_OID_BASE + '.' + conf_parse.get('POWER_STRIP', 'power_oid_cycle')

	def power_off(self, port_id):
		retval = _SNMP_set(self.POWER_OID_STATES + '.' + str(port_id),
							self.POWER_STATES['off'],
							self.target, self.SNMP_COMMUNITY, use_v1=True)
		return retval

	def power_on(self, port_id):
		retval = _SNMP_set(self.POWER_OID_STATES + '.' + str(port_id),
							self.POWER_STATES['on'],
							self.target, self.SNMP_COMMUNITY, use_v1=True)
		return retval

	def power_cycle(self, port_id):
		retval = _SNMP_set(self.POWER_OID_CYCLE + '.' + str(port_id),
							self.POWER_STATES['on'],
							self.target, self.SNMP_COMMUNITY, use_v1=True)
		return retval

	def power_state(self, port_id):
		retval = _SNMP_get(self.POWER_OID_STATES + '.' + str(port_id),
							self.target, self.SNMP_COMMUNITY, use_v1=True)
		if retval:
			return retval == self.POWER_STATES['on']
		else:
			return False


class PowerSwitch:
	'''Manages SNMP commands for a "GUDE Expert Power Control NET 2x6"

	This class is an SNMP command wrapper that currently allows to
	get the power state and power off,on,cycle the power ports.
	Ports are numbered from 1-12 with 1-6 and 7-12 belonging to the A and B
	side respectively.

	The SNMP OID configuration and necessary integer values can be found in
	the CONFIGFILE global constant (power.cfg adjacient to this file).

	@author Bernd May <bm@dv-team.de>

	@param string target: unicode string of hostname or IP of power switch

	@method power_off(port_id):   switches off target power port
	@method power_on(port_id):	 switches on target power port
	@method power_cycle(port_id): switches off and on the target power port
	@method power_state(port_id): return On(True) or Off(False) state of port

	@raises ValueError
	'''

	def __init__(self, target):
		''' Return initialized instance '''
		self.target = unicode(target)
		if CONFIGFILE:
			self._readConfig()
		else:
			raise ValueError('No %s found in path:' % CONFIGFILE)

	def _readConfig(self):
		''' Read configuration from POWER_SWITCH section of CONFIGFILE '''

		# Set Configparser to module default CONFIGFILE
		conf_parse = ConfigParser.SafeConfigParser()
		conf_parse.read(CONFIGFILE)
		# SNMP Configuration
		self.SNMP_COMMUNITY = conf_parse.get('POWER_SWITCH', 'snmp_community')
		self.POWER_OID_BASE = conf_parse.get('POWER_SWITCH', 'power_oid_base')
		self.POWER_STATES = dict(
								on=rfc1902.Integer(
									conf_parse.get('POWER_SWITCH', 'power_on')),
								off=rfc1902.Integer(
									conf_parse.get('POWER_SWITCH', 'power_off')))
		self.CYCLE_INTERVAL = int(conf_parse.get('POWER_SWITCH', 'cycle_interval'))
		self.PORT_MAX_NUM = int(conf_parse.get('POWER_SWITCH', 'port_max_num'))

	def power_off(self, port_id):
		retval = _SNMP_set(self.POWER_OID_BASE + '.' + str(port_id),
							self.POWER_STATES['off'],
							self.target, self.SNMP_COMMUNITY, use_v1=True)
		return retval

	def power_on(self, port_id):
		retval = _SNMP_set(self.POWER_OID_BASE + '.' + str(port_id),
							self.POWER_STATES['on'],
							self.target, self.SNMP_COMMUNITY, use_v1=True)
		return retval

	def power_cycle(self, port_id):
		retval = self.power_off(port_id)
		if retval:
			time.sleep(int(self.CYCLE_INTERVAL))
			retval = self.power_on(port_id)

		return retval

	def power_state(self, port_id):
		retval = _SNMP_get(self.POWER_OID_BASE + '.' + str(port_id),
							self.target, self.SNMP_COMMUNITY, use_v1=True)
		if retval:
			return retval == self.POWER_STATES['on']
		else:
			return False


class XenDom0:
	''' Manages power control for XEN DomUs on a Dom0 via SNMP

	This class is an SNMP command wrapper that currently allows to
	power off, on and cycle a DomU by Name or ID.

	The SNMP OID configuration and necessary string values can be found in
	the CONFIGFILE global constant (power.cfg adjacient to this file).

	@author Bernd May <bm@dv-team.de>

	@param string target: unicode string of hostname or IP of Dom0

	@method power_off(domU_id):   shuts down target DomU with name domU_id
	@method power_on(domU_id):	 starts target DomU with name domU_id
	@method power_cycle(domU_id): reboots the target DomU with name domU_id

	@raises ValueError
	'''

	def __init__(self, target):
		''' Return initialized instance '''

		self.target = unicode(target)
		if CONFIGFILE:
			self._readConfig()
		else:
			raise ValueError('No %s found in path:' % CONFIGFILE)

	def _readConfig(self):
		''' Read configuration from XEN_DOM0 section of CONFIGFILE '''

		# Set Configparser to module default CONFIGFILE
		conf_parse = ConfigParser.SafeConfigParser()
		conf_parse.read(CONFIGFILE)
		# SNMP Configuration
		self.SNMP_COMMUNITY = conf_parse.get('XEN_DOM0', 'snmp_community')
		self.POWER_OID_CMD = conf_parse.get('XEN_DOM0', 'power_oid_cmd')
		self.POWER_OID_CMD_STATUS = conf_parse.get('XEN_DOM0', 'power_oid_cmd_status')
		self.POWER_CMD_STATES = dict(active=conf_parse.get('XEN_DOM0', 'power_cmd_active'),
									inactive=conf_parse.get('XEN_DOM0', 'power_cmd_inactive'))
		self.POWER_OID_CMD_ARG = conf_parse.get('XEN_DOM0', 'power_oid_cmd_arg')
		self.POWER_CMD_ARGS = dict(on=conf_parse.get('XEN_DOM0', 'power_on_arg'),
									off=conf_parse.get('XEN_DOM0', 'power_off_arg'),
									cycle=conf_parse.get('XEN_DOM0', 'power_cycle_arg'),
									state=conf_parse.get('XEN_DOM0', 'power_state_arg'))

	def _get_snmp_power_cmd_state(self):
		''' Return value of the POWER_OID_CMD_STATUS SNMP object.

		This value is either 1 (inactive), 2 (active) or something else which is
		undefined.
		'''

		retval = _SNMP_get(self.POWER_OID_CMD_STATUS, self.target,
							self.SNMP_COMMUNITY)
		return retval

	def _activate_snmp_power_cmd(self):
		''' Set the POWER_OID_CMD_STATUS SNMP object value to active '''

		retval = _SNMP_set(self.POWER_OID_CMD_STATUS, self.POWER_CMD_STATES['active'],
							self.target, self.SNMP_COMMUNITY)
		return retval

	def _deactivate_snmp_power_cmd(self):
		''' Set the POWER_OID_CMD_STATUS SNMP object value to inaktive '''

		retval = _SNMP_set(self.POWER_OID_CMD_STATUS, self.POWER_CMD_STATES['inactive'],
							self.target, self.SNMP_COMMUNITY)
		return retval

	def _set_snmp_power_cmd_args(self, args):
		''' Set the POWER_OID_CMD_ARG SNMP object value to args '''

		if _get_snmp_power_cmd_state() == self.POWER_CMD_STATES['active']:
			retval = _SNMP_set(self.POWER_OID_CMD_ARG, args, self.target,
								self.SNMP_COMMUNITY)
		else:
			retval = False

		return retval

	def _call_snmp_remote_cmd(self, *cmd_args):
		''' Activate SNMP OID command, set arguments and get output value '''

		args = ""
		for arg in cmd_args:
			args + " " + str(arg)

		if not _activate_snmp_power_cmd() or not _set_snmp_power_cmd_args(args):
			return False

		retval = _SNMP_get(self.POWER_OID_CMD, self.target, self.SNMP_COMMUNITY)

		if not _set_snmp_power_cmd_args("") or not _deactivate_snmp_power_cmd():
			return False

		return retval

	def power_off(self, domU_id):
		''' Send shutdown command to domU '''

		retval = _call_snmp_remote_cmd(self.POWER_CMD_ARGS['off'], domU_id)

		return retval

	def power_on(self, domU_id):
		''' Start domU on this Dom0 '''

		retval = _call_snmp_remote_cmd(self.POWER_CMD_ARGS['on'], domU_id)

		return retval

	def power_cycle(self, domU_id):
		''' Send reboot command to domU '''

		retval = _call_snmp_remote_cmd(self.POWER_CMD_ARGS['cycle'], domU_id)

		return retval

	def power_state(self, domU_id):
		''' Get current power state of domU '''

		retval = _call_snmp_remote_cmd(self.POWER_CMD_ARGS['state'], domU_id)

		return retval
