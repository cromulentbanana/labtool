from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^$', 'device.views.list'),

    # hack fix, would be better if this would be catched earlier
    #(r'^accounts/profile/$', 'device.views.list'),

    # Examples:
    # url(r'^$', 'labtoolIX.views.home', name='home'),
    # url(r'^labtoolIX/', include('labtoolIX.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    #url(r'^reservation/list', 'reservation.views.list'),

	url(r'^api/', include('tastyapi.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

	url(r'^account/', include('account.urls', namespace='account', app_name='account')),

	url(r'^reservation/', include('reservation.urls', namespace='reservation', app_name='reservation')),

    url(r'^device/', include('device.urls', namespace='device', app_name='device')),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'media'}),
)
