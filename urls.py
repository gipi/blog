from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import redirect_to
from django.contrib import admin

admin.autodiscover()

from snippet.feeds import LatestBlogEntriesFeed, LatestBlogEntriesForUserFeed

feeds = {
    'latest': LatestBlogEntriesFeed,
    'user': LatestBlogEntriesForUserFeed,
}

urlpatterns = patterns('',
        (r'^favicon\.ico$', redirect_to ,
            {'url': settings.MEDIA_URL + 'images/favicon.ico'}),
        (r'^robots\.txt', redirect_to,
            {'url': settings.MEDIA_URL + 'robots.txt'}),
        (r'^admin/(.*)', admin.site.root),
        url(r'^$', redirect_to, {'url': '/blog/'}, name='home'),
        url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
        url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),
        (r'^preview/$', 'snippet.views.preview'),
        (r'^blog/', include('snippet.urls')),
        # comment stuffs
        (r'^comments/', include('django.contrib.comments.urls')),
        (r'^feeds/(?P<url>.*)/$',
            'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
)

if settings.DEBUG:
    urlpatterns += patterns('',
            # Trick for Django to support static files
            # (security hole: only for Dev environement!!!!)
            url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.MEDIA_ROOT}),
    )
