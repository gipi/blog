---
layout: post
comments: true
title: "Reusing old shit: creating a BSP using Yocto for the Samsung Galaxy S (S5PV210)"
tags: [embedded, yocto]
---


 - http://www.friendlyarm.net/products/mini210

## Specifications

Obviously there are a lot of componentes in a smartphone, like
the follwing (table copied from the [replicant's page](https://redmine.replicant.us/projects/replicant/wiki/GalaxySGTI9000)


| Component | Name | Source | Status |
|-----------|------|--------|--------|
| SoC       | Samsung S5PC110/S5PV210 ("Hummingbird" FastCore Cortex-A8) | Linux kernel | Linux kernel support
| GPU           | PowerVR SGX540 | https://secure.wikimedia.org/wikipedia/en/wiki/Exynos | Linux kernel support, proprietary userspace
| Audio Codec   | WM8994 | Linux kernel | Linux kernel support (ALSA), free userspace
| Modem         | XMM6160 | XDA-Developers | Free userspace implementation: Samsung-RIL/libsamsung-ipc
| Wi-Fi         | BCM4329 | Linux kernel | Linux kernel support, proprietary loaded firmware
| Bluetooth     | BCM4329 | Linux kernel | Linux kernel support, proprietary loaded firmware
| GPS           | BCM4751 | https://plus.google.com/+StephenShankland/posts/CJ3bqa1x2Ek | Proprietary userspace, no free implementation: BCM4751
| Accelerometer | SMB380            | Android module | Linux kernel support, free userspace
| Compass       | MS3C              | Android module | Linux kernel support, free userspace
| Light         | Sharp GP2A        | Linux kernel support, free userspace | 
| Proximity     | Sharp GP2A        | Linux kernel support, free userspace | 
| FM Radio      | SI4709            | Linux kernel | Linux kernel support
| Camera (back) | NEC CE147         | Linux kernel support, free userspace | 
| Camera (front) | Samsung S5KA3DFX | Linux kernel support, free userspace | 
| Touchscreen   | Atmel MXT224 | Linux kernel support | 
| Display       | TL2796 | Linux kernel support | 

## Boot mode

First of all, in order to enter **flashing mode** you need to power up the phone holding volume-down and home.

## Serial && SBL

The first door to access a device in general is the serial, in our case Samsung
has decided to use the ``USB`` port for that via the ``FSA9280A`` chip, described
in the datasheet as "USB Port Multimedia Switch Featuring Automatic Select
and Accessory Detection"; in practice uses the value of resistance between the
pin ``ID`` and ``GND`` to enable a different internal subsystem.

In our case we want to access the UART and the bootloaders so we can use
a value of 619K as a resistor.

### PBL&SBL

It's possible to activate in this configuration ``SBoot`` pressing enter during boot;
take in mind that the new line is ``CR`` otherwise it doesn't work!

```
$ python -m serial.tools.miniterm /dev/ttyUSB0 115200
1
-----------------------------------------------------------
   Samsung Primitive Bootloader (PBL) v3.0
   Copyright (C) Samsung Electronics Co., Ltd. 2006-2010
-----------------------------------------------------------

+n1stVPN       2688
+nPgsPerBlk    64
PBL found bootable SBL: Partition(3).

Set cpu clk. from 400MHz to 800MHz.
OM=0x9, device=OnenandMux(Audi)
IROM e-fused - Non Secure Boot Version.

-----------------------------------------------------------
   Samsung Secondary Bootloader (SBL) v3.0
   Copyright (C) Samsung Electronics Co., Ltd. 2006-2010

   Board Name: ARIES REV 03
   Build On: Nov 25 2011 17:00:37
-----------------------------------------------------------

Re_partition: magic code(0xffffffff)
[PAM:   ] ++FSR_PAM_Init
[PAM:   ]   OneNAND physical base address       : 0xb0000000
[PAM:   ]   OneNAND virtual  base address       : 0xb0000000
[PAM:   ]   OneNAND nMID=0xec : nDID=0x50
[PAM:   ] --FSR_PAM_Init
fsr_bml_load_partition: pi->nNumOfPartEntry = 12
partitions loading success
board partition information update.. source: 0x0
.Done.
read 1 units.
==== PARTITION INFORMATION ====
 ID         : IBL+PBL (0x0)
 ATTR       : RO SLC (0x1002)
 FIRST_UNIT : 0
 NO_UNITS   : 1
===============================
 ID         : PIT (0x1)
 ATTR       : RO SLC (0x1002)
 FIRST_UNIT : 1
 NO_UNITS   : 1
===============================
 ID         : EFS (0x14)
 ATTR       : RW STL SLC (0x1101)
 FIRST_UNIT : 2
 NO_UNITS   : 40
===============================
 ID         : SBL (0x3)
 ATTR       : RO SLC (0x1002)
 FIRST_UNIT : 42
 NO_UNITS   : 5
===============================
 ID         : SBL2 (0x4)
 ATTR       : RO SLC (0x1002)
 FIRST_UNIT : 47
 NO_UNITS   : 5
===============================
 ID         : PARAM (0x15)
 ATTR       : RW STL SLC (0x1101)
 FIRST_UNIT : 52
 NO_UNITS   : 20
===============================
 ID         : KERNEL (0x6)
 ATTR       : RO SLC (0x1002)
 FIRST_UNIT : 72
 NO_UNITS   : 30
===============================
 ID         : RECOVERY (0x7)
 ATTR       : RO SLC (0x1002)
 FIRST_UNIT : 102
 NO_UNITS   : 30
===============================
 ID         : FACTORYFS (0x16)
 ATTR       : RW STL SLC (0x1101)
 FIRST_UNIT : 132
 NO_UNITS   : 1146
===============================
 ID         : DBDATAFS (0x17)
 ATTR       : RW STL SLC (0x1101)
 FIRST_UNIT : 1278
 NO_UNITS   : 536
===============================
 ID         : CACHE (0x18)
 ATTR       : RW STL SLC (0x1101)
 FIRST_UNIT : 1814
 NO_UNITS   : 140
===============================
 ID         : MODEM (0xb)
 ATTR       : RO SLC (0x1002)
 FIRST_UNIT : 1954
 NO_UNITS   : 50
===============================
loke_init: j4fs_open success..
load_lfs_parameters valid magic code and version.
load_debug_level reading debug level from file successfully(0x574f4c44).
init_fuel_gauge: vcell = 4080mV, soc = 89
reading nps status file is successfully!.
nps status=0x504d4f43
PMIC_IRQ1    = 0x30
PMIC_IRQ2    = 0x0
PMIC_IRQ3    = 0x0
PMIC_IRQ4    = 0x0
PMIC_STATUS1 = 0x40
PMIC_STATUS2 = 0x0
get_debug_level current debug level is 0x574f4c44.
aries_process_platform: Debug Level Low
keypad_scan: key value ----------------->= 0x0
CONFIG_ARIES_REV:48 , CONFIG_ARIES_REV03:48
aries_process_platform: final s1 booting mode = 0
DISPLAY_PATH_SEL[MDNIE 0x1]is on
MDNIE setting Init start!!
vsync interrupt is off
video interrupt is off
[fb0] turn on
MDNIE setting Init end!!

Autoboot (2 seconds) in progress, press any key to stop .

Autoboot aborted..
SBL>
SBL>
SBL> 
SBL> 
SBL>
SBL> help
Following commands are supported:
* setenv
* saveenv
* printenv
* help
* reset
* boot
* kernel
* format
* open
* close
* erasepart
* eraseall
* loadkernel
* showpart
* addpart
* delpart
* savepart
* nkernel
* nramdisk
* nandread
* nandwrite
* usb
* mmctest
* keyread
* usb_read
* usb_write
* fuelgauge
* pmic_read
* pmic_write
To get commands help, Type "help <command>"
SBL> printenv
PARAM Rev 1.3
SERIAL_SPEED : 7
LOAD_RAMDISK : 0
BOOT_DELAY : 0
LCD_LEVEL : 97
SWITCH_SEL : 1
PHONE_DEBUG_ON : 0
LCD_DIM_LEVEL : 0
LCD_DIM_TIME : 6
MELODY_MODE : 1
REBOOT_MODE : 0
NATION_SEL : 0
LANGUAGE_SEL : 0
SET_DEFAULT_PARAM : 0
PARAM_INT_13 : 0
PARAM_INT_14 : 0
VERSION : I9000XXIL
CMDLINE : console=ttySAC2,115200 loglevel=4
DELTA_LOCATION : /mnt/rsv
PARAM_STR_3 : 
PARAM_STR_4 : 
SBL> setenv SWITCH_SEL 6543
argv[0] : setenv
argv[1] : SWITCH_SEL
argv[2] : 6543
value : 6543
SBL> setenv PHONE_DEBUG_ON  1
argv[0] : setenv
argv[1] : PHONE_DEBUG_ON
argv[2] : 
argv[3] : 1
value : 0
SBL> saveenv
save param.blk, size: 5268
save param.blk successfully.
```

You have explicitely call ``loadkernel`` and ``boot`` to start the booting
process

```
SBL> loadkernel
FOTA Check Bit 
 Read BML page=, NumPgs=
FOTA Check Bit (0xffffffff)
Load Partion idx = (6)
..............................done
Kernel read success from kernel partition no.6, idx.6.
SBL> boot
setting param.serialnr=0x35346118 0x192600ec
setting param.board_rev=0x30
setting param.cmdline=console=ttySAC2,115200 loglevel=4

Starting kernel at 0x32000000...

Uncompressing Linux... done, booting the kernel.
<hit enter to activate fiq debugger>
```

## Kernel

The cool thing is that the kernel is supported in mainline
using the ``s5pv210`` configuration, so building it is
pretty simple

```
$ export CROSS_COMPILE=arm-linux-gnueabi-
$ export ARCH=arm
$ make s5pv210_defconfig
$ make -j 8 zImage s5pv210-galaxys.dtb
$ cat arch/arm/boot/zImage arch/arm/boot/dts/s5pv210-galaxys.dtb > arch/arm/boot/zImage_w_dtb
```

Obviously you need also the device tree configuration.
(I'm not completely sure if it's needed appending the device tree to the compressed image).

**Note:** you need the option ``rootwait`` otherwise it's possible that
the kernel panics (the error message indicates the wrong partition so
it's possible to lose hours trying to fix that ;)).

## Flashing

Now the problem is how can I "upload" the kernel just compiled? For this
family of devices Samsung has used a proprietary protocol and a tool
named **Odin**; it exists a open source reverse engineered version named
**Heimdall** that is possible to build using the following commands

```
$ git clone https://gitlab.com/BenjaminDobell/Heimdall && cd Heimdall
$ mkdir build && cd build
$ cmake ..
$ make -j8
```

| PIT | Description |
|-----|-------------|
| IBL+PBL | |
| PIT     |  | 
| EFS     |  modem data partition |
| SBL1    |  |
| SBL2    |  | 
| PARAM   |  | 
| KERNEL  |  boot partition |
| RECOVERY | recovery partition |
| FACTORYFS |  Android system partition |
| DBDATAFS | Android application data |
| CACHE   |  Android cache partition |
| MODEM   |  modem firmware partition 


## u-boot

It's possible to use a bootloader to ease the tinkering, in
particular exists a version of ``u-boot`` (this is the [repo](https://github.com/xc-racer99/u-boot-aries/wiki)).

You can build by yourself

```
$ git clone https://github.com/xc-racer99/u-boot-aries && cd u-boot-aries
$ export CROSS_COMPILE=arm-linux-gnueabi-
$ export ARCH=arm
$ make s5p_aries_defconfig
$ make -j 8
```

and flash it in the ``KERNEL`` partition

```
$ heimdall flash --KERNEL u-boot.bin
```

Usually it boots the option choosen at the last boot
but it's possible to access the menu pressing the ``Home``
button during power-up.

One of the way to upload a kernel is via fastboot

```
$ fastboot -b 0x32000000 -c "console=ttySAC2,115200 loglevel=4 earlyprintk root=/dev/ram0 mem=128M" boot zImage_w_dtb
```

If booting fails with ``undefined instruction`` could be

 - wrong load address
 - device tree not appended to the zImage


```
Aries # fatls mmc 0:1
            extlinux/
    30586   s5pv210-galaxys.dtb
  3681954   zImage-s5pv210-galaxys--5.2.32+git0+bb2776d6be_73b12de4c8-r0-s5pv210-20200329180843.dtb.bin
  3681954   zImage-s5pv210-galaxys-s5pv210.dtb.bin

3 file(s), 1 dir(s)

Aries # fatinfo
usage: fatinfo <interface> [<dev[:part]>]
Aries # fatinfo mmc 0
Interface:  MMC
  Device 0: Vendor: Man 000003 Snr 0483cb00 Rev: 0.2 Prod: SU08G
            Type: Removable Hard Disk
            Capacity: 7580.0 MB = 7.4 GB (15523840 x 512)
Filesystem: FAT16 "boot       "
Aries # fatload
fatload - load binary file from a dos filesystem

Usage:
fatload <interface> [<dev[:part]> [<addr> [<filename> [bytes [pos]]]]]
    - Load binary file 'filename' from 'dev' on 'interface'
      to address 'addr' from dos filesystem.
      'pos' gives the file position to start loading from.
      If 'pos' is omitted, 0 is used. 'pos' requires 'bytes'.
      'bytes' gives the size to load. If 'bytes' is 0 or omitted,
      the load stops on end of file.
      If either 'pos' or 'bytes' are not aligned to
      ARCH_DMA_MINALIGN then a misaligned buffer warning will
      be printed and performance will suffer for the load.
Aries # fatload mmc 0:1 0x32000000 zImage-s5pv210-galaxys-s5pv210.dtb.bin
3681954 bytes read in 710 ms (4.9 MiB/s)
Aries # help bootz
bootz - boot Linux zImage image from memory

Usage:
bootz [addr [initrd[:size]] [fdt]]
    - boot Linux zImage stored in memory
        The argument 'initrd' is optional and specifies the address
        of the initrd in memory. The optional argument ':size' allows
        specifying the size of RAW initrd.
        When booting a Linux kernel which requires a flat device-tree
        a third argument is required which is the address of the
        device-tree blob. To boot that kernel without an initrd image,
        use a '-' for the second argument. If you do not pass a third
        a bd_info struct will be passed instead

Aries # print bootargs
bootargs=console=${console} ${mtdparts} ubi.mtd=ubi;
Aries # print console
console=ttySAC2,115200n8
Aries # setenv bootargs 'root=/dev/mmcblk2p2 console=ttySAC2,115200n8 rootwait earlyprintk'
Aries # print bootargs
bootargs=root=/dev/mmcblk2p2 console=ttySAC2,115200n8 rootwait earlyprintk
Aries # bootz 0x32000000
Kernel image @ 0x32000000 [ 0x000000 - 0x37b728 ]

Starting kernel ...

```

## Linkography

 - [Cyanogenmod wiki page](https://web.archive.org/web/20161224193352/https://wiki.cyanogenmod.org/w/Galaxysmtd_Info)
 - [Semaphore kernel](https://github.com/stratosk/samsung-kernel-aries.git) source together with [ics ramdisk](https://github.com/stratosk/ics-ramdisk.git)
 - [Samsung Galaxy S Support With The Linux 4.19 Kernel](https://www.phoronix.com/scan.php?page=news_item&px=Samsung-Galaxy-S-DT-Linux-4.19)
 - Following the [eLinux](http://elinux.org/Toolchains#Linaro_.28ARM.29) info, we install ``gcc-arm-linux-gnueabi`` with the following entry for ``apt``
 - https://wiki.postmarketos.org/wiki/Deviceinfo_flash_methods
 - https://wiki.postmarketos.org/wiki/Samsung_Galaxy_S_(samsung-i9000)
 - [Self Made UART JIG and Debugging Connector for SGS I9000](https://www.xda-developers.com/self-made-uart-jig-and-debugging-connector-for-sgs-i9000/)
 - [Galaxy S UART JIG & Debugging Connector](https://forum.xda-developers.com/showthread.php?t=925034)
 - [Fun with resistors (home/car dock mode + more)](https://forum.xda-developers.com/showthread.php?t=820275)
 - [[GUIDE] USB Uart on Galaxy S devices [2012/09/25]](https://forum.xda-developers.com/showthread.php?t=1901376)
 - [UART Output / Bootloader Hacking / Kernel Debuging](https://forum.xda-developers.com/showthread.php?t=1209288)
 - [[GUIDE] Samsung Galaxy S7 UART](https://forum.xda-developers.com/galaxy-s7/how-to/guide-samsung-galaxy-s7-uart-t3743895)
 - [S-Boot](http://hexdetective.blogspot.com/2017/02/exploiting-android-s-boot-getting.html)
