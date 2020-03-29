---
layout: post
comments: true
title: "Debian, a cheat sheet (sort of)"
tags: [debian, WIP, cheat sheet]
---

## Releases

| Version | Codename | Date |
|---------|----------|------|
| 1.0     | Buzz | 1996 |
| 1.2 | Rex | 1996 |
| 1.3 | Bo | 1997 |
| 2.0 | Hamm | 1998 |
| 2.1 | Slink |1999 |
| 2.2 | Potato | 2000 |
| 3.0 | Woody | 2002 |
| 3.1 | Sarge | 2005 |
| 4.0 | Etch | 2007 |
| 5.0 | Lenny | 2009 |
| 6.0 | Squeeze | 2011 |
| 7.0 | Wheezy | 2013 |
| 8.0 | Jessie | 2015 |
| 9.0 | Stretch | 2017 |
| 10  | Buster | 2019 |

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

## Download packages from snapshot.debian.org

Can occur that you need the binary (``gcc`` I'm talking to you)
and the only way to obtain it a part from recompiling is from
the packages of an old distribution; you can obtain a little easier
using a custom configuration file for ``apt``:

```
Dir::Etc::main ".";
Dir::Etc::Parts "./apt.conf.d";
Dir::Etc::sourcelist "./sources.list";
Dir::Etc::sourceparts "./sources.list.d";
Dir::State "./apt-tmp";
Dir::State::status "./apt-tmp/status";
Dir::Cache "./apt-tmp";
Acquire::Check-Valid-Until false;
Acquire::AllowInsecureRepositories true;
Acquire::AllowDowngradeToInsecureRepositories true;
```

and in ``sources.list`` you can add the entries from snapshot.debian.org
using as distribution one that was "active" at that time

```
$ mkdir -p apt-tmp/lists/partial
$ touch apt-tmp/status
$ apt-get -c apt.conf update
$ apt-get -c apt.conf install -d <package>
```

once you have the packages into ``apt-tmp/archives/`` you can
use the following one-liner

```
$ for i in $(find apt-tmp/archives -name \*.deb); do echo --- $i;dpkg -x $i sysroot/ ;done
```

and have all the files into ``sysroot/``.

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
 - [Downgrade all Debian packages to a specific date](https://vincent.bernat.ch/en/blog/2020-downgrade-debian)

