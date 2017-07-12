---
layout: post
comments: true
title: "Create root filesystems for embedded systems"
tags: [embedded, Debian, Linux, multistrap, QEMU]
---

All is started from this [link](https://blahcat.github.io/2017/06/25/qemu-images-to-play-with/) where
a good boy shared some images in order to start to put hands on esotic architectures.

The bad thing in my opinion is that he doesn't explain how they have been generated,
just in case someone need to customize something; in this post I want to show how to create root filesystems for all
the necessary architectures using ``multistrap``.

[Multistrap](https://wiki.debian.org/Multistrap) is a Debian tool used to create root filesystem: from the
Debian's wiki

> It was designed primarily for making root filesystems for foreign architecture embedded systems, but in fact can be used for many tasks where one might also use debootstrap.
> 
> Its main limitation compared to debootstrap is that it uses apt and dpkg directly so can only work on a debian system - debootstrap depends on nothing but shell, wget, binutils and thus can run pretty-much anywhere.

```
[General]
directory=target-rootfs
cleanup=true
noauth=true
unpack=true
debootstrap=Grip Net Utils
aptsources=Grip
#tarballname=rootfs.tar
#
[Grip]
packages=apt kmod lsof
#keyring=emdebian-archive-keyring
#source=http://www.emdebian.org/grip
source=http://emdebian.bytesatwork.ch/mirror/grip
suite=wheezy-grip

[Net]
#Basic packages to enable the networking
packages=netbase net-tools udev iproute iputils-ping ifupdown isc-dhcp-client ssh
source=http://emdebian.bytesatwork.ch/mirror/grip

[Utils]
#General purpose utilities
packages=locales adduser nano less wget dialog usbutils
source=http://emdebian.bytesatwork.ch/mirror/grip
```

Then we can create a root fs, since I am corageous I choose to create one
for the PowerPC architecture

```
$ sudo multistrap -a powerpc -f multistrap-embed.conf -d /tmp/rootfs-ppc
$ sudo mount -o bind /dev/ /tmp/rootfs-ppc/dev
$ sudo cp /usr/bin/qemu-ppc-static /tmp/rootfs-ppc/usr/bin/
$ sudo LC_ALL=C LANGUAGE=C LANG=C chroot /tmp/rootfs-ppc/ dpkg --configure -a
```

```
$ sudo chroot /tmp/rootfs-ppc/ /bin/bash
root@host:/# uname -a
Linux antani 4.9.0-3-amd64 #1 SMP Debian 4.9.30-2 (2017-06-12) ppc GNU/Linux
```
