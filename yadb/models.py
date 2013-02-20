from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.contrib.comments.moderation import CommentModerator, moderator
from django.db.models import Q
from yadb.utils import slugify
# with this import all the ReST directive can be used
from . import rst_tex, rst_code, rst_video


from tagging.fields import TagField
from markitup_field.fields import MarkupField

# for trackback stuffs
from trackback import signals
from trackback.utils import handlers

class BlogAuthenticatedManager(models.Manager):
    def get_authenticated(self, user=None):
        real_Q = Q(status='pubblicato')

        if user.is_authenticated():
            real_Q = real_Q | ( Q(user=user) & Q(status='bozza') )

        return self.filter(real_Q)



class Blog(models.Model):
    class Meta:
        ordering = ['-creation_date']

    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=10,
        choices=(
            ('bozza', 'bozza'),
            ('pubblicato', 'pubblicato'),
        )
    )
    content = MarkupField(markup_format='restructuredtext', escape_html=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now_add=True)
    tags = TagField(help_text='separe tags with commas')
    user = models.ForeignKey(User)
    # eventually this field could enable comments
    enable_comments = models.BooleanField()
    trackback_content_field_name = '_content_rendered'

    objects = BlogAuthenticatedManager()

    def get_absolute_url(self):
        return reverse('blog-post', args=[self.slug])

    def save(self, *args, **kwargs):
        super(Blog, self).save(*args, **kwargs)
        if self.status == 'pubblicato': # or some other condition
            signals.send_pingback.send(sender=self.__class__, instance=self)
            signals.send_trackback.send(sender=self.__class__, instance=self)

class AdminBlog(admin.ModelAdmin):
    list_display = ('title', 'user', 'creation_date', 'modify_date')
    exclude = ('slug', 'user')

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        # TODO: maybe exists a Django function for slugify
        initial_slug = slugify(obj.title)

        # check for slug existence
        trailing = ''
        idx = 0
        try:
            while Blog.objects.get(slug=initial_slug + trailing):
                idx += 1
                trailing = '-%d' % idx
        except Blog.DoesNotExist:
            pass

        obj.slug = initial_slug + trailing

        obj.save()


class BlogCommentModeration(CommentModerator):
    email_notification = True
    enable_field = 'enable_comments'

moderator.register(Blog, BlogCommentModeration)

admin.site.register(Blog, AdminBlog)

signals.send_pingback.connect(handlers.send_pingback, sender=Blog)
signals.send_trackback.connect(handlers.send_trackback, sender=Blog)
