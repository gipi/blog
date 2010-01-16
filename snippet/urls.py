from django.conf.urls.defaults import *

urlpatterns = patterns('',
                url(r'^$', 'snippet.views.blog_list', name='blog-list'),
                url(r'^add/$', 'snippet.views.blog_add', name='blog-add'),
                url(r'^edit/(\d*)/$',
                    'snippet.views.blog_add', name='blog-edit'),
                url(r'^post/([\w\d-]*)/$',
                        'snippet.views.blog_view', name='blog-post'),
)
