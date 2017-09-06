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

This is not a complete replacement for the images linked above since at the end
of the procedure won't have a linux kernel to use to start ``QEMU`` but I think
it's useful for someone with already a running instance.


## Create the filesystem

The dependencies on a Debian system are

```
$ sudo apt-get install qemu multistrap qemu-user-static
```

since I am corageous I choose to create one root filesystem for the PowerPC architecture:
save the content below as ``multistrap.conf``

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
noauth=true
packages=apt kmod lsof
source=http://emdebian.bytesatwork.ch/mirror/grip
keyring=emdebian-archive-keyring
suite=stable-grip

[Net]
#Basic packages to enable the networking
packages=netbase net-tools udev iproute iputils-ping ifupdown isc-dhcp-client ssh

[Utils]
#General purpose utilities
packages=locales adduser nano less wget dialog usbutils
```

Then we can create a root fs using ``multistrap`` (the ``-a`` flag is what
sets the architecture)

```
$ sudo multistrap -a powerpc -f multistrap.conf -d /tmp/rootfs-ppc
$ sudo mount -o bind /dev/ /tmp/rootfs-ppc/dev
$ sudo cp /usr/bin/qemu-ppc-static /tmp/rootfs-ppc/usr/bin/
$ sudo LC_ALL=C LANGUAGE=C LANG=C chroot /tmp/rootfs-ppc/ dpkg --configure -a
```

select ``NO`` when asked to use ``dash`` as default shell. Now we can enter
inside the system and how can see now you have a PowerPC architecture

```
$ sudo chroot /tmp/rootfs-ppc/ /bin/bash
root@host:/# uname -a
Linux antani 4.9.0-3-amd64 #1 SMP Debian 4.9.30-2 (2017-06-12) ppc GNU/Linux
```

If you want an internet connection remember to ``mount --bind`` the
``resolv.conf`` file inside the ``chroot``.

If you want to create a real root filesystem for QEMU (or whatever) you can use the
following command after installing the ``libguestfs-tools`` package:

```
$ sudo virt-make-fs --format=qcow2 --size=+200M /tmp/rootfs-ppc/ /tmp/rootfs.img
```
(see [virt-make-fs](http://libguestfs.org/virt-make-fs.1.html) ``man`` page for more informations).

Probably in a following up post I will write about using projects like [OpenEmbedded](https://www.openembedded.org) or
[buildroot](https://buildroot.org/) to have a complete and customizable running systems.
