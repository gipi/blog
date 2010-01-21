from django.conf.urls.defaults import *
from django.views.generic.date_based import archive_month

from snippet.models import Blog

urlpatterns = patterns('',
                url(r'^$', 'snippet.views.blog_list', name='blog-list'),
                url(r'^add/$', 'snippet.views.blog_add', name='blog-add'),
                url(r'^edit/(\d*)/$',
                    'snippet.views.blog_add', name='blog-edit'),
                url(r'^post/([\w\d-]*)/$',
                        'snippet.views.blog_view', name='blog-post'),
                url(r'^archives/(?P<year>\d{4})/(?P<month>.*)/$',
                    archive_month, {
                        'queryset': Blog.objects.all().\
                                filter(status='pubblicato'),
                        'date_field': 'creation_date'
                    }, name='blog-archives'),
)
