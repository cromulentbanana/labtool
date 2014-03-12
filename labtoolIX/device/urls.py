from django.conf.urls import patterns, url


urlpatterns = patterns('',

	url(r'^$', 'device.views.list', name="start"),
	url(r'^links/(?P<device_id>\d+)/$', 'device.views.links', name="links"),
	url(r'^links/(?P<device_id>\d+)/used/$', 'device.views.links', name="links.used"),
	url(r'^linktool/$', 'device.views.batch_link_insertion', name="batch_link_insertion"),
)
