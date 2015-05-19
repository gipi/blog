from django.conf.urls import patterns, include, url
from django.views.generic.list_detail import object_detail

from yadb.models import Blog

urlpatterns = patterns('yadb.views',
                url(r'^$', 'blog_list', name='blog-list'),
                url(r'^add/$', 'blog_add', name='blog-add'),
                url(r'^edit/(\d*)/$', 'blog_add', name='blog-edit'),
                url(r'^post/(?P<slug>[\w\d-]*)/$', object_detail, {
                    'queryset': Blog.objects,
                    'slug_field': 'slug',
                    'template_name': 'yadb/blog.html',
                    'template_object_name': 'blog',
                    }, name='blog-post'),
                url(r'^upload/$', 'upload', name='blog-upload'),
                url(r'^upload_popup/$', 'uploaded', name='blog-upload-popup'),
                url(r'^archives/$', 'blog_archives', name='blog-archives'),
                url(r'^categories/(?P<tags>.*)/$', 'blog_categories', name='categories'),
                (r'pingback/', include('trackback.urls')),
)
