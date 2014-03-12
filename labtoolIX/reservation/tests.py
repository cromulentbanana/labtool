"""
Tests for reservation functionality
"""

import datetime

from django.test import TestCase
from device.models import Device, DeviceClass
from django.contrib.auth.models import User
from django.utils.timezone import utc
from reservation.models import Reservation
from django.core.exceptions import ValidationError
import unittest


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

	@unittest.skip("feature not yet implemented")
	def test_no_reservation_creation_in_the_past(self):
		""" Reservations must begin at or after the current system now """
		r = Reservation(user=self.user)
		r.startTime = datetime.datetime(2011, 10, 12, 10, 0, 0).replace(tzinfo=utc)
		r.endTime   = datetime.datetime(2011, 10, 12, 14, 0, 0).replace(tzinfo=utc)
		r.save()
		r.devices.add(self.d1)
		r.save()

		self.assertRaises(ValidationError, r.save)

	def test_simple_reservation_creation(self):
		r = Reservation(user=self.user)
		r.startTime = datetime.datetime(2016, 10, 12, 10, 0, 0).replace(tzinfo=utc)
		r.endTime   = datetime.datetime(2016, 10, 12, 14, 0, 0).replace(tzinfo=utc)
		r.save()
		r.devices.add(self.d1)
		r.save()

		self.assertEqual(Reservation.objects.get(id=1).devices.all()[0], self.d1)

	def test_start_end_time_inverstion_raises_exception(self):
		""" Reservation with begin after end must raise ValidationError """
		r = Reservation(user=self.user)
		r.startTime   = datetime.datetime(2016, 10, 12, 14, 0, 0).replace(tzinfo=utc)
		r.endTime = datetime.datetime(2016, 10, 12, 10, 0, 0).replace(tzinfo=utc)

		self.assertRaises(ValidationError, r.save)

	def test_single_device_conflicting_reservations(self):
		r = Reservation(user=self.user)
		r.startTime = datetime.datetime(2016, 10, 12, 10, 0, 0).replace(tzinfo=utc)
		r.endTime   = datetime.datetime(2016, 10, 12, 14, 0, 0).replace(tzinfo=utc)
		r.save()
		r.devices.add(self.d1)
		r.save()

		# this reservation has a device whose existing reservation conflicts
		r = Reservation(user=self.user)
		r.startTime = datetime.datetime(2016, 10, 12,  9, 0, 0).replace(tzinfo=utc)
		r.endTime   = datetime.datetime(2016, 10, 12, 11, 0, 0).replace(tzinfo=utc)
		r.save()
		r.devices.add(self.d1)
		self.assertRaises(ValidationError, r.save)

	def test_multi_device_conflicting_reservations(self):
		r = Reservation(user=self.user)
		r.startTime = datetime.datetime(2016, 10, 12, 10, 0, 0).replace(tzinfo=utc)
		r.endTime   = datetime.datetime(2016, 10, 12, 14, 0, 0).replace(tzinfo=utc)
		r.save()
		r.devices.add(self.d1)
		r.devices.add(self.d2)
		r.save()

		# this reservation has a device whose existing reservation conflicts
		r = Reservation(user=self.user)
		r.startTime = datetime.datetime(2016, 10, 12,  9, 0, 0).replace(tzinfo=utc)
		r.endTime   = datetime.datetime(2016, 10, 12, 11, 0, 0).replace(tzinfo=utc)
		r.save()
		r.devices.add(self.d2)
		self.assertRaises(ValidationError, r.save)

	def test_bordering_reservations(self):
		""" Reservations may begin at the time dependent reservations end """
		r = Reservation(user=self.user)
		r.startTime = datetime.datetime(2016, 10, 12, 10, 0, 0).replace(tzinfo=utc)
		r.endTime   = datetime.datetime(2016, 10, 12, 14, 0, 0).replace(tzinfo=utc)
		r.save()
		r.devices.add(self.d1)
		r.save()

		# test bordering reservation
		r = Reservation(user=self.user)
		r.startTime = datetime.datetime(2016, 10, 12, 14, 0, 0).replace(tzinfo=utc)
		r.endTime   = datetime.datetime(2016, 10, 12, 15, 0, 0).replace(tzinfo=utc)
		r.save()
		r.devices.add(self.d1)
		self.assertEqual(Reservation.objects.get(id=1).devices.all()[0], self.d1)


	# Only active and future reservations may have device additions
	@unittest.skip("feature not yet implemented")
	def test_active_reservation_device_addition(self):
		""" A new reservation should be created inclding the new devices
		(if possible), old reservation terminated now and new reservation starting
		now
		"""
		pass

	@unittest.skip("feature not yet implemented")
	def test_future_reservation_device_addition_(self):
		pass

	@unittest.skip("feature not yet implemented")
	def test_ended_reservation_device_addition_raises_exception(self):
		pass


	# Only active and future reservations may be time-extended i.e. end-time set to system now
	@unittest.skip("feature not yet implemented")
	def test_active_reservation_extension(self):
		pass

	@unittest.skip("feature not yet implemented")
	def test_future_reservation_extension_raises_exception(self):
		pass

	@unittest.skip("feature not yet implemented")
	def test_ended_reservation_extension_raises_exception(self):
		pass


	# Only active reservations may be terminated i.e. end-time set to system now
	def test_active_reservation_termination(self):
		""" Active reservations should not be running after termination """
		r = Reservation(user=self.user)
		now = datetime.datetime.utcnow().replace(tzinfo=utc)
		r.startTime = now + datetime.timedelta(days=-1)
		r.endTime   = now + datetime.timedelta(days=10)
		r.save(full_clean=False)

		r.terminate(full_clean=False)
		
		self.assertFalse(r.is_running())

	def test_future_reservation_termination_raises_exception(self):
		""" Future reservations may not be terminated """
		r = Reservation(user=self.user)
		now = datetime.datetime.utcnow().replace(tzinfo=utc)
		r.startTime = now + datetime.timedelta(days=10)
		r.endTime   = now + datetime.timedelta(days=12)
		r.save()

		self.assertRaises(ValidationError, r.terminate)

	def test_ended_reservation_termination_raises_exception(self):
		""" Ended reservations may not be terminated """
		r = Reservation(user=self.user)
		now = datetime.datetime.utcnow().replace(tzinfo=utc)
		r.startTime = now + datetime.timedelta(days=-14)
		r.endTime   = now + datetime.timedelta(days=-7)
		r.save(full_clean=False)

		self.assertRaises(ValidationError, r.terminate)

	# Reservations may only be deleted i.e. removed from the database or flagged as deleted and thus never considered by any logic if they have not yet begun
	@unittest.skip("feature not yet implemented")
	def test_active_reservation_deletion_raises_exception(self):
		pass

	@unittest.skip("feature not yet implemented")
	def test_future_active_reservation_deletion(self):
		pass

	@unittest.skip("feature not yet implemented")
	def test_ended_reservation_deletion_raises_exception(self):
		pass
