---
layout: post
comments: true
title: "Yocto getting started"
tags: [embedded, yocto, linux]
---

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

## Bitbake

This is the program that handles the build process, it is written in python and
preprocess the recipes using a syntax similar to bash and python.

The source code is defined in ``bitbake/lib/bb/main.py``.

## Variables

There are two aspects of this argument: one is how to use them, the other is where are defined.

### Usage

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

## Compilers

 - ``gcc`` is the recipe for gcc that runs on the target machine itself.
 - ``gcc-cross`` is the cross-compiler that the build system uses. If you build any recipe for the target that needs to be compiled with gcc, this is what will be used to compile that.
 - ``gcc-cross-canadian-`` is the final relocatable cross-compiler for the SDK, in this case for the ARM architecture.
 - ``gcc-crosssdk`` is an intermediate step in producing gcc-cross-canadian.
 - the ``*-initial`` are the initial versions of the compiler required to bootstrap the toolchain separately for the standard cross-compiler and for the SDK.
 - ``gcc-runtime`` builds the runtime components that come as part of gcc (e.g. libstdc++).
 - ``gccmakedep`` isn't really part of gcc itself, it's a script that comes as part of the X11 utilities that some projects need to determine dependencies for each source file.

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

### Download

First of all you need to download it, there are a lot of [fetcher](https://www.yoctoproject.org/docs/2.5/bitbake-user-manual/bitbake-user-manual.html#bb-fetchers)

## Images

[Link](https://www.yoctoproject.org/docs/current/mega-manual/mega-manual.html#ref-images)

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

## Kernel

Remember that the kernel is a particular recipe that needs particular attention; in particular
take in mind that for example the ``CFLAGS`` are not passed directly but set by the ``Makefile``
using the ``KBUILD_CFLAGS`` and family.

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

### Include your file

```
$ bitbake-layers show-recipes /etc/network/interfaces
$ bitbake-layers show-appends init-ifupdown
```
### Find which recipe creates a file

```
$ oe-pkgdata-util find-path $FILE
```

## Links

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

