---
layout: post
comments: true
title: "Add unitests to a Django application"
tags: [python,django,unit tests]
---

Suppose you have written a Django app and obviously you want to [test
it]({% post_url 2012-12-19-the-amazing-world-of-python-testing %}).

This is an example, inspired from other projects like [dj-stripe](https://github.com/pydanny/dj-stripe/blob/master/runtests.py)
or [cookiecutter-djangopackage](https://github.com/pydanny/cookiecutter-djangopackage/blob/master/%7B%7Bcookiecutter.repo_name%7D%7D/runtests.py)

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
    management.execute_from_command_line(['', 'test', APP_NAME,])
    sys.exit()

if __name__ == '__main__':
    main()

```
