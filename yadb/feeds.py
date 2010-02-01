from django.contrib.syndication.feeds import Feed, FeedDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from snippet.models import Blog

class BlogFeed(Feed):
    title_template = 'yadb/feeds_title.html'
    description_template = 'yadb/feeds_description.html'

class LatestBlogEntriesFeed(BlogFeed):
    title = 'Latest blog post'
    link = '/blog/'
    description = 'Updates sui nuovi post'

    def items(self):
        return Blog.objects.\
                filter(status='pubblicato').\
                order_by('-creation_date')[:5]

class LatestBlogEntriesForUserFeed(BlogFeed):
    def get_object(self, bits):
        """
        This obtains the User istance, i.e. the obj argument
        used in the following method.
        """
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return User.objects.get(username__exact=bits[0])

    def title(self, obj):
        return 'Posts for user \'%s\'' % obj.username

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return 'The latest posts written by user \'%s\'' % obj.username

    def items(self, obj):
        return Blog.objects.\
                filter(user__id__exact=obj.id).\
                filter(status='pubblicato').\
                order_by('-creation_date')[:5]
