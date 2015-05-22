from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.core.urlresolvers import reverse
from django_comments.moderation import CommentModerator, moderator
from django.db.models import Q
from yadb.utils import slugify
# with this import all the ReST directive can be used
from . import rst_tex, rst_code, rst_video
from adminfiles.admin import FilePickerAdmin


from tagging.fields import TagField
from markitup_field.fields import MarkupField

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

    objects = BlogAuthenticatedManager()

    def get_absolute_url(self):
        return reverse('blog-post', args=[self.slug])

class AdminBlog(FilePickerAdmin):
    list_display = ('title', 'user', 'status', 'creation_date', 'modify_date')
    exclude = ('slug', 'user')
    adminfiles_fields = (
        'content',
    )

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