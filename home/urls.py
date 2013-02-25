from django.conf.urls.defaults import patterns, url
from django.views.generic.base import TemplateView
from django.conf import settings

import os

try:
    GOOGLE_VERIFICATION_PAGE = settings.GOOGLE_VERIFICATION_PAGE
except:
    GOOGLE_VERIFICATION_PAGE = 'google-no-party.html'

urlpatterns = patterns('',
    url(
        r'^%s' % GOOGLE_VERIFICATION_PAGE,
        'django.views.static.serve',
        {
            'document_root': os.path.dirname(__file__),
            'path': GOOGLE_VERIFICATION_PAGE,
        }
    ),
    url(r'^$', TemplateView.as_view(template_name='home/index.html'), name='home'),
)
