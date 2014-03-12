import datetime

from django.shortcuts import render_to_response
from django.template import RequestContext
from reservation.models import Reservation
from django.contrib.auth.decorators import login_required
from django.utils.timezone import utc

@login_required
def list(request):
	context = {}

	now = datetime.datetime.utcnow().replace(tzinfo=utc)
	reservations = Reservation.objects.filter(endTime__gte=now).order_by('startTime')
	context['reservations'] = reservations.all()

	return render_to_response("reservation/list.html", context, RequestContext(request))

@login_required
def listCurrent(request):
	context = {}

	now = datetime.datetime.utcnow().replace(tzinfo=utc)
	reservations = Reservation.objects.filter(endTime__gte=now).order_by('startTime')
	context['my_reservations'] = reservations.all().filter(user=request.user.id).all()

	return render_to_response("reservation/list.html", context, RequestContext(request))


@login_required
def listPast(request):
	context = {}

	now = datetime.datetime.utcnow().replace(tzinfo=utc)
	reservations = Reservation.objects.filter(endTime__lte=now).order_by('-startTime')
	context['reservations'] = reservations.all().filter(user=request.user.id).all()

	return render_to_response("reservation/list.html", context, RequestContext(request))
