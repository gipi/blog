from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.contrib.comments.moderation import CommentModerator, moderator


from tagging.fields import TagField

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

    def get_absolute_url(self):
        return reverse('blog-post', args=[self.slug])

class BlogCommentModeration(CommentModerator):
    email_notification = True
    #enable_field = 'enable_comments'

moderator.register(Blog, BlogCommentModeration)
admin.site.register(Blog)
