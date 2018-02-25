---
layout: post
comments: true
title: "Attach images to a Django model without using database backed fields"
tags: [Django, python, imagekit, wip]
---

Let's start with a model that has a field where an image will be uploaded;
this image will be manipulated with some library (for example pillow) in order
to obtain, for example, a thumbnail: the first example I'm going to show is using
[imagekit](https://django-imagekit.readthedocs.org/en/latest/)

```python
from django.db import models

from imagekit.models import ImageSpecField


class MyModel(models.Model):
    image = models.ImageField(
        upload_to='uploads', null=False, blank=False)
    image_thumb = ImageSpecField(source='image', id='my_app:viewdraft:imagethumb')
```

The core of this methodology is the ``imagegenerators.py`` file that has to be placed
along the application code and will be loaded automatically by ``imagekit`` when
it's initializated

```python
'''
Automatically loaded from ImageKit.
'''
import os

from imagekit import ImageSpec, register
from imagekit.utils import get_field_info
from pilkit.processors import ResizeToFill


class ImageThumb(ImageSpec):
    '''
    This Spec creates a thumb image using THUMBNAIL_CUBE_SIDE settings
    and saving it alongside the original image.
    '''
    format = 'JPEG'

    @property
    def cachefile_name(self):
        model, field_name = get_field_info(self.source)

        field = getattr(model, field_name)

        dirname = os.path.dirname(field.name)
        filename = '%s_thumb.jpg' % os.path.basename(field.name).split('.')[0]

        return os.path.join(dirname, filename)

    @property
    def processors(self):
        from django.conf import settings
        return [ResizeToFill(settings.THUMBNAIL_CUBE_SIDE * 2, settings.THUMBNAIL_CUBE_SIDE * 4)]

register.generator('my_app:viewdraft:imagethumb', ImageThumb)
```

## Descriptors

Now it's easy-peasy, but suppose now that we want to create for each image another set of images
generated from that, for example from a panoramic image we would like to generate the cubemap
consisting of 6 images of the corresponding faces.

The idea is to attach to the model a manager-like object (like the [Manager](https://docs.djangoproject.com/en/1.8/topics/db/managers/)
associated with any Django's model). The code following is an example of a pattern used for example
also for the FileField, ImageField, i.e. implements a custom ``contribute_to_class()`` method in the field
that ``setattr()`` a descriptor to the instance.

We can do that with the following three classes

```python
from django.core.files.storage import default_storage

class CubeImagesManager(object):
    '''
    Attach a field to the model that has the 6 faces of the cube
    (plus the correspondendant thumb).
    '''
    def __init__(self, files_extension='jpeg'): # maybe ext in a settings
        # TODO: check exists the %s formatter and only that
        self.vd_instance = None
        self.files_extension = files_extension

    def contribute_to_class(self, model, name):
        self.vd_instance = model
        setattr(model, name, CubeImages(model, self.files_extension))


class CubeImages(object):
    def __init__(self, model, files_extension):
        self.files_extension = files_extension
        self.instance = None
        self.format = 'tile_%s'
        self.format_thumb = 'tile_%s_thumb'

        self.allowed_attributes = [
            self.format % _ for _ in ('f', 'b', 'l', 'r', 'u', 'd')] +
            [self.format_thumb % _ for _ in ('f', 'b', 'l', 'r', 'u', 'd')]

    def __get__(self, instance, value):
        '''
        WORKAROUND:
        by using this we set the instance of the model that is calling the object
        '''
        self.instance = instance
        return self

    def __getattr__(self, item):
        if item in self.allowed_attributes:
            complete_filename = "%s.%s" % (item, self.files_extension) # THE EXTENSION IS FIXED?
            return CubeImageDescriptor(get_upload_path_cube(self.instance, complete_filename))

        raise AttributeError('You call this object with wrong attribute name \'%s\', allowed %s' %
                             (item, self.allowed_attributes))


class CubeImageDescriptor(object):
    '''Wrap the path to the storage to return the correct instance from the path'''
    def __init__(self, path):
        self.path = path
        self.storage = default_storage

    def _storage_attr(self, attr, *args, **kwargs):
        fn = getattr(self.storage, attr)
        return fn(self.path, *args, **kwargs)

    def save(self, content, **kwargs):
        return self._storage_attr('save', content, **kwargs)

    @property
    def url(self):
        return self._storage_attr('url')
```

The only thing you need to do is add a ``CubeManager`` instance to a field in order
to attach six properties to the instances of the ``MyModel`` class

```python
class MyModel(models.Model):
    ...
    cubes = CubeManager()
```

but bad enough I haven't had time for complete this post, in future I will return to complete it.
