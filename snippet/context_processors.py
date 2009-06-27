from django.conf import settings

def version(request):
	return {'version': settings.SNIPPY_GIT_VERSION}
