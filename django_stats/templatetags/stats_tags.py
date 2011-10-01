from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from django_stats.models import Stats

register = template.Library()

def page_counter(page_path):
    if settings.DEBUG:
        print page_path

    #return ''

    try:
        stats = Stats.objects.get(page_path=page_path)
        counter = stats.counter
    except ObjectDoesNotExist:
        counter = 0

    return '%d' % counter

register.simple_tag(page_counter)
