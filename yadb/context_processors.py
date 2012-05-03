from django.conf import settings

def analytics(request):
    analytics_id = getattr(settings, 'GOOGLE_ANALYTICS_ID', None)

    return { 'google_analytics_id': analytics_id }

def version(request):
	return {'version': settings.SNIPPY_GIT_VERSION}
