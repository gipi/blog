from django.conf.urls.defaults import *
from django.views.generic.date_based import archive_month
from django.views.generic.list_detail import object_list

from yadb.models import Blog

urlpatterns = patterns('yadb.views',
                url(r'^$', 'blog_list', name='blog-list'),
                url(r'^add/$', 'blog_add', name='blog-add'),
                url(r'^edit/(\d*)/$', 'blog_add', name='blog-edit'),
                url(r'^post/([\w\d-]*)/$', 'blog_view', name='blog-post'),
                url(r'^upload/$', 'upload', name='blog-upload'),
                url(r'^upload_popup/$', 'uploaded', name='blog-upload-popup'),
                url(r'^archives/$', 'blog_archives', name='blog-archives'),
)
