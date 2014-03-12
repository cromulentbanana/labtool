from tastypie.serializers import Serializer

class StrictDateSerializer(Serializer):
	def format_datetime(self, data):
		# Convert datetime to ISO8601 strict per https://github.com/toastdriven/django-tastypie/pull/460
		r = data.isoformat()
		if data.microsecond:
			r = r[:19] + r[26:]
		if r.endswith('+00:00'):
			r = r[:-6] + 'Z'
		return r