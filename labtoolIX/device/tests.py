"""
Tests for all Device related functions
"""

import datetime

from django.test import TestCase
from device.models import Device, DeviceClass, PowerPort
from django.contrib.auth.models import User
from django.utils.timezone import utc
from reservation.models import Reservation
from device.interaction import powercontroller
import ssh
import unittest

class PowerTest(TestCase):
	def setUp(self):
		# device classes
		rClass = DeviceClass(name='Router')
		rClass.save()
		sClass = DeviceClass(name='Switch')
		sClass.save()
		rlClass = DeviceClass(name='Routerlab Device')
		rlClass.save()
		lcClass = DeviceClass(name='Labcourse Device')
		lcClass.save()
		lgClass = DeviceClass(name='LoadGen')
		lgClass.save()
		domUClass = DeviceClass(name='VirtualLoadGen')
		domUClass.save()

		# power device classes
		pdClass = DeviceClass(name='PowerDevice')
		pdClass.save()
		pdIlomClass = DeviceClass(name='ILOM')
		pdIlomClass.save()
		pdXenDom0Class = DeviceClass(name='XenDom0')
		pdXenDom0Class.save()
		pdPowerSwitchClass = DeviceClass(name='GUDE Power Switch')
		pdPowerSwitchClass.save()
		pdPowerBarClass = DeviceClass(name='Infratec Power Bar')
		pdPowerBarClass.save()


		# devices
		self.router = Device(name='muc-rj1')
		self.router.save()
		self.router.deviceClasses.add(rClass)
		self.router.deviceClasses.add(rlClass)
		self.router.deviceClasses.add(lcClass)

		self.switch = Device(name='nyc-sc1')
		self.switch.save()
		self.switch.deviceClasses.add(sClass)
		self.switch.deviceClasses.add(rlClass)

		self.domU = Device(name='Loadgen42')
		self.domU.save()
		self.domU.deviceClasses.add(lcClass)
		self.domU.deviceClasses.add(rlClass)
		self.domU.deviceClasses.add(domUClass)

		self.loadgen35 = Device(name='loadgen35')
		self.loadgen35.save()
		self.loadgen35.deviceClasses.add(lcClass)
		self.loadgen35.deviceClasses.add(rlClass)
		self.loadgen35.deviceClasses.add(lgClass)

		# power devices
		self.dom0 = Device(name='LoadgenXenDom0')
		self.dom0.save()
		self.dom0.deviceClasses.add(rlClass)
		self.dom0.deviceClasses.add(pdXenDom0Class)
		self.dom0.deviceClasses.add(pdClass)

		self.ilom = Device(name='loadgen35-sp')
		self.ilom.save()
		self.ilom.deviceClasses.add(rlClass)
		self.ilom.deviceClasses.add(pdIlomClass)
		self.ilom.deviceClasses.add(pdClass)

		self.power_switch = Device(name='PowerSwitch')
		self.power_switch.save()
		self.power_switch.deviceClasses.add(rlClass)
		self.power_switch.deviceClasses.add(pdPowerSwitchClass)
		self.power_switch.deviceClasses.add(pdClass)

		self.power_bar = Device(name='PowerBar 3')
		self.power_bar.save()
		self.power_bar.deviceClasses.add(rlClass)
		self.power_bar.deviceClasses.add(pdClass)
		self.power_bar.deviceClasses.add(pdPowerBarClass)

		# link devices to power devices
		self.pp_xen = PowerPort(device=self.dom0,socketId=1)
		self.pp_xen.save()
		self.domU.power = self.pp_xen

		self.pp_ilom = PowerPort(device=self.ilom,socketId=1)
		self.pp_ilom.save()
		self.loadgen35.power = self.pp_ilom

		self.pp_power_switch_1 = PowerPort(device=self.power_switch,socketId=1)
		self.pp_power_switch_1.save()
		self.switch.power = self.pp_power_switch_1

		self.pp_power_switch_2 = PowerPort(device=self.power_switch,socketId=2)
		self.pp_power_switch_2.save()

	def test_device_power_methods(self):
		with self.assertRaises(UnboundLocalError):
			self.router.on()

		with self.assertRaises(UnboundLocalError):
			self.router.off()

		with self.assertRaises(UnboundLocalError):
			self.router.powercycle()

		with self.assertRaises(UnboundLocalError):
			self.router.isrunning()

		self.router.power = self.pp_power_switch_2
		self.assertTrue(self.router.on())
		self.assertTrue(self.router.off())
		self.assertTrue(self.router.powercycle())
		self.assertTrue(self.router.isrunning())

		self.assertTrue(self.switch.on())
		self.assertTrue(self.switch.off())
		self.assertTrue(self.switch.powercycle())
		self.assertTrue(self.switch.isrunning())

		self.assertTrue(self.domU.on())
		self.assertTrue(self.domU.off())
		self.assertTrue(self.domU.powercycle())
		self.assertTrue(self.domU.isrunning())

		self.assertTrue(self.loadgen35.on())
		self.assertTrue(self.loadgen35.off())
		self.assertTrue(self.loadgen35.powercycle())
		self.assertTrue(self.loadgen35.isrunning())

	def test_power_device_methods(self):
		self.assertTrue(self.dom0.on())
		self.assertTrue(self.dom0.off())
		self.assertTrue(self.dom0.powercycle())
		self.assertTrue(self.dom0.isrunning())

		self.assertTrue(self.ilom.on())
		self.assertTrue(self.ilom.off())
		self.assertTrue(self.ilom.powercycle())
		self.assertTrue(self.ilom.isrunning())

		self.assertTrue(self.power_switch.on())
		self.assertTrue(self.power_switch.off())
		self.assertTrue(self.power_switch.powercycle())
		self.assertTrue(self.power_switch.isrunning())

		self.assertTrue(self.power_bar.on())
		self.assertTrue(self.power_bar.off())
		self.assertTrue(self.power_bar.powercycle())
		self.assertTrue(self.power_bar.isrunning())

	def test_initialize_ssh_client(self):
		self.testclient = powercontroller.initialize_ssh_client()
		self.assertEqual(isinstance(self.testclient, ssh.SSHClient),True)
		# Policy tests
		self.assertEqual(isinstance(self.testclient._policy, ssh.AutoAddPolicy),True)

		self.testclient = powercontroller.initialize_ssh_client(policy='add')
		self.assertEqual(isinstance(self.testclient._policy, ssh.AutoAddPolicy),True)

		self.testclient = powercontroller.initialize_ssh_client(policy='deny')
		self.assertEqual(isinstance(self.testclient._policy, ssh.RejectPolicy),True)

		self.testclient = powercontroller.initialize_ssh_client(policy='')
		self.assertEqual(isinstance(self.testclient._policy, ssh.WarningPolicy),True)

		# HostKey test
		self.testclient = powercontroller.initialize_ssh_client()
		# System Host Keys
		self.assertEqual(isinstance(self.testclient._system_host_keys,ssh.HostKeys),True)
		self.assertNotEqual(self.testclient._system_host_keys.__len__(), 0)

		# FIXME: Add tests for custom host_key files

	def test_interaction_ILOMSNMP(self):
		self.snmp_ilom = powercontroller.ILOMSNMP(unicode('loadgen35-sp'))

		# Test if configuration file exists and was parsed correctly
		self.assertIsNotNone(powercontroller.CONFIGFILE)
		self.assertDictContainsSubset(dict(on=1,off=2,cycle=3),self.snmp_ilom.ILOM_SNMP_POWER_STATES)
		self.assertEqual('1.3.6.1.4.1.42.2.175.102.11.1.1.1.2.4.47.83.89.83',self.snmp_ilom.ILOM_SNMP_POWER)

		# Test that power functions exist, throw no exception and return false
		self.assertFalse(self.snmp_ilom.PowerOn())
		self.assertFalse(self.snmp_ilom.PowerOff())
		self.assertFalse(self.snmp_ilom.PowerCycle())
		self.assertFalse(self.snmp_ilom.PowerIsRunning())

class ReservationTest(TestCase):
	def setUp(self):
		# add a user
		self.user = User(username='test')
		self.user.save()

		# device classes
		rClass = DeviceClass(name='Router')
		rClass.save()
		sClass = DeviceClass(name='Switch')
		sClass.save()
		rlClass = DeviceClass(name='Routerlab Device')
		rlClass.save()
		lcClass = DeviceClass(name='Labcourse Device')
		lcClass.save()

		# devices
		self.d1 = Device(name='muc-rj1')
		self.d1.save()
		self.d1.deviceClasses.add(rClass)
		self.d1.deviceClasses.add(rlClass)
		self.d1.deviceClasses.add(lcClass)

		self.d2 = Device(name='nyc-sc1')
		self.d2.save()
		self.d2.deviceClasses.add(sClass)
		self.d2.deviceClasses.add(rlClass)

	def test_device_reservability(self):
		# add a basic reservation
		r = Reservation(user=self.user)
		r.startTime = datetime.datetime(2112, 10, 12, 10, 0, 0).replace(tzinfo=utc)
		r.endTime   = datetime.datetime(2112, 10, 12, 14, 0, 0).replace(tzinfo=utc)
		r.save()
		r.devices.add(self.d1)
		r.save()

		# device can be reserved if not blocked
		self.assertEqual(True, self.d1.isReservable(
					datetime.datetime(2112, 10, 12,  8, 0, 0).replace(tzinfo=utc),
					datetime.datetime(2112, 10, 12,  9, 0, 0).replace(tzinfo=utc)
		))

		self.assertEqual(True, self.d1.isReservable(
					datetime.datetime(2112, 10, 12,  8,  0,  0).replace(tzinfo=utc),
					datetime.datetime(2112, 10, 12,  9, 59, 59).replace(tzinfo=utc)
		))

		self.assertEqual(False, self.d1.isReservable(
					datetime.datetime(2112, 10, 12,  8, 0, 0).replace(tzinfo=utc),
					datetime.datetime(2112, 10, 12, 10, 0, 0).replace(tzinfo=utc)
		))

		self.assertEqual(False, self.d1.isReservable(
					datetime.datetime(2112, 10, 11,  8, 0, 0).replace(tzinfo=utc),
					datetime.datetime(2112, 10, 16, 10, 0, 0).replace(tzinfo=utc)
		))

		self.assertEqual(True, self.d1.isReservable(
					datetime.datetime(2112, 10, 18,  8, 0, 0).replace(tzinfo=utc),
					datetime.datetime(2112, 10, 20, 10, 0, 0).replace(tzinfo=utc)
		))

	def test_adding_devices_to_reservation(self):
		# add a basic reservation
		r = Reservation(user=self.user)
		r.startTime = datetime.datetime(2112, 10, 12, 10, 0, 0).replace(tzinfo=utc)
		r.endTime   = datetime.datetime(2112, 10, 12, 14, 0, 0).replace(tzinfo=utc)
		r.save()
		r.devices.add(self.d1)
		r.save()

		newRes = r.addDevices(datetime.datetime(2112, 10, 12, 12, 0, 0).replace(tzinfo=utc), [self.d2])

		self.assertEqual(newRes.endTime, datetime.datetime(2112, 10, 12, 14, 0, 0).replace(tzinfo=utc))
		self.assertEqual(newRes.startTime, datetime.datetime(2112, 10, 12, 12, 0, 0).replace(tzinfo=utc))
		self.assertEqual(Reservation.objects.get(id=1).endTime, datetime.datetime(2112, 10, 12, 11, 59, 59).replace(tzinfo=utc))
		self.assertEqual(self.d1 in newRes.devices.all(), True)
		self.assertEqual(self.d2 in newRes.devices.all(), True)
