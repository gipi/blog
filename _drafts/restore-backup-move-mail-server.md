---
layout: post
comments: true
title: "Restore backup and move mail server"
---

We all know that backup are essential, but your backup procedure
is tested? I mean, you have ever tried to restore a service?

## Restore

First of all install all the necessary packages: to obtain the list of packages
installed with the version you can use

    $ /usr/bin/aptitude -q -F "%?p=%?V %M" --disable-columns search \~i

check if the versions that your system finds make sense or a major version
change happened (like ``dovecot`` [in my
case](http://wiki2.dovecot.org/Upgrading/2.0)) and in such case google for
problems.

After that you can copy the backuped data into the new machine: from
the machine where you have the backup, create an archive containing
all the needed

```
$ tar \
    -C <root path of the backup> \
    -c \
    etc/dovecot etc/postfix etc/aliases etc/aliases.db var/mail
```

As double check, look at the configuration files and try to find some file in ``/etc`` that
can be needed (for example certificates). Also, remember if you need to create some user.

If something goes wrong you can ``apt-get remove --purge <packages>``.

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
