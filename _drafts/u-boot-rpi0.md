---
layout: post
comments: true
title: "Using U-Boot as bootloader with a RaspberryPi Zero"
tags: [embedded, rpi, u-boot]
---

This is a guide about using u-boot with a raspberry pi zero.

I'm not telling you how to compile all the stuffs, read this [post](http://www.jumpnowtek.com/rpi/Raspberry-Pi-Systems-with-Yocto.html)
if you want to use Yocto to build all from scratch.

```
PREFERRED_PROVIDER_virtual/bootloader = "u-boot"

KERNEL_IMAGETYPE = "zImage"
KERNEL_BOOTCMD = "bootz"
CMDLINE_append = " console=tty0"
```

``boot.cmd`` to be compiled in ``boot.scr``

```
fdt addr ${fdt_addr} && fdt get value bootargs /chosen bootargs
fatload mmc 0:1 ${kernel_addr_r} zImage
bootz ${kernel_addr_r} - ${fdt_addr}
```

``cmdline.txt``

```
dwc_otg.lpm_enable=0 console=serial0,115200 root=/dev/mmcblk0p2 rootfstype=ext4 rootwait console=tty0
```

## Boot sequence

 - **stage 1:** is the on-chip ROM, loads stage2 in the L2 cache
 - **stage 2:** is ``bootcode.bin``. Enable SDRAM and loads stage 3
 - **stage 3:** is ``loader.bin``. It loads ``start.elf``
 - ``start.elf`` loads ``kernel.img``

``kernel.img`` is usually the linux kernel, we want to substitute it with ``u-boot``.
This is achievable renaming accordingly the file or changing the right variable
in the ``config.txt`` file. ``cmdline.txt`` instead contains the arguments for the kernel.

The complicated thing that happens with this device is that the ``start.elf`` prepare
already the ``fdt`` at a specific address and doesn't need to be loaded from the
SD card. The address is passed as environment variable in ``u-boot``.

Take in mind that some documents uses ``fdt_addr_r`` instead of the mainline's ``fdt_addr``.

 - [RPi Boot flow](https://www.raspberrypi.org/documentation/hardware/raspberrypi/bootmodes/bootflow.md)
 - [DEVICE TREES, OVERLAYS, AND PARAMETERS](https://www.raspberrypi.org/documentation/configuration/device-tree.md)
 - https://www.denx.de/wiki/view/DULG/UBootEnvVariables
 - https://www.denx.de/wiki/DULG/UBootCmdFDT
 - https://elinux.org/RPi_U-Boot#Test_U-Boot
 - https://dius.com.au/2015/08/19/raspberry-pi-uboot/
 - https://bootlin.com/blog/dt-overlay-uboot-libfdt/

