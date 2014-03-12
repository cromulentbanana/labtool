# -*- coding: utf-8 -*-
#from django.contrib.auth.decorators import login_required
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy

#from account.views import profile,user_add,verify_token,reset_password,forgot_password,UserListView,user_detail,change_password, user_edit

urlpatterns = patterns('',


#	url(r'^$', profile, name="start"),


	url(r'^login/$',  'django.contrib.auth.views.login',
						{
							'template_name':'account/login.html',
						},
			name='login'
		),



	url(r'^logout/$', 'django.contrib.auth.views.logout',
						{
							'next_page'	 : reverse_lazy('account:login', current_app='account'),
						},
			name="logout"
		),


)
