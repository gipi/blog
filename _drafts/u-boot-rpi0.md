---
layout: post
comments: true
title: "Using U-Boot as bootloader with a RaspberryPi Zero"
tags: [embedded, rpi, u-boot]
---

This is a guide about using u-boot with a raspberry pi zero.

I'm not telling you how to compile all the stuffs, read this [post](http://www.jumpnowtek.com/rpi/Raspberry-Pi-Systems-with-Yocto.html)
if you want to use Yocto to build all from scratch.

## Boot sequence

 - **stage 1:** is the on-chip ROM, loads stage2 in the L2 cache
 - **stage 2:** is ``bootcode.bin``. Enable SDRAM and loads stage 3
 - **stage 3:** is ``loader.bin``. It loads ``start.elf``
 - ``start.elf`` loads ``kernel.img``

``kernel.img`` is usually the linux kernel, we want to substitute it with ``u-boot``.
This is achievable renaming accordingly the file or changing the right variable
in the ``config.txt`` file.

 - https://www.denx.de/wiki/view/DULG/UBootEnvVariables
 - https://www.raspberrypi.org/documentation/configuration/device-tree.md
 - https://www.denx.de/wiki/DULG/UBootCmdFDT
 - https://elinux.org/RPi_U-Boot#Test_U-Boot
 - https://dius.com.au/2015/08/19/raspberry-pi-uboot/
 - https://bootlin.com/blog/dt-overlay-uboot-libfdt/
 - https://www.raspberrypi.org/forums/viewtopic.php?t=134018
 - https://www.raspberrypi.org/forums/viewtopic.php?f=29&t=137599

