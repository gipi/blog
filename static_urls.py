from django.conf.urls.defaults import *
from django.conf import settings

from core.urls import static_patterns

urlpatterns = patterns('',
        (r'^', include(static_patterns)),
        # Trick for Django to support static files
        # (security hole: only for Dev environement!!!!)
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
)
