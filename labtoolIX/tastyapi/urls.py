from device.api import BootmodeResource, DeviceResource, DeviceClassResource, DeviceConsoleResource, DeviceBootmodeResource, PowerPortResource, ConsolePortResource, SwitchPortResource, VlanResource, LinkResource, LinklistResource, DevicePowerControlResource
from reservation.api import ReservationResource
from tastyapi.api import UserResource, UserActiveResource, ApiKeyResource
from django.conf.urls import patterns, include

bootmodeResource = BootmodeResource()
deviceResource = DeviceResource()
devicePowerControlResource = DevicePowerControlResource()
deviceConsoleResource = DeviceConsoleResource()
deviceBootmodeResource = DeviceBootmodeResource()
deviceClassResource = DeviceClassResource()
reservationResource = ReservationResource()

powerportResource = PowerPortResource()
consoleportResource = ConsolePortResource()
switchportResource = SwitchPortResource()
vlanResource = VlanResource()
linkResource = LinkResource()
linklistResource = LinklistResource()

userActiveResource = UserActiveResource()
userResource = UserResource()
apiKeyResource = ApiKeyResource()

urlpatterns = patterns('',
	(r'', include(bootmodeResource.urls)),
	(r'', include(devicePowerControlResource.urls)),
	(r'', include(deviceConsoleResource.urls)),
	(r'', include(deviceBootmodeResource.urls)),
	(r'', include(deviceResource.urls)),
	(r'', include(deviceClassResource.urls)),
	(r'', include(reservationResource.urls)),
	(r'', include(powerportResource.urls)),
	(r'', include(consoleportResource.urls)),
	(r'', include(switchportResource.urls)),
	(r'', include(vlanResource.urls)),
	(r'', include(linkResource.urls)),
	(r'', include(linklistResource.urls)),
	(r'', include(userActiveResource.urls)),
	(r'', include(userResource.urls)),
	(r'', include(apiKeyResource.urls)),
)
