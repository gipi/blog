---
layout: post
comments: true
title: "Configure a shared printer with CUPS"
---

I have an USB printer and I configured it to be used attached to a beaglebone

In the file ``/etc/cups/cupsd.conf`` of the *printer* machine

```
Listen 0.0.0.0:631

# Restrict access to the server...
<Location />
  Order allow,deny
  Allow 192.168.1.*
</Location>
```

and edit ``/etc/cups/client.conf`` of the machine from which you want to print

```
ServerName 192.168.1.7
Encryption IfRequested
```
