from django.conf.urls import patterns, include, url

from .models import Blog
from .views import BlogDetailView, BlogListView, BlogArchiveView

urlpatterns = patterns('yadb.views',
                url(r'^$', BlogListView.as_view(), name='blog-list'),
                url(r'^add/$', 'blog_add', name='blog-add'),
                url(r'^edit/(\d*)/$', 'blog_add', name='blog-edit'),
                url(r'^post/(?P<slug>[\w\d-]*)/$', BlogDetailView.as_view(), name='blog-post'),
                url(r'^upload/$', 'upload', name='blog-upload'),
                url(r'^upload_popup/$', 'uploaded', name='blog-upload-popup'),
                url(r'^archives/$', BlogArchiveView.as_view(), name='blog-archives'),
                url(r'^categories/(?P<tags>.*)/$', 'blog_categories', name='categories'),
                #(r'pingback/', include('trackback.urls')),
)
