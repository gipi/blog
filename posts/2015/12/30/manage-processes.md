<!--
.. title: Manage processes in a web application
.. slug: manage-processes
.. date: 2015-12-30 00:00:00
.. tags: sysadmin,deploy,webapp
.. category: 
.. link: 
.. description: 
.. type: text
-->

Suppose we have the following architecture for our web application:
a standard python web application (can be anything, Django, Flask or a
custom ``WSGI`` code) where ``nginx`` communicates with
it using an unix socket by the ``uwsgi`` protocol as indicated
in the diagram below

```
                      socket
browser <---> nginx <----------> uwsgi <---> django/flask/kebab
                                |           |__ database
                                |__ celery
```

This is a pretty standard way to deploy python web applications, but I haven't
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

Bad enough, not all of these points will be addressed in the first revision of this post.

## Security

<!--
In order to understand what's security, I need to define the so called **threat model**: i.e.
what my adversary is able to do; under my point of view also a developer can be

(I would like to discuss also the *most secure* file system permissions to set the application
with, but the inception is too deep).
-->

First of all, the channel of communication between ``nginx`` and ``uwsgi`` is an unix socket
(i.e. a particular type of file), this allows a more granular access control and is more
customizable (the alternative is to use an internet socket that can be only be customized as
port number, less human readable and not access controllable).

In order to be functional (i.e. the user requesting the page would actually see
the page) the socket should be readable/writable by the ``nginx`` process and
its own ``uwsgi`` process; since I'm interested in securing the socket from
unwanted *interaction*, I want it to be not readable from other possible
``uwsgi`` instances related to other projects (obviously a vulnerability in
``nginx`` could allow an attacker to access all of them but this is unavoidable
and I think less probable). Obviously I want to avoid access from random processes
as well.

This means that we have to create a separate user for each project and that the
socket must be ``chown``ed to ``www-data:user`` with permissions
``srw-rw----`` (i.e. ``660``).

The order of the owner seems weird but take into account that ``chmod(2)`` can
change permission only by who owns the file, or quoting the documentation:

> The effective UID of the calling process must match the owner of the file, or the process must be privileged

(i.e. the attacker could change the permissions' bits if owns the file)
so, at the end of the day, to avoid escalation we need to set the owner of the files of the web application
to not be the user of under which is running the web application.

Since the socket is created by the ``uwsgi`` instance and you cannot ``chown`` to a group you don't belong,
``uwsgi`` must be started as superuser and then it must *downgrade* its own capabilities (this is a standard
behaviour for daemon); in order to do so exist some flags

* ``--uid``: the user id of the running process
* ``--gid``: the group id of the running process
* ``--chmod-socket``: the permissions on the socket, ``660`` should be just fine (here we must use ``=`` just after to avoid strange errors)
* ``--chown-socket``: who owns the socket, like ``www-data:user``

I know that I missing a lot of stuffs in securing a web application, like
filesystem permission for the web root, but that will be argument of a future
post. Indeed if I want to make a configuration I need to determine
what secure means by the definition of a **threat model** for the web application,
i.e. what your adversary is capable of and from what you want to defend
(for example: your developers are a possible threat? should be them allowed
to change configuration files?).

In the following I assume that the developer can edit the ``uwsgi.ini`` configuration
file and he/she can add processes.

## Control

In my specific case, usually I deploy untarring the archive with the code in a new directory,
executing some operations (like database migrations, backup, etc...); the tricky thing is
to substitute the running processes in the way described in the list above.

The entry point for the request at the web application is [uwsgi](https://uwsgi-docs.readthedocs.org/en/latest/)
and the idea that I want to follow is that ``uwsgi`` controls
the part after it, in this way if some process
is added we don't have to touch with sysadmin power the installation,
i.e. we want the developer to be able to add processes using the ``uwsgi.ini``
configuration file.

Now I need a process supervisor for ``uwsgi``, that starts it and manages its
lifecycle. There are some choices available for process managers, like
[supervisord](https://supervisord.readthedocs.org/en/latest/), [upstart](http://upstart.ubuntu.com/)
and many others (read this [post](http://blog.crocodoc.com/post/48703468992/process-managers-the-good-the-bad-and-the-ugly)
about process managers for more informations).

Could be possible to use stuffs like ``Procfile`` (inspired from heroku) to manage
multiple processes, or another option could be using container-like technology ([Docker](https://docker.io) or [lxc](https://linuxcontainers.org/))
but in my opinion are a little bit immature technologies.

The choice is to use ``supervisord``, it will start the ``uwsgi`` process;
since ``supervisor`` need you to be a superuser in order to interat with,
I will configure ``sudo`` in order to allow execution of commands like

    $ sudo /usr/bin/supervisorctl restart uwsgi_example

By the way this kind of configuration with sudo can be used with
whatever process manager you want.

The tricky step is to configure correctly ``uwsgi`` to manage external
processes, generally the right way to do that is to avoid daemonizing them and
undertstand what signals kill/restart them; for example
[celery](https://celery.readthedocs.org/en/latest/) uses the ``TERM`` signal as
stated
[here](https://celery.readthedocs.org/en/latest/faq.html#how-can-i-safely-shut-down-the-worker)).

## Configuration

After all this, let see how to configure all the things: these are the parameters

* ``webuser`` is the ``UNIX`` user under which the web application run
* ``www-data`` is the identity of the web server
* ``/var/www/`` is the webroot
* ``/var/www/.virtualenv/`` is the virtualenv used

### Supervisor

```ini
[program:uwsgi_example]
command=/var/www/.virtualenv/bin/uwsgi
    --ini /var/www/app/uwsgi.ini
    --processes 1
    --need-app
    --uid webuser
    --gid webuser
    --chown-socket www-data:webuser
    --chmod-socket=660
redirect_stderr=true
stdout_logfile=/var/www/logs/uwsgi.log
stderr_logfile=/var/www/logs/uwsgi_error.log
autostart=true
autorestart=true
stopsignal=QUIT
```

Note that if we use ``--ini`` as the first option for the ``supervisor``'s ``uwsgi``
option, then any value will be overwritten by the flags passed (the main concern here
are the ``uid`` and ``gid`` flags); in this way the developer cannot override these values
from the ``uwsgi.ini`` file.

### Sudo

With the configuration below, the ``webuser`` can issue command to the ``uwsgi_example``
configuration of the ``supervisor`` daemon, without requiring a password

```
%webuser ALL = (root) NOPASSWD:/usr/bin/supervisorctl [a-z]\* uwsgi_example
```

### UWSGI

Finally the ``uwsgi.ini`` file can contain the following entries

```ini
[uwsgi]
module=.wsgi:application
chdir=/var/www/
socket=/tmp/uwsgi_example.sock
pidfile=/tmp/project-master_example.pid
vacuum=True
max-requests=5000
harakiri=30
stats=/tmp/stats_example.sock
# https://uwsgi-docs.readthedocs.org/en/latest/AttachingDaemons.html#examples
# smart-attach-daemon = /tmp/celery_example.pid .virtualenv/bin/celery -A app.tasks worker --pidfile=/tmp/celery_example.pid --loglevel=debug --logfile logs/celery.log
attach-daemon2 = stopsignal=15,reloadsignal=15,cmd=.virtualenv/bin/celery -A app.tasks worker --pidfile=/tmp/celery_example.pid --loglevel=debug --logfile logs/celery.log --concurrency=5
```

In my model this file is versioned together with the code; in this specific
example is enabled the control of a celery's worker. For more information
there is a [page](https://uwsgi-docs.readthedocs.org/en/latest/AttachingDaemons.html) in the celery's documentation.

## Testing

If seems to you that all of this is tricky to build you are right, but you are lucky: I prepared
a cookiecutter template for provisioning a web app project, with a script aimed to configure all the
necessary in order to test what I described here: simply do

    $ git clone https://github.com/gipi/cookiecutter-eep-provisioning.git
    $ cd cookiecutter-eep-provisioning
    $ ./tests/tests.sh

     now you are into the provisioning directory, you can use "sshme" to enter
     as the web application user.

     At the end remember to destroy the vagrant instance with "destroy_provision".

    [/tmp/tmp.PjjmjCkjtC/provision] $

In order to use the test script you need [vagrant](https://www.vagrantup.com/) and [ansible](https://docs.ansible.com/index.html).
All it's tested for a linux system so be aware the in other OSes
may be not working correctly.

For now it's all, let me know if all this seems reasonable to you.
