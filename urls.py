from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template

from snippet.forms import EntryForm

urlpatterns = patterns('',
	url(r'^$', direct_to_template,
		{ 'template': 'homepage.html',
			'extra_context': {'form': EntryForm()}}, name='home'),
        url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
        url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),
        (r'^entry/$', 'snippet.views.test'),
        # Trick for Django to support static files (security hole: only for Dev environement! remove this on Prod!!!)$
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
