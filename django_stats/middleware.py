from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from django_stats.models import Stats, StatsSession

import re

class StatsMiddleware(object):
    def __init__(self):
        pass

    def process_request(self, request):
        # first of all test if the requested page is not in the blacklist
        for pattern in settings.STATS_BLACKLIST['path']:
            c = re.compile(pattern)
            if len(c.findall(request.path)) > 0:
                return None

        # second for USER AGENT (spiders&bots)
        # (check if it exists)
        if request.META.has_key('HTTP_USER_AGENT'):
            for pattern in settings.STATS_BLACKLIST['user agent']:
                c = re.compile(pattern)
                if len(c.findall(request.META['HTTP_USER_AGENT'])) > 0:
                    return None

        # first try to found a session_key otherwise create it
        try:
            sSession = StatsSession.objects.get(
                    session_key=request.session.session_key)
        except ObjectDoesNotExist:
            sSession = StatsSession.objects.create(
                    session_key=request.session.session_key)

        # then try to find if this page was already visited
        try:
            sPage = Stats.objects.get(page_path=request.path)
        except ObjectDoesNotExist:
            sPage = Stats.objects.create(page_path=request.path, counter=0)

        if not sSession in sPage.session_keys.all():
            sPage.session_keys.add(sSession)
            sPage.counter += 1
            sPage.save()

            if settings.DEBUG:
                print 'Update', request.path, 'stats'


        return None
