from django.conf.urls import patterns, url


urlpatterns = patterns('',
	url(r'^$', 'reservation.views.listCurrent', name="current"),
	url(r'^past$', 'reservation.views.listPast', name="past"),
	url(r'^all$', 'reservation.views.list', name="all"),
)
