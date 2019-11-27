---
layout: post
comments: true
title: "Debian, a cheat sheet (sort of)"
tags: [debian, WIP, cheat sheet]
---

## Commands

| Command | Description |
|---------|-------------|
| ``dpkg -S <filename-search-pattern>`` | Search for a filename from installed packages |

## Building packages

The dependencies needed for build package from source are

    # sudo apt-get install build-essential fakeroot devscripts dpatch dh-make expect

to build a package obviously you need the source and its dependencies

    $ apt-get source blender
    # apt-get build-dep blender

and finally you can build it

    $ debuild -b -uc -us --no-pre-clean

If you want to install the dependencies before the build of the package you can do

```
$ mk-build-deps
$ apt install ./<package>_build-deps_<version>.deb
```

There are some utilities in Debian that can be used in order to deploy correctly a package;
first of all, can be inspiring to look at some pre-existent packages in order to understand
how some things work. A page with the git repositories of packages can be found here: http://packages.qa.debian.org/;
searching for a package shows a page with a link to the repositories.

It is also possible to [cross compile](https://wiki.debian.org/CrossCompiling) a package.

If during packaging an error like happens

    dpkg: error processing easy-backup (--purge):
    subprocess installed post-removal script returned error exit status 10

then delete `/var/lib/dpkg/info/xyz.postrm`.

In order to install a specific package version you can use a command like

    $ apt-get install subversion-tools=1.3.2-5~bpo1

### files

 - [debian/control](https://www.debian.org/doc/debian-policy/ch-controlfields.html)

### DCH

it's the tool used to increment the version number and edit the ``changelog`` file.
[Standard documentation](https://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-Version) about
version system used in Debian.

### Utilities

 - http://www.fifi.org/doc/debconf-doc/tutorial.html
 - http://webapps-common.alioth.debian.org/draft/html/index.html
 - http://people.debian.org/~seanius/policy/examples/dbconfig-common/doc/dbconfig-common-using.html
 - http://mdcc.cx/debian/debugging_debian_package_installations.html
 - [Checkinstall](http://wiki.debian.org/CheckInstall) CheckInstall keeps track of all the files created or modified by your installation script ("make install" "make install_modules", "setup", etc), builds a standard binary package and installs it in your system giving you the ability to uninstall it with your distribution's standard package management utilities.
 - https://wiki.debian.org/PkgSplit

### Patches

The patches are into ``patch/``, one file for each patch, and a file named ``series`` with the list of all the patches
to apply.

## Links

 - [Source list generator](http://debgen.simplylinux.ch/)
 - https://tracker.debian.org/
 - https://serverfault.com/questions/279153/why-does-reprepro-complain-about-the-all-architecture
 - https://vincent.bernat.im/en/blog/2016-pragmatic-debian-packaging
 - https://grml.org/
 - https://fatemachine.github.io/live-armor/ Building Custom Live Images with Debian and Grsecurity
 - [Avoiding tests when building Debian packages](https://iomem.com/archives/18-Avoiding-tests-when-building-Debian-packages.html)

