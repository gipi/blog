---
layout: post
comments: true
title: "Restore backup and move mail server"
tags: [sysadmin, postfix,backup]
---

We all know that backup are essential, but your backup procedure
is tested? I mean, you have ever tried to restore a service?

In this post I try to explain the procedure that I used to restore
and move my mail service to another server: it's a pretty basic setup,
consisting of ``postfix`` as service ``SMTP``, ``dovecot`` as ``IMAPS``
service and having as pool directory the path ``/var/mail/``.

The backup is done using ``rsnapshot`` via my [easy-backup](https://github.com/gipi/Easy-backup) package:
from the snapshot I created a ``tar`` archive with the configuration files for the
services of interest in the ``/etc`` directory and the mail pool.

## Restore

First of all install the necessary packages: to obtain the list of packages
installed with the actual version on the src server you can use

    $ /usr/bin/aptitude -q -F "%?p=%?V %M" --disable-columns search \~i

(this is already generated if you install my package ;)); now, depending
how different is the destination system, you have to
check if the versions that it finds make sense or a major version
change happened (like ``dovecot`` [in my
case](http://wiki2.dovecot.org/Upgrading/2.0)) and in such case google for
problems.

In any case, if something goes wrong you can ``apt-get remove --purge <packages>``
and restart from beginning.

After that you can copy the backuped data into the new machine: from
the machine where you have the backup, create an archive containing
all the needed

```
$ tar \
    -c \
    -C <root path of the backup> \
    etc/dovecot etc/postfix etc/aliases etc/aliases.db var/mail /home/gipi/mail/ \
    > archive-`date --iso`.tar
```

As double check, look at the configuration files and try to find some reference to files in
``/etc`` that can be needed (for example, in my case, some certificates). Also,
remember that is possible that the two systems can have the ``uid`` and ``gid``
of the corresponding users not equal causing permission issues ( I would like to
extend ``easy-backup`` to handle these cases).

Finally, compress the archive and unarchive to the final server

```
cat archive-2016-01-01.tar | gzip -9 | ssh dest tar -C / -xzv
etc/postfix/
etc/postfix/postfix-script
etc/postfix/main.cf
etc/postfix/sasl/
etc/postfix/master.cf
etc/postfix/virtual
etc/postfix/post-install
etc/postfix/postfix-files
etc/postfix/dynamicmaps.cf
etc/postfix/virtual.db
etc/dovecot/
etc/dovecot/dovecot-sql.conf
etc/dovecot/dovecot.conf
etc/dovecot/dovecot-ldap.conf
etc/dovecot/dovecot-db-example.conf
etc/dovecot/dovecot.conf.bak
etc/dovecot/dovecot-dict-sql-example.conf
etc/aliases
etc/aliases.db
var/mail/
var/mail/postgres
var/mail/gipi
```

This step can be time expensive (in my case the archive was like 80MB).

After all, restart the services and ``tail -f /var/log/syslog`` to watch
any problem that can arise.

## Test

After all the procedure we can test if the new installation is working correctly,
but since this want to be a test, without interrupting the normal mail server,
we can use [SWAKS](https://www.debian-administration.org/article/633/Testing_SMTP_servers_with_SWAKS)
and its option ``--server`` to direct the connections to the new server,
otherwise it looks for the ``MX`` DNS's entry of the recipient (i.e. the email address
indicated in the *to* field); in the following example I used as the
domain  ``yourdomain.com``

```
$ swaks \
    --server mail.yourdomain.com \
    --to user@yourdomain.com \
    --from test@example.com
```

Meanwhile you can look at the ``syslog`` on the server: in my case
the first time I've done this I forgot to add ``/etc/aliases.db``
into the backup and this below is what the server told me

```
Jan  3 12:30:13 miao postfix/smtpd[7337]: error: open database /etc/aliases.db: No such file or directory
```

Obviously, we care to have the ``TLS`` available, so we can test that also
with autentication

```
$ swaks \
    --server mail.yourdomain.com \
    -tls --tls-verify --tls-protocol tlsv1_2 \
    --auth plain \
    --from user@yourdomain.com \
    --to uptoyou@example.com
```

At this point you can also use some online tool to check you mail
server, like [starttls](https://starttls.info). It's also possible to
check for [blacklist](https://mxtoolbox.com/blacklists.aspx).

## Conclusion

If all it's ok, you are ready to switch your mail server:
my procedure was to add a [MX record](https://en.wikipedia.org/wiki/MX_record) with lower precedence
to the one pre-existing, but lowering the [time-to-live](https://en.wikipedia.org/wiki/Time_to_live)
of both the entries, so to have less time to wait in order to adjust the values. Once
the new entry was available I swapped the precedence so to have the new entry to be used
and not the old one.

At this point I tried the normal access with my email client so to assure the ``IMAP`` worked
and all the folders was there.

Finally, activated the backup for mail on the new server.

I advise you to try this, or in general, backup procedures, as probably you are not
aware exactly of what you need to restore a system: myself I missed for years
the backup of the mail folders in the home of my user.
