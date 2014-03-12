from django.shortcuts import render_to_response
from django.template import RequestContext
from device.models import Device, DeviceClass, Link, SwitchPort
from reservation.models import Reservation
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q

from django import forms
from django.forms.formsets import formset_factory
from django.core.exceptions import ObjectDoesNotExist, ValidationError

import re

@login_required
def list(request):
	return render_to_response("device/list.html", {}, RequestContext(request))

""" Form for link editing """
def linkformset_factory(device, extra=1):
	class _LinkForm(forms.Form):
		id = forms.IntegerField(widget = forms.HiddenInput)
		switchPortA = forms.ModelChoiceField(queryset=SwitchPort.objects.filter(device=device),
		                                     initial=0)
		switchPortB = forms.ModelChoiceField(queryset=SwitchPort.objects.all(),
		                                     initial=0)
		comment = forms.CharField(required=False)

		def __init__(self,*args,**kwargs):
			""" Creates devices fields based on Link instance """
			super (_LinkForm, self).__init__(*args,**kwargs)

			devices = Device.objects.order_by('name').all()

			self.fields['deviceA'] = forms.ModelChoiceField(queryset=devices,
			                                                initial=device.pk,
			                                                widget=forms.HiddenInput())
			if self.initial.get('switchPortB'):
				deviceB = self.initial['switchPortB'].device.pk
			else:
				deviceB = 0
			self.fields['deviceB'] = forms.ModelChoiceField(queryset=devices,
				                                            initial=deviceB)

			self.instance = self.initial.get('instance', Link())

		def clean(self):
			self.cleaned_data['id'] = self.initial.get('id')

			if not self.cleaned_data['id']:
				# Form for a link that didn't exist before
				if self._errors.get('id'):
					del self._errors['id']
				if not self.cleaned_data.get('switchPortB') and not self.cleaned_data.get('deviceB'):
					# Nothing was set, so just skip this form
					del self._errors['switchPortB']
					del self._errors['deviceB']
					return self.cleaned_data

			if self.cleaned_data.get('deviceA'):
				del self.cleaned_data['deviceA']
			if self.cleaned_data.get('deviceB'):
				del self.cleaned_data['deviceB']
				
			if self.cleaned_data.get('switchPortA'):
				self.instance.switchPortA = self.cleaned_data.get('switchPortA')	
			if self.cleaned_data.get('switchPortB'):
				self.instance.switchPortB = self.cleaned_data.get('switchPortB')
			if self.cleaned_data.get('comment'):
				self.instance.comment = self.cleaned_data.get('comment')

			try:
				self.instance.full_clean()
			except ObjectDoesNotExist:
				pass # this is fine, it means we have a non existing link that was not added
			except ValidationError:
				pass # Link does not validate, which is also fine since we want to allow overriding

			return self.cleaned_data

		def save(self, commit=True):
			if self.cleaned_data.get('switchPortB') == self.initial.get('switchPortB'):
				# This Link wasn't changed.
				return None
			if not self.instance.id and not self.cleaned_data.get('switchPortB') and not self.cleaned_data.get('deviceB'):
				# Non existing link, nothing to be added.
				return None
						
			if commit:
				# Delete conflicting links
				links = self.instance.check_consistency()
				if links.get('conflictingLinks'):
					for link in links['conflictingLinks']:
						print "! Deleting link to allow override: %s" % link
						link.delete()

				self.instance.save()
			return self.instance

		class Meta:
			model  = Link
			fields = ('switchPortA', 'switchPortB', 'comment')

	return formset_factory(_LinkForm, extra=extra)

@login_required
@staff_member_required
def links(request, device_id):
	context = {}
	
	if device_id:
		device = Device.objects.get(pk=device_id)
		# Get existing links
		links = Link.objects.filter(Q(switchPortA__device=device_id)|Q(switchPortB__device=device_id))
		# Create one form for each link + 1 extra
		LinkFormSet = linkformset_factory(device=device, extra=0 )

		if request.method == 'POST':
			formset = LinkFormSet(request.POST, initial=device.get_possible_links())
			if formset.is_valid():
				instances = filter(None, [form.save() for form in formset])
				context['saved_instances'] = instances
			else:
				pass # fields will show their own error messages.
		else:
			formset = LinkFormSet(initial=device.get_possible_links())

		context['device'] = device
		context['formset'] = formset
		context['available_switchports'] = device.switchports.all()
		context['available_devices'] = Device.objects.all()

	return render_to_response("device/links.html", context, RequestContext(request))


""" Form for batch link insertion """
class BatchLinkForm(forms.Form):
	LINK_PARSE_REGEX = '([a-z0-9_-]*):([a-z0-9/_-]*)<->([a-z0-9_-]*):([a-z0-9/_-]*)'

	text = forms.CharField(required=True,
	                       widget=forms.Textarea(attrs={'class':'large-textarea'}),
	                       label='Insert text in supported link syntax')

	def clean_text(self):
		text = self.cleaned_data.get('text')
		if text:
			links = []
			errors = []
			lines = text.split("\n")
			if lines:
				i = 0
				for line in lines:
					i = i + 1
					line = line.strip()
					if not line: continue # Emtpy line

					# Match RegEx
					match = re.search(self.LINK_PARSE_REGEX, line, re.I)
					if not match:
						errors.append('Parse error in line %d: %s' % (i, line))
						continue
					match = match.groups()
					devices = {}
					ports = {}
					devices['a'], ports['a'], devices['b'], ports['b'] = match

					# Get device objects by name
					for key, device in devices.iteritems():
						try:
							devices[key] = Device.objects.get(name = device)
						except ObjectDoesNotExist:
							errors.append ('Device %s does not exist.' % device)
							devices[key] = None
					
					# Get port objects by name
					for key, port in ports.iteritems():
						device = devices[key]
						if device:
							try:
								ports[key] = SwitchPort.objects.get(device = device, name = port)
							except ObjectDoesNotExist:
								errors.append ('SwitchPort %s:%s does not exist.' % (device, port) )
								ports[key] = None

					# If we have all needed objects, create a Link
					if all(v is not None for v in devices.values() + ports.values()):
						link = Link(switchPortA = ports['a'],
						            switchPortB = ports['b'])

						# Check for existing links that would be overwritten
						check_consistency = link.check_consistency()
						conflicting_links = []
						if 'conflictingLinks' in check_consistency:
							conflicting_links = check_consistency['conflictingLinks']
						
						links.append({
								'link': link,
								'line': i,
								'conflicts': conflicting_links})
			
			if not links:
				raise forms.ValidationError('No links parsed. Please check the syntax.')

			self.cleaned_data['links'] = links

			if errors:
				raise forms.ValidationError(errors)
		return text

@login_required
@staff_member_required
def batch_link_insertion(request):
	context = {'isSaved':False}

	if request.method == 'POST':
		form = BatchLinkForm(request.POST)
		if form.is_valid():
			parsed_links = form.cleaned_data['links']
			context['parsed_links'] = parsed_links
			if request.POST.get('save'):
				links_saved = links_removed = 0

				for link_info in parsed_links:
					print 'Saving link %s' % link_info['link']
					if link_info['conflicts']:
						for link in link_info['conflicts']:
							link.delete()
							links_removed += 1
					try:
						link_info['link'].save()
						links_saved += 1
					except ValidationError as err:
						print 'Error raised: %s' % err

				context['isSaved'] = True
				context['numbers'] = {
					'links_saved': links_saved,
					'links_removed': links_removed
				}

			# Process the data in form.cleaned_data
			# return HttpResponseRedirect(request.get_full_path())

	else:
		form = BatchLinkForm()

	context['form'] = form
	context['syntax'] = form.LINK_PARSE_REGEX

	return render_to_response("device/batch_link_insertion.html", context, RequestContext(request))
