<!--
.. title: Add unitests to a Django application
.. slug: create-django-app-w-unittest-included
.. date: 2016-10-30 00:00:00
.. tags: python,django,unit tests
.. category: 
.. link: 
.. description: 
.. type: text
-->


Suppose you have written a Django app and obviously you want to [test
it](link://slug/the-amazing-world-of-python-testing), the
filesystem structure is something like the following:

```
.
├── my_django_app
│   ├── __init__.py
│   ├── models.py
│   ├── tests.py
└── runtests.py
```

where ``models.py`` contains something like this

```python
from django.db import models

class A(models.Model):
    name = models.CharField(max_length=100)
```

and with very simple test module ``tests.py``:

```python
from django.test import TestCase
from .models import A


class Test(TestCase):
    def setUp(self):
        self.a = A(name='kebab')
        self.a.save()

    def test_model(self):
        self.assertEqual(self.a.name, 'kebab')
```

The magic happens with ``runtests.py`` that sets all the necessary
in order to run all the tests:

```python
from __future__ import absolute_import

import sys

from django.conf import settings
from django.core import management

APP_NAME = 'my_django_app'


def main():
    settings.configure(
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        INSTALLED_APPS = ( # These apps depend on what your app need
            'django.contrib.auth',
            'django.contrib.contenttypes',
            APP_NAME,
        ),
        TEMPLATE_CONTEXT_PROCESSORS = (
            'django.contrib.auth.context_processors.auth',
            'django.core.context_processors.debug',
            'django.core.context_processors.i18n',
            'django.core.context_processors.media',
            'django.core.context_processors.request',
            'django.core.context_processors.static',
            'django.core.context_processors.tz',
            'django.contrib.messages.context_processors.messages'
        ),
        ROOT_URLCONF = '%s.tests.urls' % APP_NAME,
        STATIC_URL = '/static/',
    )

    import django
    django.setup()
    management.execute_from_command_line(['', 'test', APP_NAME,])
    sys.exit()

if __name__ == '__main__':
    main()

```

Now you can launch the test without a complete Django project with
a simple

    $ python runtests.py
    Creating test database for alias 'default'...
    .
    ----------------------------------------------------------------------
    Ran 1 test in 0.001s

    OK
    Destroying test database for alias 'default'...

This is only an example, inspired from other projects like [dj-stripe](https://github.com/pydanny/dj-stripe/blob/master/runtests.py).
If you want really to wrote a Django app use
[cookiecutter-djangopackage](https://github.com/pydanny/cookiecutter-djangopackage/blob/master/%7B%7Bcookiecutter.repo_name%7D%7D/runtests.py)
that includes an updated version of this configuration and much more.