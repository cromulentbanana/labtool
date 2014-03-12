from django.contrib import admin
from reservation.models import Reservation, ReservationGroup


class ReservationAdmin(admin.ModelAdmin):
	list_display = ('user', 'startTime', 'endTime', 'get_devices_list')

	def get_devices_list(self, obj):
		return ', '.join([d.name for d in obj.devices.all()])
	get_devices_list.short_description = "Devices"

admin.site.register(Reservation, ReservationAdmin)
admin.site.register(ReservationGroup)
