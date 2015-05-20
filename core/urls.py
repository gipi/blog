from django.conf.urls import patterns, include, url
from django.conf import settings
# TODO: use generic template view
from django.contrib import admin
from django.views.generic import RedirectView

admin.autodiscover()

from yadb.feeds import LatestBlogEntriesFeed, LatestBlogEntriesForUserFeed
from home import urls as home_urls

feeds = {
    'latest': LatestBlogEntriesFeed,
    'user': LatestBlogEntriesForUserFeed,
}

static_patterns = patterns('',
        (r'^favicon\.ico$', RedirectView.as_view(url=settings.MEDIA_URL + 'images/favicon.ico')),
        (r'^robots\.txt', RedirectView.as_view(
            url=settings.MEDIA_URL + 'robots.txt')),
)

urlpatterns = patterns('',
        (r'^', include(static_patterns)),
        (r'^', include(home_urls)),
        (r'^admin/', include(admin.site.urls)),
        url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
        url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),
        (r'^preview/$', 'yadb.views.preview'),
        (r'^blog/', include('yadb.urls')),
        # comment stuffs
        (r'^comments/', include('django_comments.urls')),
        #(r'^feeds/(?P<url>.*)/$',
        #    'django.contrib.syndication.views', {'feed_dict': feeds}),
        url(r'^markitup/', include('markitup_field.urls')),
        url(r'^adminfiles/', include('adminfiles.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
            # Trick for Django to support static files
            # (security hole: only for Dev environement!!!!)
            url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.MEDIA_ROOT}),
    )
