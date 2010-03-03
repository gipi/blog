from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.contrib.comments.moderation import CommentModerator, moderator


from tagging.fields import TagField


# for trackback stuffs
from trackback import signals
from trackback.utils import handlers


class Blog(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=10,
        choices=(
            ('bozza', 'bozza'),
            ('pubblicato', 'pubblicato'),
        )
    )
    content = models.CharField(max_length=10000)
    creation_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now_add=True)
    tags = TagField(help_text='separe tags with commas')
    user = models.ForeignKey(User)
    # eventually this field could enable comments
    #enable_comments = models.BooleanField()
    trackback_content_field_name = 'content'

    def get_absolute_url(self):
        return reverse('blog-post', args=[self.slug])

    def save(self, *args, **kwargs):
        super(Blog, self).save(*args, **kwargs)
        if self.status == 'pubblicato': # or some other condition
            signals.send_pingback.send(sender=self.__class__, instance=self)
            signals.send_trackback.send(sender=self.__class__, instance=self)


class BlogCommentModeration(CommentModerator):
    email_notification = True
    #enable_field = 'enable_comments'

moderator.register(Blog, BlogCommentModeration)

admin.site.register(Blog)

signals.send_pingback.connect(handlers.send_pingback, sender=Blog)
signals.send_trackback.connect(handlers.send_trackback, sender=Blog)
