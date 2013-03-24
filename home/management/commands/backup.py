from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings

import sys


try:
    getattr(settings, 'SITE_BACKUP_APPS')
except:
    print 'fatal: you to set \'SITE_BACKUP_APPS\' variable with a list of\
 application to dump'
    sys.exit(1)


# TODO: backup also the uploaded data
class Command(BaseCommand):
    help = "dump as fixture the data we need in order to backup the project"

    def handle(self, *args, **options):
        call_command('dumpdata', natural=True, *settings.SITE_BACKUP_APPS)
