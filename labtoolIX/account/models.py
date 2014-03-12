# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from reservation.models import ReservationGroup


class UserProfile(models.Model):
	# This field is required.
	user              = models.OneToOneField(User)
	created_by        = models.ForeignKey(User, null=True, blank=True, default = None, related_name='created_user')
	supervisor        = models.ForeignKey(User, null=True, blank=True, default = None, related_name='supervises')

	comment	          = models.TextField(blank=True)


	reservation_group = models.ManyToManyField(ReservationGroup, blank=True)


	def  __unicode__(self):
		uid=""
		try:
			uid=self.user.__unicode__()
		except:
			uid=" - unknown - "
		return "Profile of %s." % (uid)



def create_user_profile(sender, instance, created, **kwargs):
	if created:
		UserProfile.objects.create(user=instance)
		return


post_save.connect(create_user_profile, sender=User)


