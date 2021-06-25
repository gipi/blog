<!--
.. title: Let's encrypt
.. slug: letsencrypt
.. date: 2016-01-16 00:00:00
.. tags: cryptography,sysadmin
.. category: 
.. link: 
.. description: 
.. type: text
-->


[Let's encrypt](https://letsencrypt.org) is the new thing in town: allows a seamless procedure
for obtaining ``TLS`` certificates; and it's free ;)

Roughly speaking, it's a certification authority, capable of generating certificates accepted from any major browser;
it has appositely created an ([open source](https://github.com/letsencrypt/letsencrypt)) client 
to do that *without human intervention*.

The protocol used by the client is [ACME](https://letsencrypt.github.io/acme-spec/)
(stands for *Automatic Certificate Management Environment*);

First of all, install the client (in the future will exist a maintained package)
in the server (all the operations must be done as root, I know, sucks)

    # git clone https://github.com/letsencrypt/letsencrypt && cd letsencrypt
    # ./letsencrypt-auto
    [... installing packages...]
    Creating virtual environment...
    Updating letsencrypt and virtual environment dependencies.......
    Running with virtualenv: /root/.local/share/letsencrypt/bin/letsencrypt
    No installers seem to be present and working on your system; fix that or try running letsencrypt with the "certonly" command

This creates in the ``$HOME/.local/share/letsencrypt`` a virtualenv with the client, ``letsencrypt-auto`` should
be a wrapper to the main executable named ``letsencrypt``, that checks everytime if updates are available.
If you want to use ``letsencrypt`` directly you have to activate the virtualenv.

There are several different ways to obtain a certificate and to deploy it,
I choose a manual method, since I usually I have nginx that is not officially supported.
If you have ``apache`` all should be completely automated. Exist also other methods,
if you want to improve your knowledge, read the [documentation](https://letsencrypt.readthedocs.org/en/latest/).

From [this post](https://community.letsencrypt.org/t/using-the-webroot-domain-verification-method/1445/7) I stole
the configuration for ``nginx`` (to place in ``/etc/nginx/snippets/letsencryptauth.conf``)

```nginx
location /.well-known/acme-challenge {
    alias /etc/letsencrypt/webrootauth/.well-known/acme-challenge;
    location ~ /.well-known/acme-challenge/(.*) {
        add_header Content-Type application/jose+json;
    }
}
```

then in the ``server`` block
serving the domain for which you want to issue the certificate you can include this snippet

```nginx
server {

        # the include must be placed before any location directive
        include snippets/letsencryptauth.conf;

        # other location directives
}
```

Finally we have to create the authentication directory

    # mkdir /etc/letsencrypt/webrootauth

and execute the last step

    # ./letsencrypt-auto  \
        --webroot-path /etc/letsencrypt/webrootauth \
        --domain yourdomain.com  \
        -a webroot certonly
    [... wait a little bit ...]
    IMPORTANT NOTES:
     - Congratulations! Your certificate and chain have been saved at
       /etc/letsencrypt/live/yourdomain.com/fullchain.pem. Your cert will expire
       on 2016-03-03. To obtain a new version of the certificate in the
       future, simply run Let's Encrypt again.
     - If like Let's Encrypt, please consider supporting our work by:

       Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
       Donating to EFF:                    https://eff.org/donate-le

Remember that the certificate generated will expire after just three months.

## Security

All is working but someone has (rightly) rised some concerns about security since
all the scripts are autoupdating and running as root. An alternative way is to [install and run it
 using docker](https://letsencrypt.readthedocs.org/en/latest/using.html#running-with-docker)
with the following steps: first of all, pull the image

    $ docker pull quay.io/letsencrypt/letsencrypt:latest

and then run it, mounting the path used to store configuration and certificates by letsencrypt

    $ docker run \
        -v "/etc/letsencrypt:/etc/letsencrypt" \
        -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
        --entrypoint=/bin/bash \
        -it quay.io/letsencrypt/letsencrypt
    root@d24cd7b4b487:/opt/letsencrypt#

I warn you that [docker](https://docker.io) works only on 64bit machines.