---
layout: post
comments: true
title: "Add unitests to a Django application"
---

```python
from __future__ import absolute_import

import sys

from django.conf import settings
from django.core import management

APP_NAME = 'longerusernameandemail'


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
