from django.contrib.syndication.feeds import Feed

from snippet.models import Blog

class BlogFeed(Feed):
    title_template = 'snippet/feeds_title.html'
    description_template = 'snippet/feeds_description.html'

class LatestBlogEntriesFeed(BlogFeed):
    title = 'Latest blog post'
    link = '/blog/'
    description = 'Updates sui nuovi post'

    def items(self):
        return Blog.objects.order_by('-creation_date')[:5]
