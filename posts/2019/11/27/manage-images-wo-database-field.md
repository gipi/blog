<!--
.. title: Attach images to a Django model without using database backed fields
.. slug: manage-images-wo-database-field
.. date: 2019-11-27 00:00:00
.. tags: django,programming,python
.. category: 
.. link: 
.. description: 
.. type: text
-->


In this post I want to create a model field that allows to manage derived images
from a pre-existing field in the same model without using the database to store
the path of the derived images but to derive it from a predefined convention.

<!-- TEASER_END -->

In particular let's suppose that we have a model with a field storing a
panoramic image and we want to create from that another set of images,
consisting of 6 images of the corresponding faces of the cubemap.

At first I will explain how in the python language, an attribute of
a class is returned and which possibilities are available to customize that,
after that I will explain how Django uses this functionality to create automagically
its fields and at the end I will create my custom pseudo-field with what
we have learnt.

**Note:** this post has been completely rewritten after I realized that I did
not understand at all how **descriptors** in python works.

## Descriptors (or the magic art of accessing attributes in Python)

Python is a language full of introspection functionalities; when you access an
attribute in python, the resolution algorithm searches in order

 1. class' ``__getattribute__``
 2. data descriptors in the class' ``__dict__``
 3. variables from the instance's ``__dict__``
 4. non data descriptors from the class' ``__dict__``
 5. variables from the class' ``__dict__``
 6. class' ``__getattr__``
 7. raise ``AttributeError``

(if you want to see a really good diagram, [look at this piece of art](https://blog.ionelmc.ro/2015/02/09/understanding-python-metaclasses/#object-attribute-lookup)).

But what are **data descriptors**? in practice an object that implements
the following protocol

 - ``__get__(self, obj, type=None)``
 - ``__set__(self, obj, value)``
 - ``__delete__(self, obj)``

if instead implements only the ``__get__`` method then is called a **non-data descriptor**.

When a descriptor is used to set a class' attribute, then when you access the attribute
(and the resolution algorithm doesn't find anything before that to return), the access is
resolved as ``desc.__get__(self, instance, type=None)``.

**Note:** descriptors are intended to be used with classes' attributes, if you set
an **instance**'s attribute to a descriptor, accessing that attribute will return the
descriptor, without "magic".

Before you think that you never used descriptors, you must know that for example
functions in python are non-data descriptors, and that the ``property`` decorator
[has the following signature](https://docs.python.org/3/library/functions.html#property)

```
class property(fget=None, fset=None, fdel=None, doc=None)
```
indeed if you define a class in the following way

```python
class Model(object):

    @property
    def miao(self):
        return 'miao'
```

you have the following behaviour

```python
>>> m1 = Model()
>>> m1.miao
'miao'
>>> m1.__dict__['miao']
---------------------------------------------------------------------------
KeyError                                  Traceback (most recent call last)
<ipython-input-14-ba1f034653b8> in <module>
----> 1 m1.__dict__['miao']

KeyError: 'miao'

>>> m1.__class__.__dict__['miao']
<property at 0x7fd805d81cb0>
>>> dir(m1.__class__.__dict__['miao'])
['__class__',
 ...
 '__get__',
 ...
 '__set__',
 ...
 'setter']
```

## Django's magic

Now let's talk about Django: when I get my first contact with this framework
I was amazed by the magic of describing the database using an object of the language
itself, i.e. a class and that the framework was able to automatically create all the necessary
to talk with the database and validate the data automagically.

All this is possible by the use of descriptors and metaclasses: we have just seen the
descriptors, and metaclasses are out of scope for this post but let me say that
a class, roughly speaking, is an instance of a metaclass in the same way an instance
of a class is obtained from a class: in particular ``__new__()`` is the analogous
of ``__init__()`` for a metaclass.

If we take a look at the code in ``django/db/models/base.py`` we can see that
when we create a class in Django, the framework calls the method ``contribute_to_class()``
for all the class' attributes that have it

```python
class ModelBase(type):
    """Metaclass for all models."""
    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = super().__new__
        ...
        contributable_attrs = {}
        for obj_name, obj in list(attrs.items()):
            if _has_contribute_to_class(obj):
                contributable_attrs[obj_name] = obj
            else:
                new_attrs[obj_name] = obj
        new_class = super_new(cls, name, bases, new_attrs, **kwargs)
        ...
        # Add remaining attributes (those with a contribute_to_class() method)
        # to the class.
        for obj_name, obj in contributable_attrs.items():
            new_class.add_to_class(obj_name, obj)
        ...

    def _has_contribute_to_class(value):
        # Only call contribute_to_class() if it's bound.
        return not inspect.isclass(value) and hasattr(value, 'contribute_to_class')

    def add_to_class(cls, name, value):
        if _has_contribute_to_class(value):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)
    ...
```

If this attributes are derived from ``Field`` (code at ``django/db/models/fields/__init__.py``)
you see that the instance of the attribute are wrapped around a (non data-)descriptor

```python
@total_ordering
class Field(RegisterLookupMixin):
    """Base class for all field types"""
    ...
    descriptor_class = DeferredAttribute
    ...
    def contribute_to_class(self, cls, name, private_only=False):
        """
        Register the field with the model class it belongs to.
        If private_only is True, create a separate instance of this field
        for every subclass of cls, even if cls is not an abstract model.
        """
        ...
        if self.column:
            # Don't override classmethods with the descriptor. This means that
            # if you have a classmethod and a field with the same name, then
            # such fields can't be deferred (we don't have a check for this).
            if not getattr(cls, self.attname, None):
                setattr(cls, self.attname, self.descriptor_class(self))
        ...
```

called ``DeferredAttribute`` that you can find at ``django/db/models/query_utils.py``

```python
class DeferredAttribute:
    """
    A wrapper for a deferred-loading field. When the value is read from this
    object the first time, the query is executed.
    """
    def __init__(self, field):
        self.field = field

    def __get__(self, instance, cls=None):
        """
        Retrieve and caches the value from the datastore on the first lookup.
        Return the cached value.
        """
        if instance is None:
            return self
        data = instance.__dict__
        field_name = self.field.attname
        if data.get(field_name, self) is self:
            # Let's see if the field is part of the parent chain. If so we
            # might be able to reuse the already loaded value. Refs #18343.
            val = self._check_parent_chain(instance)
            if val is None:
                instance.refresh_from_db(fields=[field_name])
                val = getattr(instance, field_name)
            data[field_name] = val
        return data[field_name]
    ...
```

You can see that the actual value of the field is retrieved from the instance's ``__dict__``
attribute if exists otherwise is refreshed from the database and saved there.

By the way this seems a nice trick in Django: if you have modified a field and you want to return
to the originary value, you can ``del`` the entry of the field from ``__dict__`` and the next
access to the attribute will return the value stored in the database (doesn't seem to work with ``id``
though).

There is only one more thing to explore: the ``FileField`` and ``ImageField``; these classes has
a custom descriptor (the code can be found at ``django/db/models/fields/files.py``)

```python
class FileField(Field):

    # The class to wrap instance attributes in. Accessing the file object off
    # the instance will always return an instance of attr_class.
    attr_class = FieldFile

    # The descriptor to use for accessing the attribute off of the class.
    descriptor_class = FileDescriptor
    ...
```

as you see it's using ``FileDescriptor`` and has one more class attribute
named ``attr_class``, that is set to ``FieldFile`` (to not be confused with the original ``FileField``!).

Indeed the descriptor uses the ``attr_class`` to wrap the value stored in the
``__dict__``'s instance

```python
class FileDescriptor:
    """
    The descriptor for the file attribute on the model instance. Return a
    FieldFile when accessed so you can write code like::
        >>> from myapp.models import MyModel
        >>> instance = MyModel.objects.get(pk=1)
        >>> instance.file.size
    Assign a file object on assignment so you can do::
        >>> with open('/path/to/hello.world') as f:
        ...     instance.file = File(f)
    """
    def __init__(self, field):
        self.field = field

    def __get__(self, instance, cls=None):
        if instance is None:
            return self

        # This is slightly complicated, so worth an explanation.
        # instance.file`needs to ultimately return some instance of `File`,
        # probably a subclass. Additionally, this returned object needs to have
        # the FieldFile API so that users can easily do things like
        # instance.file.path and have that delegated to the file storage engine.
        # Easy enough if we're strict about assignment in __set__, but if you
        # peek below you can see that we're not. So depending on the current
        # value of the field we have to dynamically construct some sort of
        # "thing" to return.

        # The instance dict contains whatever was originally assigned
        # in __set__.
        if self.field.name in instance.__dict__:
            file = instance.__dict__[self.field.name]
        else:
            instance.refresh_from_db(fields=[self.field.name])
            file = getattr(instance, self.field.name)

        # If this value is a string (instance.file = "path/to/file") or None
        # then we simply wrap it with the appropriate attribute class according
        # to the file field. [This is FieldFile for FileFields and
        # ImageFieldFile for ImageFields; it's also conceivable that user
        # subclasses might also want to subclass the attribute class]. This
        # object understands how to convert a path to a file, and also how to
        # handle None.
        if isinstance(file, str) or file is None:
            attr = self.field.attr_class(instance, self.field, file)
            instance.__dict__[self.field.name] = attr

        # Other types of files may be assigned as well, but they need to have
        # the FieldFile interface added to them. Thus, we wrap any other type of
        # File inside a FieldFile (well, the field's attr_class, which is
        # usually FieldFile).
        elif isinstance(file, File) and not isinstance(file, FieldFile):
            file_copy = self.field.attr_class(instance, self.field, file.name)
            file_copy.file = file
            file_copy._committed = False
            instance.__dict__[self.field.name] = file_copy

        # Finally, because of the (some would say boneheaded) way pickle works,
        # the underlying FieldFile might not actually itself have an associated
        # file. So we need to reset the details of the FieldFile in those cases.
        elif isinstance(file, FieldFile) and not hasattr(file, 'field'):
            file.instance = instance
            file.field = self.field
            file.storage = self.field.storage

        # Make sure that the instance is correct.
        elif isinstance(file, FieldFile) and instance is not file.instance:
            file.instance = instance

        # That was fun, wasn't it?
        return instance.__dict__[self.field.name]

    def __set__(self, instance, value):
        instance.__dict__[self.field.name] = value
```

Note how this is a real data descriptor, this means that has priority over the ``__dict__``
of the instance for retrieving the element (I think because otherwise couldn't wrap the object
with the proper ``attr_class`` instance).

## Let's create our field

The idea is to attach to the model a manager-like object (but avoiding the database part)
that in some way uses the information of a pre-existing ``ImageField`` to
resolve derived images. Note that here we don't need any setter since the paths
must derive from the pre-existing field.

The only thing you need to do is add a ``CubeImagesManager`` instance to a field in order
to attach six properties to the instances of the ``MyModel`` class

```python
class MyModel(models.Model):
    ...
    image = models.ImageField(upload_to='kebab')
    cubes = CubeImagesManager('image')
```

after that is possible to access the six images via the ``cubes`` attribute

```
>>> m = MyModel.objects.first()
>>> m.image
<ImageFieldFile: kebab/miao.txt>
>>> m.cubes
<cube_images.manager.CubeImages object at 0x7fcc008fd150>
>>> m.cubes.tile_f
<ImageFieldFile: kebab/miao_tile_f.jpeg>
>>> m.cubes.tile_u.path
'/tmp/tmp9xouh9d7/kebab/miao_tile_u.jpeg'
>>> m.cubes.tile_d.url
'/media/kebab/miao_tile_d.jpeg'
```

The steps to implement this field

 1. since we don't need the database we can derive the field from ``object``,
    instead of ``Field`` without worries
 2. we need to implement the ``contribute_to_class()`` method that set the appropriate
    descriptor
 3. the descriptor needs only the ``__get__()`` method implemented since we don't want
    anyone to set explicitely the value
 4. we want only a predefined number of attributes from what is returned from the manager;
    this can be done using ``__getattr__``
 5. we want to reuse the ``FieldImage`` wrapper class so to have the attributes of ``CubeImages``
    behave like ``ImageField`` instances.

We can do that with the following four classes (see the source [here](https://github.com/gipi/cube-images/blob/master/cube_images/manager.py))

```python
from django.core.files.storage import default_storage as django_default_storage
from django.db.models.fields.files import ImageFieldFile
from pathlib import Path


def get_upload_path_cube(base, filename):
    '''Builds the path of a cube image given the original filename and the final part.'''
    base = Path(base)
    components = list(base.parts)
    components[-1] = '%s_%s' % (base.stem, filename)

    return str(Path(*components))


class CubeImagesManager(object):
    '''Attach a field to the model that has the 6 faces of the cube.'''

    def __init__(self, field_name, files_extension='jpeg'):  # maybe ext in a settings
        self.field_name = field_name
        self.files_extension = files_extension

    def contribute_to_class(self, model, name):
        setattr(model, name, CubeImagesDescriptor(self.field_name, self.files_extension))


class CubeImagesDescriptor(object):

    def __init__(self, field_name, files_extension):
        self.files_extension = files_extension
        self.field_name = field_name

    def __get__(self, instance, value):
        field = getattr(instance, self.field_name)
        return CubeImages(
            instance,
            field,
            self.files_extension
        )


class CubeImages(object):

    def __init__(self, instance, field_image_instance, files_extension):
        self.instance = instance
        self.field_image_instance = field_image_instance
        self.files_extension = files_extension
        self.format = 'tile_%s'

        self.allowed_attributes = [
            self.format % _ for _ in ('f', 'b', 'l', 'r', 'u', 'd')
        ]

    def __getattr__(self, item):
        if item in self.allowed_attributes:
            complete_filename = "%s.%s" % (item, self.files_extension)  # THE EXTENSION IS FIXED?
            return ImageFieldFile(self.instance, self.field_image_instance, get_upload_path_cube(self.field_image_instance.name, complete_filename))

        raise AttributeError('You call this object with wrong attribute name \'%s\', allowed %s' %
                             (item, self.allowed_attributes))


class CubeImage(object):

    def __init__(self, path):
        self.path = path
        self.storage = django_default_storage

    def _storage_attr(self, attr, *args, **kwargs):
        fn = getattr(self.storage, attr)
        return fn(self.path, *args, **kwargs)

    def save(self, content, **kwargs):
        return self._storage_attr('save', content, **kwargs)

    @property
    def url(self):
        return self._storage_attr('url')
```

**Note:** the way the manager it's implemented has the side effect that each time
you access it, a new ``CubeImages`` instance is returned by ``__get__``.

If you want to experiment I create a little django application that contains
the code above, you can find it in [this github repo](https://github.com/gipi/cube-images).

## Links

 - [Data model](https://docs.python.org/3/reference/datamodel.html)
 - "Understanding Python metaclasses" post with a section about [object attribute lookup](https://blog.ionelmc.ro/2015/02/09/understanding-python-metaclasses/#object-attribute-lookup)
 - [Descriptor HowTo guide](https://docs.python.org/3/howto/descriptor.html)
 - [Python’s Object Model](http://www.aleax.it/Python/nylug05_om.pdf), slide by Alex Martelli
