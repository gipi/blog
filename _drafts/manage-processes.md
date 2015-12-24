---
layout: post
comments: true
title: "Manage processes in a web application"
---
Suppose we have the following architecture for our web application:
a standard python web application where ``nginx`` communicate with
it using an unix socket by the ``uwsgi`` protocol as indicated
in the diagram below

```
                      socket
client <---> nginx <----------> uwsgi <---> django/flask/kebab
                                |           |__ database
                                |__ celery
```

This is a pretty standard way to deploy python web application, but I haven't
found any complete description on how manage this configuration.

I want

* Security
 0. each web application must be isolated from any other service on the server
 0. obviously the code must run with the minimal permissions possible
 0. the developer don't have to be a system administrator, must have the same permission
    of the running web application
* Control
 0. a single point for controlling the status of the web application
 0. the web application can have more than one process, not directly web related (celery anyone)
 0. the developer can add processes
 0. when the processes die must be restarted in correct order
 0. updating must not cause sudden kill of processes (a long running celery task should finish)
 0. restarting on updating must be explicit
 0. the service must restart automagically at reboot

## Security

In order to understand what's security, I need to define the so called **threat model**: i.e.
what my adversary is able to do; under my point of view also a developer can be
(I would like to discuss also the *most secure* file system permissions to set the application
with, but the inception is too deep).

First of all, the channel of communication between ``nginx`` and ``uwsgi`` is an unix socket
(i.e. a particular type of file), this allows a more granular access control and is more
customizable (the alternative is to use an internet socket that can be only be customized as
port number, less human readable and not access controllable).

So a socket should be readable/writable by the ``nginx`` process and its own ``uwsgi`` process
but not by others ``uwsgi`` instances of others projects; this means that we have to create an
user of each project and that the socket must be ``chown``ed to ``www-data:user`` with permissions
``srw-rw----`` (i.e. ``660``).

Since the socket is created by the ``uwsgi`` instance and you cannot ``chown`` to a group you don't belong,
``uwsgi`` must be started with some flags set in order the permissions appropriately

* ``--uid``: the user id of the running process
* ``--gid``: the group id of the running process
* ``--chmod-socket``: the permissions on the socket, ``660`` should be just fine (here we must use ``=`` just after to avoid strange errors)
* ``--chown-socket``: who owns the socket, like ``www-data:user``

The order of the owner seems weird but take into account that ``chmod(2)`` can change permission only by who owns the file,
or quoting the documentation:

> The effective UID of the calling process must match the owner of the file, or the process must be privileged

so, at the end of the day, to avoid escalation we need to set the owner of the files of the web application
to not be the user of under which is running the web application.

Note that if we use ``--ini`` as the first option for the ``supervisor``'s ``uwsgi``
option, then any value will be overwritten by the flags passed (the main concern here
are the ``uid`` and ``gid`` flags).

**NB:** take into account if ``uwsgi`` has the configuration file that can be
edited by deploying user; you have to define a precise **threat model**

## Control

In my specific case, usually I deploy untarring the archive with the code in a new directory,
executing some operations (like database migrations, backup, etc...); the tricky thing is
to substitute the running processes in the way described in the list above.

The entry point for the request at the web application is [uwsgi](https://uwsgi-docs.readthedocs.org/en/latest/)

The idea is that we follow the chain also for the managing part: ``uwsgi`` controls
the part after it and ``supervisor`` controls ``uwsgi``, in this way if some process
is added we don't have to touch with sysadmin power the installation.

What I need is a process supervisor, that starts all the needed processes as child
and manages their lifecycle. There are some choices available

* [supervisord](https://supervisord.readthedocs.org/en/latest/)
* Could be possible to use stuffs like ``Procfile`` (inspired from heroku) to manage
multiple processes and in this case it will control ``uwsgi`` and the related processes.
* Another option could be using container-like technology ([Docker](https://docker.io) or [lxc](https://linuxcontainers.org/))

## Configuration

After all this

### Daemon

It's possible to use a following line in ``uwsgi.ini`` for manage a ``celery`` instance

```
smart-attach-daemon = /tmp/celery_example.pid .virtualenv/bin/celery -A app.tasks worker --pidfile=/tmp/celery_example.pid --loglevel=debug --logfile logs/celery.log
```

the only problem with this is that celery it's not killed and restarted with the master ``uwsgi``,
we should use the ``--attach-daemon2`` [flag](https://uwsgi-docs.readthedocs.org/en/latest/AttachingDaemons.html#attach-daemon2)

```ini
[uwsgi]
attach-daemon2 = cmd=my_daemon.sh,pidfile=/tmp/my.pid,uid=33,gid=33,stopsignal=3
```

Each possible accessory process have their own ratio for the stopping (for example
``celery`` use the ``TERM`` signal as stated [here](https://celery.readthedocs.org/en/latest/faq.html#how-can-i-safely-shut-down-the-worker)).
