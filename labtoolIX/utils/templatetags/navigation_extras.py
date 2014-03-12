from django.template import Library
import re

register = Library()

@register.simple_tag
def active(request, pattern):
	if pattern == request.path:
		return "active"
	return ""

@register.simple_tag
def active_or_parent(request, pattern):
	if re.match(r'^' + pattern, request.path):
		return "active"
	return ""