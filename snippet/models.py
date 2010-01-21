from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from tagging.fields import TagField

class Blog(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=100)
    status = models.CharField(max_length=10,
        choices=(
            ('bozza', 'bozza'),
            ('pubblicato', 'pubblicato'),
        )
    )
    content = models.CharField(max_length=1000)
    creation_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now_add=True)
    tags = TagField(help_text='separe tags with commas')
    user = models.ForeignKey(User)

    def get_absolute_url(self):
        return reverse('blog-post', args=[self.pk])
