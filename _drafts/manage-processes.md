---
layout: post
comments: true
title: "Manage processes in a web application"
---

```
client <---> nginx <---> uwsgi <---> django/flask/kebab
                         |           |__ database
                         |__ celery
```

We want

1. a single point for controlling the status of the web application
1. the web application can have more than one process, not directly web related (celery anyone)
3. when the processes die must be restarted in correct order
4. possibility of controlling the main process
5. updating must not cause sudden kill of processes (a long running celery task should finish)

The problem is that we want to manually restart ``uwsgi`` since we are deploying untarring
the code into a new directory so that the original interpreter cannot possibly know that the
code is changed.

One way of do this is [supervisord](https://supervisord.readthedocs.org/en/latest/)

The entry point for the request at the web application is [uwsgi](https://uwsgi-docs.readthedocs.org/en/latest/)

The idea is that we follow the chain also for the managing part: ``uwsgi`` controls
the part after it and ``supervisor`` controls ``uwsgi``, in this way if some process
is added we don't have to touch with sysadmin power the installation

Could be possible to use stuffs like ``Procfile`` (inspired from heroku) to manage
multiple processes and in this case it will control ``uwsgi`` and the related processes.

## Problems

The socket used to communicate between ``nginx`` and ``uwsgi`` should be readable/writable
from each other but not by others (where by others we mean other ``uwsgi`` instances of others
project).

I think we want to avoid putting all the ``uwsgi`` instances in a group in common
since this will allow to communicate each other, the solution is to set the user
as the user of the webapp and as group, ```www-data`` or who belongs ``nginx``.

**NB:** take into account if ``uwsgi`` has the configuration file that can be
edited by deploying user
