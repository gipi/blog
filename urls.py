from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
        (r'^entry/$', 'snippet.views.test'),
        # Trick for Django to support static files (security hole: only for Dev environement! remove this on Prod!!!)$
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
