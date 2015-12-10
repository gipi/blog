---
layout: post
comments: true
title: "Manage processes in a web application"
---

```
client <---> nginx <---> uwsgi <---> django/flask/kebab
                                     |__ database
                                     |__ celery
```

We want

1. a single point for controlling the status of the web application
1. the web application can have more than one process, not directly web related (celery anyone)
3. when the processes die must be restarted in correct order
4. possibility of controlling the main process

The problem is that we want to manually restart ``uwsgi`` since we are deploying untarring
the code into a new directory so that the original interpreter cannot possibly know that the
code is changed.

One way of do this is [supervisord](https://supervisord.readthedocs.org/en/latest/)

The entry point for the request at the web application is [uwsgi](https://uwsgi-docs.readthedocs.org/en/latest/)

The idea is that we follow the chain also for the managing part: ``uwsgi`` controls
the part after it and ``supervisor`` controls ``uwsgi``, in this way if some process
is added we don't have to touch with sysadmin power the installation

**NB:** take into account if ``uwsgi`` has the configuration file that can be
edited by deploying user
