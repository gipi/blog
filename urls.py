from django.conf.urls.defaults import *
from django.conf import settings
# TODO: use generic template view
from django.views.generic.simple import redirect_to
from django.views.generic.base import TemplateView
from django.contrib import admin

admin.autodiscover()

from yadb.feeds import LatestBlogEntriesFeed, LatestBlogEntriesForUserFeed

feeds = {
    'latest': LatestBlogEntriesFeed,
    'user': LatestBlogEntriesForUserFeed,
}

static_patterns = patterns('',
        (r'^favicon\.ico$', redirect_to ,
            {'url': settings.MEDIA_URL + 'images/favicon.ico'}),
        (r'^robots\.txt', redirect_to,
            {'url': settings.MEDIA_URL + 'robots.txt'}),
)

urlpatterns = patterns('',
        (r'^', include(static_patterns)),
        (r'^admin/', include(admin.site.urls)),
        url(r'^$', TemplateView.as_view(template_name='home/index.html'), name='home'),
        url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
        url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),
        (r'^preview/$', 'yadb.views.preview'),
        (r'^blog/', include('yadb.urls')),
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
