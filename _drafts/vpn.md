---
layout: post
comments: true
title: "Configuring a IpSec VPN (fortigate client)"
tags: [VPN, linux]
---

I was in need to have a working VPN with Fortigate and here I'm going to
recollect the procedure that has permited to accomplish such simple but
incredibly complex task.

My sistem is an Ubuntu 20.04, for example on an Ubuntu 18.10 this doesn't work
:) if someone knows why I would be glad to be informed.

## Dependencies

These are the packages that I installed

```
strongswan libstrongswan-standard-plugins libstrongswan resolvconf
```

## Configuration

To configure a connection having ``172.16.0.0/16`` as the "enterprise" part of
the tunnel, and as "local" part your home network (``192.168.1.0/24``) and using
as authentication an internal ``LDAP``, I used the following ``/etc/ipsec.conf``

```
# ipsec.conf - strongSwan IPsec configuration file

# basic configuration
# https://serverfault.com/questions/778487/connecting-to-a-fortigate-vpn-from-a-remote-linux-machine-via-openswan
# Introduction to IPsec: http://www.ipsec-howto.org/x202.html
config setup
   charondebug = "dmn 1, mgr 1, ike 2, chd 1, job 1, cfg 3, knl 2, net 2, lib 1"
   nat_traversal = yes

conn myvpn
	type = tunnel
	dpdaction = restart
	keyexchange = ikev1
	ike = aes128-sha1-modp1536
	esp = aes256-sha256-modp1536
	aggressive = yes
	right = vpn.kebab.it
	rightsubnet=172.16.0.0/16
	rightid = %any
	rightauth = psk

	left = %defaultroute
	leftsourceip = %config
	leftsubnet=%dynamic,192.168.1.0/24
	leftauth = psk
	leftauth2 = xauth
	xauth_identity = "ajeje.brazov"
	auto = route
```

You need also to indicate the ``PSK`` and the actual personal password in the
``/etc/ipsec.secrets``.


## Start tunnel

The command that I use to start it is

```
$ ipsec start --nofork
```

When just started you see the following

```
root@stakanov:~# ipsec statusall
Status of IKE charon daemon (strongSwan 5.8.2, Linux 5.4.0-26-generic, x86_64):
  uptime: 10 seconds, since Jun 11 08:55:01 2020
  malloc: sbrk 2424832, mmap 0, used 676864, free 1747968
  worker threads: 11 of 16 idle, 5/0/0/0 working, job queue: 0/0/0/0, scheduled: 0
  loaded plugins: charon aesni aes rc2 sha2 sha1 md5 mgf1 random nonce x509 revocation constraints pubkey pkcs1 pkcs7 pkcs8 pkcs12 pgp dnskey sshkey pem openssl fips-prf gmp agent xcbc hmac gcm drbg attr kernel-netlink resolve socket-default connmark farp stroke updown eap-identity eap-aka eap-md5 eap-gtc eap-mschapv2 eap-dynamic eap-radius eap-tls eap-ttls eap-peap eap-tnc xauth-generic xauth-eap xauth-pam tnc-tnccs dhcp lookip error-notify certexpire led addrblock unity counters
Listening IP addresses:
  192.168.1.40
Connections:
       myvpn:  %any...vpn.kebab.it  IKEv1 Aggressive, dpddelay=30s
       myvpn:   local:  uses pre-shared key authentication
       myvpn:   local:  uses XAuth authentication: any with XAuth identity 'gp'
       myvpn:   remote: uses pre-shared key authentication
       myvpn:   child:  dynamic 192.168.1.0/24 === 172.16.0.0/16 TUNNEL, dpdaction=restart
Routed Connections:
       myvpn{1}:  ROUTED, TUNNEL, reqid 1
       myvpn{1}:   192.168.1.0/24 === 172.16.0.0/16
Security Associations (0 up, 0 connecting):
  none
```

when the tunnel starts working you can instead see
(for some reason I need to ping an actual machine to trigger the tunnel
activation)

```
root@stakanov:~# ipsec statusall
Status of IKE charon daemon (strongSwan 5.8.2, Linux 5.4.0-26-generic, x86_64):
  uptime: 70 seconds, since Jun 11 08:55:00 2020
  malloc: sbrk 2965504, mmap 0, used 799552, free 2165952
  worker threads: 11 of 16 idle, 5/0/0/0 working, job queue: 0/0/0/0, scheduled: 5
  loaded plugins: charon aesni aes rc2 sha2 sha1 md5 mgf1 random nonce x509 revocation constraints pubkey pkcs1 pkcs7 pkcs8 pkcs12 pgp dnskey sshkey pem openssl fips-prf gmp agent xcbc hmac gcm drbg attr kernel-netlink resolve socket-default connmark farp stroke updown eap-identity eap-aka eap-md5 eap-gtc eap-mschapv2 eap-dynamic eap-radius eap-tls eap-ttls eap-peap eap-tnc xauth-generic xauth-eap xauth-pam tnc-tnccs dhcp lookip error-notify certexpire led addrblock unity counters
Listening IP addresses:
  192.168.1.40
Connections:
       myvpn:  %any...vpn.kebab.it  IKEv1 Aggressive, dpddelay=30s
       myvpn:   local:  [192.168.1.40] uses pre-shared key authentication
       myvpn:   local:  uses XAuth authentication: any with XAuth identity 'gp'
       myvpn:   remote: uses pre-shared key authentication
       myvpn:   child:  dynamic 192.168.1.0/24 === 172.16.0.0/16 TUNNEL, dpdaction=restart
Routed Connections:
       myvpn{1}:  ROUTED, TUNNEL, reqid 1
       myvpn{1}:   192.168.1.0/24 === 172.16.0.0/16
Security Associations (1 up, 0 connecting):
       myvpn[1]: ESTABLISHED 6 seconds ago, 192.168.1.40[192.168.1.40]...x.y.z.w[x.y.z.w]
       myvpn[1]: IKEv1 SPIs: c1587a4adf5fb482_i* a4511810194c7c64_r, pre-shared key+XAuth reauthentication in 2 hours
       myvpn[1]: IKE proposal: AES_CBC_128/HMAC_SHA1_96/PRF_HMAC_SHA1/MODP_1536
       myvpn{2}:  INSTALLED, TUNNEL, reqid 1, ESP in UDP SPIs: cddba753_i 4cdaab82_o
       myvpn{2}:  AES_CBC_256/HMAC_SHA2_256_128/MODP_1536, 2038 bytes_i (22 pkts, 2s ago), 1497 bytes_o (22 pkts, 2s ago), rekeying in 42 minutes
       myvpn{2}:   10.10.50.12/32 === 172.16.0.0/16
```

## Docker

It is possible to use this configuration via a ``Dockerfile`` reproducing the
steps above but take in mind that it is going to fail with some weird error like
``The expanding file pattern '/etc/strongswan.d/charon/*.conf' failed: Permission denied``; this is
caused by ``apparmor`` triggering: indeed if look at the log you will see
something like the following

```
audit: type=1400 audit(1592238171.739:83): apparmor="DENIED" operation="open" profile="/usr/lib/ipsec/charon" name="/var/lib/docker/overlay2/02767f1d398d73371577bf0894a350595be9cecaecdbb9f416b7f421ae7820eb/diff/etc/strongswan.d/charon/" pid=46257 comm="charon" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
audit: type=1400 audit(1592238171.739:84): apparmor="DENIED" operation="open" profile="/usr/lib/ipsec/charon" name="/var/lib/docker/overlay2/02767f1d398d73371577bf0894a350595be9cecaecdbb9f416b7f421ae7820eb/diff/etc/strongswan.d/" pid=46257 comm="charon" requested_mask="r" denied_mask="r" fsuid=0 ouid=0
```

the [solution](https://askubuntu.com/a/1250809/1095510) would be to do

```
$ sudo aa-complain /etc/apparmor.d/usr.lib.ipsec.charon
```

installing ``apparmor-utils``.

## Linkography

 - https://wiki.mikrotik.com/wiki/Manual:IP/IPsec
 - https://libreswan.org/man/ipsec.conf.5.html
 - https://manpages.debian.org/unstable/strongswan-starter/ipsec.conf.5.en.html
 - https://libreswan.org/wiki/images/e/e0/Netdev-0x12-ipsec-flow.pdf
