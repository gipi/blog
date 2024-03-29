---
layout: post
comments: true
title: "Yocto getting started"
tags: [embedded, yocto]
---

 - [Variables](#variables)
 - [Images](#images)
 - [SDK](#sdk)
 - [HOWTOs](#howtos)

**Yocto** is an umbrella of projects used to generate a working linux distribution for embedded system.

If you want to know more I advice to read the [bitbake user manual](https://www.yoctoproject.org/docs/1.6/bitbake-user-manual/bitbake-user-manual.html)
that is well written: it seems to explain in detail how internally bitbake works and what variables needs
and defines to work correctly.

The first thing to learn is the versions available:

 - **rocky**
 - **poky**
 - **sumo**

**Note:** Debian 9 is indicated as a compatible distribution but bad enough without ``libc6:2.28`` is not
able to compile ``pseudo-native``.

## Getting started

```
FROM ubuntu:18.04

RUN apt update && apt -y install gawk \
    wget \
    git-core \
    diffstat \
    unzip \
    texinfo \
    gcc-multilib \
     build-essential \
     chrpath \
     socat \
     libsdl1.2-dev \
     cpio \
     locales \
     python \
     python-pip \
     python3-pip
RUN locale-gen en_US.UTF-8
RUN update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
RUN pip3 install kas
```

```
$ docker run -it -u 1000:1000 -v $PWD:/app gp/yocto /bin/bash
```

## Bitbake

This is the program that handles the build process, it is written in python and
preprocess the recipes using a syntax similar to bash and python.

The source code is defined in ``bitbake/lib/bb/main.py``.

## Variables

There are two aspects of this argument: one is how to use them, the other is where are defined.
Please refer to the [related documentation](https://www.yoctoproject.org/docs/3.1/mega-manual/mega-manual.html#basic-syntax) for more information.

### Usage

| Syntax | Meaning |
|--------|---------|
| ``VAR = "foo"``   | simple assignment |
| ``VAR ?= "foo"``  | assign if it doesn't have a value |
| ``VAR ??= "foo"`` | as above but with lower precedence |
| ``VAR  = "something ${VAR_BIS} kebab"`` | ``VAR_BIS`` is expanded when ``VAR`` is referenced, if doesn't exist the the literal ``${VAR_BIS}`` is used |
| ``VAR := "something ${VAR_BIS} kebab"`` | ``VAR_BIS`` expanded when parsed |
| ``VAR += "foo"`` | append with space, with immediate effect |
| ``VAR =+ "foo"`` | prepend with space, with immediate effect |
| ``VAR .= "foo"`` | append without space, with immediate effect |
| ``VAR =. "foo"`` | prepend without space, with immediate effect |
| ``VAR_append = "foo"`` | append without space, applied at variable expansion time |
| ``VAR_prepend = "foo"`` | prepend without space, applied at variable expansion time |
| ``VAR_remove = "foo"`` | remove value, applied at variable expansion time |
| ``VAR = "foo ${@<python-code-one-liner>}"`` | expand with the result of the python code |

### Definition

A lot of variables useful to the recipes are defined directly into ``meta/conf/bitbake.conf``
that is read by ``bitbake`` when started

```
PN = "${@bb.parse.BBHandler.vars_from_file(d.getVar('FILE', False),d)[0] or 'defaultpkgname'}"
PV = "${@bb.parse.BBHandler.vars_from_file(d.getVar('FILE', False),d)[1] or '1.0'}"
PR = "${@bb.parse.BBHandler.vars_from_file(d.getVar('FILE', False),d)[2] or 'r0'}"
PE = ""
PF = "${PN}-${EXTENDPE}${PV}-${PR}"
EXTENDPE = "${@['','${PE}_'][int(d.getVar('PE') or 0) > 0]}"
P = "${PN}-${PV}"

[...snip...]

# Base package name
# Automatically derives "foo" from "foo-native", "foo-cross" or "foo-initial"
# otherwise it is the same as PN and P
SPECIAL_PKGSUFFIX = "-native -cross -initial -intermediate -crosssdk -cross-canadian"
BPN = "${@oe.utils.prune_suffix(d.getVar('PN'), d.getVar('SPECIAL_PKGSUFFIX').split(), d)}"
BP = "${BPN}-${PV}"

[...snip...]

STAMPS_DIR ?= "${TMPDIR}/stamps"
STAMP = "${STAMPS_DIR}/${MULTIMACH_TARGET_SYS}/${PN}/${EXTENDPE}${PV}-${PR}"
STAMPCLEAN = "${STAMPS_DIR}/${MULTIMACH_TARGET_SYS}/${PN}/*-*"
BASE_WORKDIR ?= "${TMPDIR}/work"
WORKDIR = "${BASE_WORKDIR}/${MULTIMACH_TARGET_SYS}/${PN}/${EXTENDPE}${PV}-${PR}"
T = "${WORKDIR}/temp"
D = "${WORKDIR}/image"
S = "${WORKDIR}/${BP}"
B = "${S}"

[...snip...]

```

the variable ``FILE`` is the filename of the recipe from which several other
recipe's variables are generated, like ``PN``, ``PV`` using the ``_`` character
as delimiter.

the evaluation orders is:

 1. variables on the command line (e.g., 'MACHINE=beagleboard bitbake
    myimage') are evaluated first,
 2. variables in local.conf,
 3. Rest depends on the order of things in bblayers.conf *and* how any
    given layer.conf is implemented (some layers preppend their stuff to the
    BBPATH and some layers append; from memory the Yocto layers prepend, but
    layers from OE usually append, and this inconsistency makes for lot of
    fun when combining layers into custom distro).

## Compilers

 - ``gcc`` is the recipe for gcc that runs on the target machine itself.
 - ``gcc-cross`` is the cross-compiler that the build system uses. If you build any recipe for the target that needs to be compiled with gcc, this is what will be used to compile that.
 - ``gcc-cross-canadian-`` is the final relocatable cross-compiler for the SDK, in this case for the ARM architecture.
 - ``gcc-crosssdk`` is an intermediate step in producing gcc-cross-canadian.
 - the ``*-initial`` are the initial versions of the compiler required to bootstrap the toolchain separately for the standard cross-compiler and for the SDK.
 - ``gcc-runtime`` builds the runtime components that come as part of gcc (e.g. libstdc++).
 - ``gccmakedep`` isn't really part of gcc itself, it's a script that comes as part of the X11 utilities that some projects need to determine dependencies for each source file.

You can select the version with ``GCCVERSION`` or ``BUILD_CC``, see [this
post "How to Set the Toolchain Version in Yocto"](https://preemptable.org/post/2019/10/31/yocto-toolchain-version) for a little explanation.

see ``poky/tree/meta/classes/native.bbclass``


## Shared state cache

The Yocto Project implements shared state code that supports incremental builds ([ref](https://www.yoctoproject.org/docs/2.8/overview-manual/overview-manual.html#shared-state-cache)).

The support is provided by the ``sstate.bbclass`` class that is enabled by default through the ``INHERIT_DISTRO``
variable.

## Cleaning

([src](https://community.nxp.com/thread/353311)) When you say bitbake
core-image-minimal, the dependencies required to build that system image are
recursively discovered and built.  However, when you want to clean things out,
the same recursion doesn't take place.  Only the package you explicitly name
gets cleaned.  So all bitbake core-image-minimal -c clean -f will actually
clean is the working directory where the system image was built.  All the rest
of the stuff -- the kernel, the shell commands, the compilers used to build
everything -- stays around.

So, alas, the question needs to be asked:  What do you want to clean out, and
why?

If you want to clean out intermediate build products for the target just to
recover disk space, you can delete those directories by hand.  From the build
directory:

 
```
$ rm -fr tmp/work
```
 

If you want to clean out the various host-side tools:

 
```
$ rm -fr tmp/sysroots
```

If you want to clean out all the accumulated system images (because they're big and take a lot of space):
 
```
$ rm -fr tmp/deploy/images
```

If you want to clean out a particular component so it will get rebuilt:
 
```
$ bitbake <component> -c clean -f
```

If you think the build and/or download caches are corrupt and want bitbake to
forget everything it thinks it knows about a component so it can be rebuilt
from scratch:

```
$ bitbake <component> -c cleanall -f
```

If you have the ``build/`` configuration directory as a git repo you can simply

```
$ git clean -f -x -d
```

to restart from scratch.

## Recipes

A **recipe** is a set of instructions to follow in order to build something;
it is divided in a few steps (called **tasks** [here the documentation](https://www.yoctoproject.org/docs/2.2/mega-manual/mega-manual.html#ref-tasks)).

 - download
 - unpack
 - prepare

You can see which tasks are defined for a particular recipe with

```
$ bitbake -c listtasks $recipe
```

and executing one with

```
$ bitbake -c $TASK $RECIPE
```

The base class that defines a recipe is in ``meta/classes/base.bbclass`` ([doc](https://www.yoctoproject.org/docs/2.2/mega-manual/mega-manual.html#ref-classes-base))
that in the first line defines which is the default task to run

```
BB_DEFAULT_TASK ?= "build"
```

and it defines

```
oe_runmake_call() {
	bbnote ${MAKE} ${EXTRA_OEMAKE} "$@"
	${MAKE} ${EXTRA_OEMAKE} "$@"
}

oe_runmake() {
	oe_runmake_call "$@" || die "oe_runmake failed"
}
```
that is used to compile stuffs at the lowest level in Yocto.

Internally in ``bitbake/lib/cookerdata.py`` the ``base`` class is
always used for all the recipes

```
class CookerDataBuilder(object):

    def __init__(self, cookercfg, worker = False):
        ...
    def parseConfigurationFiles(self, prefiles, postfiles, mc = "default"):
        ...
        # Handle any INHERITs and inherit the base class
        bbclasses  = ["base"] + (data.getVar('INHERIT') or "").split()
        for bbclass in bbclasses:
            data = _inherit(bbclass, data)
        ...
```

From the [technical FAQ](https://wiki.yoctoproject.org/wiki/Technical_FAQ#I_tried_bitbake_.3Csome_target_package_name.3E_that_I_know_exists_and_it_told_me_that_nothing_PROVIDES_this....3F)

> There are two namespaces that bitbake concerns itself with - recipe names
> (a.k.a. build time targets) and package names (a.k.a. runtime targets). You can
> specify a build time target on the bitbake command line, but not a runtime
> target; you need to find the recipe that provides the package you are trying to
> build and build that instead (or simply add that package to your image and
> build the image). In current versions bitbake will at least tell you which
> recipes have matching or similar-sounding runtime provides (RPROVIDES) so that
> you'll usually get a hint on which recipe you need to build.

### Download

First of all you need to download it, there are a lot of [fetcher](https://www.yoctoproject.org/docs/2.5/bitbake-user-manual/bitbake-user-manual.html#bb-fetchers)


## Images

[Documentation](https://www.yoctoproject.org/docs/current/mega-manual/mega-manual.html#ref-images)

An image is like a special "root" recipe

A simple dirty trick to have the list of images available is

```
$ ls meta*/recipes*/images/*.bb
meta/recipes-core/images/build-appliance-image_15.0.0.bb  meta/recipes-extended/images/core-image-lsb-dev.bb               meta/recipes-sato/images/core-image-sato-dev.bb
meta/recipes-core/images/core-image-base.bb               meta/recipes-extended/images/core-image-lsb-sdk.bb               meta/recipes-sato/images/core-image-sato-sdk.bb
meta/recipes-core/images/core-image-minimal.bb            meta/recipes-extended/images/core-image-testmaster.bb            meta/recipes-sato/images/core-image-sato-sdk-ptest.bb
meta/recipes-core/images/core-image-minimal-dev.bb        meta/recipes-extended/images/core-image-testmaster-initramfs.bb  meta-selftest/recipes-test/images/error-image.bb
meta/recipes-core/images/core-image-minimal-initramfs.bb  meta/recipes-graphics/images/core-image-clutter.bb               meta-selftest/recipes-test/images/oe-selftest-image.bb
meta/recipes-core/images/core-image-minimal-mtdutils.bb   meta/recipes-graphics/images/core-image-weston.bb                meta-selftest/recipes-test/images/test-empty-image.bb
meta/recipes-core/images/core-image-tiny-initramfs.bb     meta/recipes-graphics/images/core-image-x11.bb                   meta-selftest/recipes-test/images/wic-image-minimal.bb
meta/recipes-extended/images/core-image-full-cmdline.bb   meta/recipes-rt/images/core-image-rt.bb                          meta-skeleton/recipes-multilib/images/core-image-multilib-example.bb
meta/recipes-extended/images/core-image-kernel-dev.bb     meta/recipes-rt/images/core-image-rt-sdk.bb
meta/recipes-extended/images/core-image-lsb.bb            meta/recipes-sato/images/core-image-sato.bb
```

An image is intended to extend ``meta/classes/images.bbclass``

The part interesting for me is

```
IMAGE_CLASSES ??= ""

# rootfs bootstrap install
# warning -  image-container resets this
ROOTFS_BOOTSTRAP_INSTALL = "run-postinsts"

# Handle inherits of any of the image classes we need
IMGCLASSES = "rootfs_${IMAGE_PKGTYPE} image_types ${IMAGE_CLASSES}"
# Only Linux SDKs support populate_sdk_ext, fall back to populate_sdk_base
# in the non-Linux SDK_OS case, such as mingw32
IMGCLASSES += "${@['populate_sdk_base', 'populate_sdk_ext']['linux' in d.getVar("SDK_OS")]}"
IMGCLASSES += "${@bb.utils.contains_any('IMAGE_FSTYPES', 'live iso hddimg', 'image-live', '', d)}"
IMGCLASSES += "${@bb.utils.contains('IMAGE_FSTYPES', 'container', 'image-container', '', d)}"
IMGCLASSES += "image_types_wic"
IMGCLASSES += "rootfs-postcommands"
IMGCLASSES += "image-postinst-intercepts"
inherit ${IMGCLASSES}

 ...

fakeroot python do_rootfs () {
    from oe.rootfs import create_rootfs
    from oe.manifest import create_manifest
 ...
    create_rootfs(d, progress_reporter=progress_reporter, logcatcher=logcatcher)
 ...
}
do_rootfs[dirs] = "${TOPDIR}"
do_rootfs[cleandirs] += "${S} ${IMGDEPLOYDIR}"
do_rootfs[umask] = "022"
do_rootfs[file-checksums] += "${POSTINST_INTERCEPT_CHECKSUMS}"
addtask rootfs after do_prepare_recipe_sysroot
```

the ``create_rootfs()`` is imported from ``meta/lib/oe`` and it seems to populate the
root filesystem installing the packages one by one!

If you want to create a new image, remember to ``export IMAGE_BASENAME``

Also ``meta/classes/core-image.bbclass`` that defines ``core-image``

```
# Common code for generating core reference images
#
# Copyright (C) 2007-2011 Linux Foundation

# IMAGE_FEATURES control content of the core reference images
# 
# By default we install packagegroup-core-boot and packagegroup-base-extended packages;
# this gives us working (console only) rootfs.
#
# Available IMAGE_FEATURES:
#
# - x11                 - X server
# - x11-base            - X server with minimal environment
# - x11-sato            - OpenedHand Sato environment
# - tools-debug         - debugging tools
 ...
# - read-only-rootfs    - tweaks an image to support read-only rootfs
# - splash              - bootup splash screen
#
FEATURE_PACKAGES_x11 = "packagegroup-core-x11"
  ...
FEATURE_PACKAGES_ssh-server-openssh = "packagegroup-core-ssh-openssh"
FEATURE_PACKAGES_hwcodecs = "${MACHINE_HWCODECS}"


# IMAGE_FEATURES_REPLACES_foo = 'bar1 bar2'
# Including image feature foo would replace the image features bar1 and bar2
IMAGE_FEATURES_REPLACES_ssh-server-openssh = "ssh-server-dropbear"

# IMAGE_FEATURES_CONFLICTS_foo = 'bar1 bar2'
# An error exception would be raised if both image features foo and bar1(or bar2) are included


CORE_IMAGE_BASE_INSTALL = '\
    packagegroup-core-boot \
    packagegroup-base-extended \
    \
    ${CORE_IMAGE_EXTRA_INSTALL} \
    '

CORE_IMAGE_EXTRA_INSTALL ?= ""

IMAGE_INSTALL ?= "${CORE_IMAGE_BASE_INSTALL}"

inherit image
```

### Package groups

Defined in ``meta/classes/packagegroup.bbclass``

### ``DEPENDS`` vs ``RDEPENDS``

[link to mailing list](https://www.yoctoproject.org/pipermail/yocto/2013-August/015792.html)


## Start a new project

First of all you need to have the Yocto base repository cloned

```
$ git clone git://git.yoctoproject.org/poky.git
```

and the dependencies installed

```
# apt-get install gawk wget git-core diffstat unzip texinfo gcc-multilib \
     build-essential chrpath socat libsdl1.2-dev xterm python python2.7
```

and then you have to define a new configuration build directory
(that usually is going to be saved under versioning): for example
below you see what happens when you are creating one from scratch:

```
$ source poky-rocko/oe-init-build-env $BUILD_CONF_DIR
You had no conf/local.conf file. This configuration file has therefore been
created for you with some default values. You may wish to edit it to, for
example, select a different MACHINE (target hardware). See conf/local.conf
for more information as common configuration options are commented.

You had no conf/bblayers.conf file. This configuration file has therefore been
created for you with some default values. To add additional metadata layers
into your configuration please add entries to conf/bblayers.conf.

The Yocto Project has extensive documentation about OE including a reference
manual which can be found at:
    http://yoctoproject.org/documentation

For more information about OpenEmbedded see their website:
    http://www.openembedded.org/


### Shell environment set up for builds. ###

You can now run 'bitbake <target>'

Common targets are:
    core-image-minimal
    core-image-sato
    meta-toolchain
    meta-ide-support

You can also run generated qemu images with a command like 'runqemu qemux86'
```

I don't know if can be defined as a best practice, but I usually create a manifest
to use with ``repo`` to download all the necessary layers together with the configuration
build directory; you can see for example [this repo](https://github.com/gipi/rpi0-repo)
for the Raspberry Pi.

I advise you to indicate a suitable path for variables like ``DL_DIR`` in order to avoid
redownloading over and over the same stuff.

 - https://git.yoctoproject.org/cgit/cgit.cgi/poky/tree/meta-poky/conf/local.conf.sample.extended

## Create a new layer

 - https://www.yoctoproject.org/docs/current/dev-manual/dev-manual.html#creating-your-own-layer

```
$ mkdir meta-whatever && cd meta-whatever
$ mkdir conf
$ cat > conf/layer.conf <<EOF
# We have a conf and classes directory, add to BBPATH
BBPATH .= ":\${LAYERDIR}"

# We have recipes-* directories, add to BBFILES
BBFILES += "\${LAYERDIR}/recipes-*/*/*.bb \\
            \${LAYERDIR}/recipes-*/*/*.bbappend"

BBFILE_COLLECTIONS += "whatever"                           # this is a unique identifier
BBFILE_PATTERN_whatever = "^\${LAYERDIR}/"                  # to be changed here
BBFILE_PRIORITY_whatever = "5"                             # and here
LAYERVERSION_whatever = "1"               # layer version  # and here
LAYERSERIES_COMPAT_whatever = "zeus"      # compatibility  # and here
EOF
```

## Add a new machine

 - https://www.yoctoproject.org/docs/current/dev-manual/dev-manual.html#platdev-newmachine

```
$ cd meta-whatever
$ mkdir conf/machine/
$ cat > conf/machine/whatever-soc.conf <<EOF
require conf/machine/include/tune-cortexa8.inc
```

## Use your layer

Into ``conf/bblayer.conf``, you can indicate your layer

```
# POKY_BBLAYERS_CONF_VERSION is increased each time build/conf/bblayers.conf
# changes incompatibly
POKY_BBLAYERS_CONF_VERSION = "2"

BBPATH = "${TOPDIR}"
BBFILES ?= ""

LAYER_PATH = "${TOPDIR}/../sources" # I assume your layers are into sources/

BBLAYERS ?= " \
    ${LAYER_PATH}/meta \
    ${LAYER_PATH}/meta-poky \
    ${LAYER_PATH}/meta-whatever \
"
```


## Building

The main purpose of Yocto is building something and the main tool to accomplish that
is ``bitbake``: to initialize the environment you have to

```
$ source poky-rocko/oe-init-build-env $BUILD_CONF_DIR
### Shell environment set up for builds. ###

You can now run 'bitbake <target>'

Common targets are:
    core-image-minimal
    core-image-sato
    meta-toolchain
    meta-ide-support

You can also run generated qemu images with a command like 'runqemu qemux86'
```

You can use the flag ``--continue`` to push the build forward as much as possible.

## Clean

```
$ bitbake -c cleanall <recipe>
```

## Kernel

 - yoctoproject.org/docs/1.6/kernel-dev/kernel-dev.html
 - https://www.yoctoproject.org/docs/1.8.1/kernel-dev/kernel-dev.html#using-an-in-tree-defconfig-file

First of all the kernel is enabled by the ``PREFERRED_PROVIDER_virtual/kernel`` variable
and you can choose the preferred version like

```
PREFERRED_VERSION_linux-yocto ??= "4.19.%"
```

Remember that the kernel is a particular recipe that needs particular attention; in particular
take in mind that for example the ``CFLAGS`` are not passed directly but set by the ``Makefile``
using the ``KBUILD_CFLAGS`` and family.

Difference between linux-yocto and ???

If you want ``zImage`` and device tree in the same binary exists the variable ``KERNEL_DEVICETREE_BUNDLE``.

```
KCONFIG_MODE = "--alldefconfig"
```

```
FILESEXTRAPATHS_prepend := "${THISDIR}/files:"
     SRC_URI += "file://defconfig"
```

## WIC

 - https://www.yoctoproject.org/docs/2.2.1/dev-manual/dev-manual.html#openembedded-kickstart-wks-reference
 - https://www.yoctoproject.org/docs/2.4.2/dev-manual/dev-manual.html#creating-partitioned-images-using-wic

It's a utility for creating disk images.

You can increase the debug level with ``--debug`` (after the subcommand)

IMAGE_TYPES
IMAGE_BOOT_FILES

```
$ wic ls ./galaxy-s-202003291054-mmcblk.direct:1
Volume in drive : is boot       
 Volume Serial Number is 731F-09B5
Directory for ::/

ZIMAGE         1166704 2020-03-29   8:54  zImage
        1 file            1 166 704 bytes
                          9 693 184 bytes free
```

note that generated files won't be included in the previous listing (like ``extlinux`` ;)).

### Modules

To my surprise seems that the modules are installed by default in the root filesystem
but you need to add them into ``IMAGE_INSTALL`` like

```
IMAGE_INSTALL_append = " kernel-modules"
```

### Initrd&Initramfs

[INITRAMFS_IMAGE](https://www.yoctoproject.org/docs/3.1/ref-manual/ref-manual.html#var-INITRAMFS_IMAGE)

core-image-minimal-initramfs

```
The INITRAMFS_IMAGE image variable will cause an additional recipe to
# be built as a dependency to the what ever rootfs recipe you might be
# using such as core-image-sato.  The initramfs might be needed for
# the initial boot of of the target system such as to load kernel
# modules prior to mounting the root file system.
#
# INITRAMFS_IMAGE_BUNDLE variable controls if the image recipe
# specified by the INITRAMFS_IMAGE will be run through an extra pass
# through the kernel compilation in order to build a single binary
# which contains both the kernel image and the initramfs.  The
# combined binary will be deposited into the tmp/deploy directory.
# NOTE: You can set INITRAMFS_IMAGE in an image recipe, but
#       INITRAMFS_IMAGE_BUNDLE can only be set in a conf file.
```

## Init system

```
VIRTUAL-RUNTIME_init_manager ?= "sysvinit"
VIRTUAL-RUNTIME_initscripts ?= "initscripts"
```


## Feature

https://www.yoctoproject.org/docs/1.7/ref-manual/ref-manual.html#ref-features-machine

## SDK

```
$ bitbake -c populate_sdk $IMAGE_NAME
```

this creates the install script in ``tmp/deploy/sdk``; at installation time it asks
you the path where to place the SDK, usually something like ``/opt/poky/$VERSION/``.

When you want to enable the tools available in the SDK you simply activate it by

```
$ source $PATH_TO_SDK/environment-setup-$machine
```

## HOWTOs

### Substitute a file

Simply add to your ``bbappend``

```
FILESEXTRAPATHS_prepend := "${THISDIR}/files/:"
```

with inside the file you want to replace in the original recipe.

### Add a package to your image

This is done modifying the ``IMAGE_INSTALL`` variable, that can be done
with ``_append`` or ``+=``

```
IMAGE_INSTALL_append = " vim"
```

but [take in mind](https://www.yoctoproject.org/pipermail/yocto/2012-June/007363.html) that ``_append``
is preferred (there are ordering issues: ``meta/classes/core-image.bbclass`` contains the line

```
IMAGE_INSTALL ?= "${CORE_IMAGE_BASE_INSTALL}"
```

so it's possible that your packages are discarded).

[documentation](https://www.yoctoproject.org/docs/3.1/dev-manual/dev-manual.html#usingpoky-extend-customimage-localconf)

However to double check what is installed, look at the ``<image name>.manifest`` in the final directory.

### Enable debian package management

Add ``package-management`` to ``IMAGE_FEATURES`` and ``PACKAGE_CLASSES ?= "package_deb"``.

### Include your file

```
$ bitbake-layers show-recipes vim
 ...
=== Matching recipes: ===
vim:
  meta                 8.1.1518
$ bitbake-layers show-appends formfactor
 ...
=== Matched appended recipes ===
formfactor_0.0.bb:
  /hack/yocto-samsung-galaxys/../poky-rocko/meta-yocto-bsp/recipes-bsp/formfactor/formfactor_0.0.bbappend
  /hack/yocto-samsung-galaxys/../meta-s5pv210/recipes-bsp/formfactor/formfactor_0.0.bbappend
```

### List recipes

```
$ bitbake -s core-image-minimal
```

### List packages

```
$ bitbake -g <image> && cat pn-buildlist | grep -ve "native" | sort | uniq
```

### Find appended layers

```
$ bitbake-layers show-appends
```

### Find which recipe creates a file

This works only **after** building

```
$ oe-pkgdata-util find-path $FILE
```

### Find build timestamp

It's located into ``/etc/timestamp``.

### Monitoring disk space usage

```
# Disk Space Monitoring during the build
#
# Monitor the disk space during the build. If there is less that 1GB of space or less
# than 100K inodes in any key build location (TMPDIR, DL_DIR, SSTATE_DIR), gracefully
# shutdown the build. If there is less that 100MB or 1K inodes, perform a hard abort
# of the build. The reason for this is that running completely out of space can corrupt
# files and damages the build in ways which may not be easily recoverable.
# It's necesary to monitor /tmp, if there is no space left the build will fail
# with very exotic errors.
BB_DISKMON_DIRS ??= "\
    STOPTASKS,${TMPDIR},1G,100K \
    STOPTASKS,${DL_DIR},1G,100K \
    STOPTASKS,${SSTATE_DIR},1G,100K \
    STOPTASKS,/tmp,100M,100K \
    ABORT,${TMPDIR},100M,1K \
    ABORT,${DL_DIR},100M,1K \
    ABORT,${SSTATE_DIR},100M,1K \
    ABORT,/tmp,10M,1K"
```

## Links

 - https://layers.openembedded.org/
 - https://www.yoctoproject.org/docs/current/ref-manual/ref-manual.html#qa-errors-and-warnings
 - [Yocto project - Mega Manual](https://www.yoctoproject.org/docs/current/mega-manual/mega-manual.html)
 - [Yocto Project Board Support Package Developer's Guide](https://www.yoctoproject.org/docs/2.4/bsp-guide/bsp-guide.html)
 - [Yocto Project Development Tasks Manual](https://www.yoctoproject.org/docs/current/dev-manual/dev-manual.html) if you want to write recipes, read this!
 - [Bitbale user manual](https://www.yoctoproject.org/docs/1.6/bitbake-user-manual/bitbake-user-manual.html)
 - [Yocto WIKI](https://wiki.yoctoproject.org/wiki/Main_Page)
 - [Prebuilt toolchains](http://downloads.yoctoproject.org/releases/yocto/yocto-1.8/toolchain/)
 - [Prebuilt kernels and rootfs](http://downloads.yoctoproject.org/releases/yocto/yocto-1.8/machines/qemu)
 - https://elinux.org/Bitbake_Cheat_Sheet
 - https://a4z.bitbucket.io/docs/BitBake/guide.html
 - https://www.yoctoproject.org/docs/what-i-wish-id-known/
 - https://github.com/shr-distribution/meta-smartphone/
 - https://git.yoctoproject.org/cgit.cgi/poky/plain/meta/classes/package.bbclass
 - https://stackoverflow.com/questions/47047209/how-to-change-the-config-of-u-boot-in-yocto
 - https://events.static.linuxfound.org/sites/events/files/slides/can_board_bring_up_be_less_painful_insop_song.pdf
 - https://community.nxp.com/thread/353311
 - https://stackoverflow.com/questions/18074979/methods-for-speeding-up-build-time-in-a-project-using-bitbake
 - http://www.wiki.xilinx.com/Yocto
 - https://stackoverflow.com/questions/37347808/how-to-use-an-own-device-tree-and-modified-kernel-config-in-yocto

```
Scanning mmc 0:1...
Found /extlinux/extlinux.conf
Retrieving file: /extlinux/extlinux.conf
229 bytes read in 16 ms (13.7 KiB/s)
0:      Yocto
Retrieving file: /zImage-s5pv210-galaxys--5.2.32+git0+bb2776d6be_73b12de4c8-r0-s5pv210-20200402133134.dtb.bin
3800010 bytes read in 730 ms (5 MiB/s)
append: root=/dev/mmcblk2p2 rootwait rootwait console=ttySAC2 console=tty earlyprintk
Retrieving file: /s5pv210-galaxys.dtb
30586 bytes read in 21 ms (1.4 MiB/s)
Kernel image @ 0x32000000 [ 0x000000 - 0x398450 ]
## Flattened Device Tree blob at 33000000
   Booting using the fdt blob at 0x33000000
   Loading Device Tree to 34ff5000, end 34fff779 ... OK

Starting kernel ...
```



 - https://stackoverflow.com/questions/47047209/how-to-change-the-config-of-u-boot-in-yocto
 - https://www.element14.com/community/community/designcenter/single-board-computers/riotboard/blog/2014/09/24/riotboard-yocto-part2-build-u-boot-using-yocto
 - https://community.nxp.com/docs/DOC-94953
 - http://www.embeddedlinux.org.cn/oemanual/recipes_examples.html#recipes_helloworld_example
 - http://www.embeddedlinux.org.cn/oemanual/recipes_syntax.html
 - http://www.embeddedlinux.org.cn/OEManual/recipes_versioning.html
 - https://stackoverflow.com/questions/26003402/how-to-add-global-cxx-compiler-flag-to-yocto-build
 - https://stackoverflow.com/questions/42538230/how-to-add-preprocessor-definition-in-cmake-projet-build-by-yocto?rq=1
 - https://www.toradex.com/community/questions/7401/can-i-run-full-screen-qt-application-with-lxde-dis.html
 - [qemu-kvm screen resolution](https://bbs.archlinux.org/viewtopic.php?id=153526)
 - https://stackoverflow.com/questions/31617575/how-to-use-usb-camera-in-qemu
 - https://doc.qt.io/qt-5.10/scalability.html
 - https://git.yoctoproject.org/cgit/cgit.cgi/poky/tree/meta/classes/update-alternatives.bbclass
 - https://www.yoctoproject.org/docs/current/ref-manual/ref-manual.html#ref-classes-update-alternatives
 - https://stackoverflow.com/questions/7373349/qt-shadow-building
 - https://stackoverflow.com/questions/17305374/qt-5-0-built-in-logging
 - https://developer.toradex.com/knowledge-base/board-support-package/openembedded-(core)#Adding_the_Qt5_Layer
 - https://medium.com/@shigmas/yocto-pi-and-qt-e9f2df38a610
 - [SO WORKDIR question](https://stackoverflow.com/questions/28827764/workdir-in-yocto-receipe)
 - [questions about WORKDIR and S usage and files/ stuff](http://lists.openembedded.org/pipermail/openembedded-core/2015-February/101990.html)
 - https://www.kynetics.com/docs/2018/Yocto-SDK-Qt/
 - https://wiki.rdkcentral.com/display/RDK/Yocto+Software+Development+Kit%28SDK%29+Guide
 - https://wiki.yoctoproject.org/wiki/TipsAndTricks/Cmake,Eclipse,_and_SDKS
 - https://stackoverflow.com/questions/49532977/yocto-generated-nativesdk-cmake-sdk-is-incomplete
 - https://wiki.yoctoproject.org/wiki/TipsAndTricks/QuickAndDirtyKernelConfig to quickly modify the ``.config`` without creating another recipe
 - https://old.yoctoproject.org/training/kernel-lab
 - https://www.yoctoproject.org/docs/1.6.1/kernel-dev/kernel-dev.html
 - https://stefanchrist.eu/blog/2017_09_15/Yocto%20Recipes%20vs%20Packages.xhtml
 - https://github.com/shantanoo-desai/yoctoproject-cheatsheet

