---
layout: post
comments: true
title: "Restore backup and move mail server"
---

We all know that backup are essential, but your backup procedure
is tested? I mean, you have ever tried to restore a service?

In this post I try to explain the procedure that I used to restore
and move my mail service to another server: it's a pretty basic setup,
consisting of ``postfix`` as service ``SMTP``, ``dovecot`` as ``IMAPS``
service and having as pool directory the path ``/var/mail/``.

The backup is done using ``rsnapshot`` via my [easy-backup](https://github.com/gipi/Easy-backup) package:
I create a ``tar`` archive with the configuration file in the ``/etc``
directory and the mail pool.

## Restore

First of all install all the necessary packages: to obtain the list of packages
installed with the actual version on the src server you can use

    $ /usr/bin/aptitude -q -F "%?p=%?V %M" --disable-columns search \~i

check if the versions that your system finds make sense or a major version
change happened (like ``dovecot`` [in my
case](http://wiki2.dovecot.org/Upgrading/2.0)) and in such case google for
problems.

If something goes wrong you can ``apt-get remove --purge <packages>``.

After that you can copy the backuped data into the new machine: from
the machine where you have the backup, create an archive containing
all the needed

```
$ tar \
    -C <root path of the backup> \
    -c \
    etc/dovecot etc/postfix etc/aliases etc/aliases.db var/mail /home/gipi/mail/
```

As double check, look at the configuration files and try to find some file in
``/etc`` that can be needed (for example, in my case, some certificates). Also,
remember that is possible that the two system can have the ``uid`` and ``gid``
of the corresponding users not equal causing permission issues.

## Test

After all the procedure we can test if the new installation is working correctly,
but since this want to be a test, without interrupting the normal mail server,
we can use [SWAKS](https://www.debian-administration.org/article/633/Testing_SMTP_servers_with_SWAKS)

```
$ swaks --server ohr.lol --to gp@ktln2.org --from test@example.com
```

Meanwhile you can look at the ``syslog`` on the server: in my case
the first time I've done this I forgot to add ``/etc/aliases.db``
into the backup and this below is what the server told me

```
Jan  3 12:30:13 miao postfix/smtpd[7337]: error: open database /etc/aliases.db: No such file or directory
```

Finally, activated the backup for mail on the new server.
