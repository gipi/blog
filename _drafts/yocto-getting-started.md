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

## Variables

There are two aspects of this argument: one is how to use them, the other is where are defined.

### Usage

### Definition

A lot of variables useful to the recipes are defined directly into ``bitbake.conf``

```
PN = "${@bb.parse.BBHandler.vars_from_file(d.getVar('FILE', False),d)[0] or 'defaultpkgname'}"
PV = "${@bb.parse.BBHandler.vars_from_file(d.getVar('FILE', False),d)[1] or '1.0'}"
PR = "${@bb.parse.BBHandler.vars_from_file(d.getVar('FILE', False),d)[2] or 'r0'}"
PE = ""
PF = "${PN}-${EXTENDPE}${PV}-${PR}"
EXTENDPE = "${@['','${PE}_'][int(d.getVar('PE') or 0) > 0]}"
P = "${PN}-${PV}"

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

```

## Recipes

First of all you need to download it, there are a lot of [fetcher](https://www.yoctoproject.org/docs/2.5/bitbake-user-manual/bitbake-user-manual.html#bb-fetchers)

## Images

[Link](https://www.yoctoproject.org/docs/current/mega-manual/mega-manual.html#ref-images)

## HOWTOs

### Include your file

```
$ bitbake-layers show-recipes /etc/network/interfaces
$ bitbake-layers show-appends init-ifupdown
```

## Links

 - [Yocto project - Mega Manual](https://www.yoctoproject.org/docs/current/mega-manual/mega-manual.html)
 - [Yocto Project Board Support Package Developer's Guide](https://www.yoctoproject.org/docs/2.4/bsp-guide/bsp-guide.html)
 - [Yocto Project Development Tasks Manual](https://www.yoctoproject.org/docs/current/dev-manual/dev-manual.html) if you want to write recipes, read this!
 - [Bitbale user manual](https://www.yoctoproject.org/docs/1.6/bitbake-user-manual/bitbake-user-manual.html)
 - [Yocto WIKI](https://wiki.yoctoproject.org/wiki/Main_Page)
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

