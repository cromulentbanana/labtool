from django.contrib import admin
from device.models import Device, DeviceClass, PowerPort, ConsolePort, SwitchPort, Vlan, Link, Bootmode

class DeviceAdmin(admin.ModelAdmin):
	list_display = ('name', 'model', 'get_device_classes')

	def get_device_classes(self, obj):
		return ', '.join([d.name for d in obj.deviceClasses.all()])
	get_device_classes.short_description = "DeviceClasses"

class LinkAdmin(admin.ModelAdmin):
	list_display = ('switchPortA','switchPortB')

class SwitchPortAdmin(admin.ModelAdmin):
	list_display = ('device','name')

admin.site.register(Device, DeviceAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(SwitchPort, SwitchPortAdmin)

admin.site.register(Bootmode)
admin.site.register(DeviceClass)
admin.site.register(PowerPort)
admin.site.register(ConsolePort)
admin.site.register(Vlan)
