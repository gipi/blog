---
layout: post
comments: true
title: "Reusing old shit: creating a BSP using Yocto for the Samsung Galaxy S (S5PV210)"
tags: [embedded, yocto]
---

In this post I'll describe my esperiments in reusing my old Samsung Galaxy S;
don't expected anything sophisticated, it's more a brain dump.

If you are interested exists a development board that should match the
specification of this cellphone: the [Mini210](http://www.friendlyarm.net/products/mini210).

## Specifications

Obviously there are a lot of components in a smartphone, like
the following (table copied from the [replicant's page](https://redmine.replicant.us/projects/replicant/wiki/GalaxySGTI9000)


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
a value of 619K as a resistor. The ``D-`` signal is ``TX`` and ``D+`` is ``RX``.

I tried to create a jig in order to make development a little easier, otherwise
I have to plug/unplug cables to switch from flashing to serial, risking damaging
the connector itself 

![]({{ site.baseurl }}/public/images/samsung-galaxy-s/usb_serial_mux.jpg)

the core is the ``TS3USB211`` chip that multiplexes between two high speed usb devices;
in my case one is a serial interface but doesn't matter.

### PBL&SBL

Now is possible to access the primary and secondary bootloaders' console;
pressing enter during the early boot activates a terminal for interacting with ``SBoot``;
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

However not all the peripherals are supported yet, if you want them you can use the following
``tree`` used by the developers as a staging point for all the changes that they want to upstream

 - https://github.com/xc-racer99/linux/tree/all-devices
 - https://github.com/PabloPL/linux

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

(be aware that compiles 32bit)

### PIT

The ``PIT``, as far as I understood it, is a kind of partition for the system as
seen by the bootloader and I don't know how much of it is translated for the
filesystem as seen by a running Linux system.

However these are a couple links for more information

 - [XDA - Investigation Into PIT Files](https://forum.xda-developers.com/showthread.php?t=816449)
 - [XDA - The reality of PIT files](https://forum.xda-developers.com/showthread.php?t=999097)
 - https://github.com/xc-racer99/android_kernel_samsung_aries/blob/aosp-7.1/drivers/mtd/onenand/samsung_gsm.h

The rough layout should be the following

| PIT | Description |
|-----|-------------|
| IBL+PBL | primary boot loader |
| PIT     |  | 
| EFS     | modem data partition |
| SBL1    | secondary boot loader |
| SBL2    | secondary boot loader backup | 
| PARAM   |  | 
| KERNEL  |  boot partition |
| RECOVERY | recovery partition (in practice backup kernel) |
| FACTORYFS |  Android system partition |
| DBDATAFS | Android application data |
| CACHE   |  Android cache partition |
| MODEM   |  modem firmware partition 

and it's possible to see the actual organization in the cellphone using
this one-liner

```
 ./heimdall/heimdall print-pit
 Heimdall v1.4.0

 Copyright (c) 2010-2013, Benjamin Dobell, Glass Echidna
 http://www.glassechidna.com.au/

 This software is provided free of charge. Copying and redistribution is
 encouraged.

 If you appreciate this software and you would like to support future
 development please consider donating:
 http://www.glassechidna.com.au/donate/

 Initialising connection...
 Detecting device...
 Claiming interface...
 Attempt failed. Detaching driver...
 Claiming interface again...
 Setting up interface...

 Initialising protocol...
 Protocol initialisation successful.

 Beginning session...

 Some devices may take up to 2 minutes to respond.
 Please be patient!

 Session begun.

 Downloading device's PIT file...
 PIT file download successful.

 Entry Count: 13
 Unknown 1: 1
 Unknown 2: 0
 Unknown 3: 7508
 Unknown 4: 65
 Unknown 5: 64224
 Unknown 6: 18
 Unknown 7: 55304
 Unknown 8: 67


 --- Entry #0 ---
 Binary Type: 0 (AP)
 Device Type: 0 (OneNAND)
 Identifier: 0
 Attributes: 0 (Read-Only)
 Update Attributes: 0
 Partition Block Size/Offset: 256
 Partition Block Count: 1
 File Offset (Obsolete): 6684783
 File Size (Obsolete): 2097268
 Partition Name: IBL+PBL
 Flash Filename: boot.bin
 FOTA Filename:


 --- Entry #1 ---
 Binary Type: 0 (AP)
 Device Type: 0 (OneNAND)
 Identifier: 1
 Attributes: 0 (Read-Only)
 Update Attributes: 0
 Partition Block Size/Offset: 256
 Partition Block Count: 1
 File Offset (Obsolete): 0
 File Size (Obsolete): 0
 Partition Name: PIT
 Flash Filename:
 FOTA Filename:


 --- Entry #2 ---
 Binary Type: 0 (AP)
 Device Type: 0 (OneNAND)
 Identifier: 20
 Attributes: 2 (STL Read-Only)
 Update Attributes: 0
 Partition Block Size/Offset: 256
 Partition Block Count: 40
 File Offset (Obsolete): 0
 File Size (Obsolete): 0
 Partition Name: EFS
 Flash Filename: efs.rfs
 FOTA Filename:


 --- Entry #3 ---
 Binary Type: 0 (AP)
 Device Type: 0 (OneNAND)
 Identifier: 3
 Attributes: 0 (Read-Only)
 Update Attributes: 0
 Partition Block Size/Offset: 256
 Partition Block Count: 5
 File Offset (Obsolete): 0
 File Size (Obsolete): 0
 Partition Name: SBL
 Flash Filename: sbl.bin
 FOTA Filename:


 --- Entry #4 ---
 Binary Type: 0 (AP)
 Device Type: 0 (OneNAND)
 Identifier: 4
 Attributes: 0 (Read-Only)
 Update Attributes: 0
 Partition Block Size/Offset: 256
 Partition Block Count: 5
 File Offset (Obsolete): 0
 File Size (Obsolete): 0
 Partition Name: SBL2
 Flash Filename: sbl.bin
 FOTA Filename:


 --- Entry #5 ---
 Binary Type: 0 (AP)
 Device Type: 0 (OneNAND)
 Identifier: 21
 Attributes: 2 (STL Read-Only)
 Update Attributes: 0
 Partition Block Size/Offset: 256
 Partition Block Count: 20
 File Offset (Obsolete): 0
 File Size (Obsolete): 0
 Partition Name: PARAM
 Flash Filename: param.lfs
 FOTA Filename:


 --- Entry #6 ---
 Binary Type: 0 (AP)
 Device Type: 0 (OneNAND)
 Identifier: 6
 Attributes: 0 (Read-Only)
 Update Attributes: 0
 Partition Block Size/Offset: 256
 Partition Block Count: 30
 File Offset (Obsolete): 0
 File Size (Obsolete): 0
 Partition Name: KERNEL
 Flash Filename: zImage
 FOTA Filename:


 --- Entry #7 ---
 Binary Type: 0 (AP)
 Device Type: 0 (OneNAND)
 Identifier: 7
 Attributes: 0 (Read-Only)
 Update Attributes: 0
 Partition Block Size/Offset: 256
 Partition Block Count: 30
 File Offset (Obsolete): 0
 File Size (Obsolete): 0
 Partition Name: RECOVERY
 Flash Filename: zImage
 FOTA Filename:


 --- Entry #8 ---
 Binary Type: 0 (AP)
 Device Type: 0 (OneNAND)
 Identifier: 22
 Attributes: 2 (STL Read-Only)
 Update Attributes: 0
 Partition Block Size/Offset: 256
 Partition Block Count: 1146
 File Offset (Obsolete): 0
 File Size (Obsolete): 0
 Partition Name: FACTORYFS
 Flash Filename: factoryfs.rfs
 FOTA Filename:


 --- Entry #9 ---
 Binary Type: 0 (AP)
 Device Type: 0 (OneNAND)
 Identifier: 23
 Attributes: 2 (STL Read-Only)
 Update Attributes: 0
 Partition Block Size/Offset: 256
 Partition Block Count: 536
 File Offset (Obsolete): 0
 File Size (Obsolete): 0
 Partition Name: DBDATAFS
 Flash Filename: dbdata.rfs
 FOTA Filename:


 --- Entry #10 ---
 Binary Type: 0 (AP)
 Device Type: 0 (OneNAND)
 Identifier: 24
 Attributes: 2 (STL Read-Only)
 Update Attributes: 0
 Partition Block Size/Offset: 256
 Partition Block Count: 140
 File Offset (Obsolete): 0
 File Size (Obsolete): 0
 Partition Name: CACHE
 Flash Filename: cache.rfs
 FOTA Filename:


 --- Entry #11 ---
 Binary Type: 0 (AP)
 Device Type: 0 (OneNAND)
 Identifier: 11
 Attributes: 0 (Read-Only)
 Update Attributes: 0
 Partition Block Size/Offset: 256
 Partition Block Count: 50
 File Offset (Obsolete): 0
 File Size (Obsolete): 0
 Partition Name: MODEM
 Flash Filename: modem.bin
 FOTA Filename:


 --- Entry #12 ---
 Binary Type: 1 (CP)
 Device Type: 1 (File/FAT)
 Identifier: 11
 Attributes: 0 (Read-Only)
 Update Attributes: 0
 Partition Block Size/Offset: 0
 Partition Block Count: 0
 File Offset (Obsolete): 0
 File Size (Obsolete): 0
 Partition Name:
 Flash Filename:
 FOTA Filename:

 Ending session...
 Rebooting device...
 Releasing device interface...
 Re-attaching kernel driver...
 ```

 - https://bootlin.com/blog/creating-flashing-ubi-ubifs-images/
 - https://elinux.org/UBIFS


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


Below a couple of possible commands to boot a system from sd card

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

## Proprietary firmwares

These are the binary blobs (and one configuration file) present
in the Android system

| Firmware name | Related chip | Related functionality|
|---------------|--------------|----------------------|
| fw_bcmdhd.bin       | Broadcom BCM4329 | Wi-Fi|
| fw_bcmdhd_apsta.bin | Broadcom BCM4329 | Wi-Fi host|
| nvram_net.txt       | Broadcom BCM4329 | Wi-Fi configuration|
| bcm4329.hcd         | Broadcom BCM4329 | Bluetooth|
| samsung_mfc_fw.bin  | Samsung S5PC110/S5PV210 MFC | Hardware media encoding/decoding|


but practically all of them are now available (still from broadcom) under
different names.

## Yocto

What I described above is a tedious process, involving bootloader and kernel but that
it's missing for example the root filesystem. To improve the process , I created a [yocto](https://www.yoctoproject.org/) layer
that you can find on github as [meta-s5pv210](https://github.com/gipi/meta-s5pv210).

With a simple

```
$ bitbake core-image-sato
```

you obtain an image named ``core-image-sato-s5pv210.wic`` to use for flashing an SD Card.

## Peripherals configuration

### I2C

The following option must be set otherwise  ``/dev/i2c-x`` is not present
and you cannot debug
```
CONFIG_I2C_CHARDEV
```

```
root@s5pv210:~# modprobe i2c-dev
i2c /dev entries driver
```

```
root@s5pv210:~# for x in $(find /sys/bus/i2c/devices/ ); do echo -en $x"\t";cat $x/name; done
/sys/bus/i2c/devices/   cat: can't open '/sys/bus/i2c/devices//name': No such file or directory
/sys/bus/i2c/devices/11-0044    gp2ap002a00f
/sys/bus/i2c/devices/i2c-13     i2c-gpio-2
/sys/bus/i2c/devices/6-0066     max8998
/sys/bus/i2c/devices/i2c-11     i2c-gpio-9
/sys/bus/i2c/devices/0-0062     s5ka3dfx
/sys/bus/i2c/devices/i2c-8      i2c-gpio-6
/sys/bus/i2c/devices/8-0010     si470x
/sys/bus/i2c/devices/5-0038     bma023
/sys/bus/i2c/devices/6-0006     dummy
/sys/bus/i2c/devices/12-002e    yas529
/sys/bus/i2c/devices/i2c-6      i2c-gpio-4
/sys/bus/i2c/devices/13-001a    wm8994
/sys/bus/i2c/devices/2-004a     maxtouch
/sys/bus/i2c/devices/10-0020    aries-touchkey
/sys/bus/i2c/devices/i2c-2      s3c2410-i2c
/sys/bus/i2c/devices/i2c-12     i2c-gpio-10
/sys/bus/i2c/devices/i2c-0      s3c2410-i2c
/sys/bus/i2c/devices/7-0025     fsa9480
/sys/bus/i2c/devices/0-003c     ce147
/sys/bus/i2c/devices/i2c-9      i2c-gpio-7
/sys/bus/i2c/devices/i2c-10     i2c-gpio-8
/sys/bus/i2c/devices/9-0036     max17040
/sys/bus/i2c/devices/i2c-7      i2c-gpio-5
/sys/bus/i2c/devices/i2c-5      i2c-gpio-3
```

```
root@s5pv210:~# i2cdetect -l
i2c-6   i2c             i2c-gpio-0                              I2C adapter
i2c-2   i2c             s3c2410-i2c                             I2C adapter
i2c-9   i2c             i2c-gpio-1                              I2C adapter
root@s5pv210:~# i2cdetect 2
WARNING! This program can confuse your I2C bus, cause data loss and worse!
I will probe file /dev/i2c-2.
I will probe address range 0x03-0x77.
Continue? [Y/n] 
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- UU -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --
root@s5pv210:~# i2cdetect 6
WARNING! This program can confuse your I2C bus, cause data loss and worse!
I will probe file /dev/i2c-6.
I will probe address range 0x03-0x77.
Continue? [Y/n] 
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- UU -- -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- UU -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --
root@s5pv210:~# i2cdetect 9
WARNING! This program can confuse your I2C bus, cause data loss and worse!
I will probe file /dev/i2c-9.
I will probe address range 0x03-0x77.
Continue? [Y/n] 
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- UU -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --
```

### Video

The device has two cameras (front and back); the front one is a ``s5ka3dfx`` sensor
that can be enabled via ``CONFIG_VIDEO_S5KA3DFX``.

```
root@s5pv210:~# dmesg | grep video
videodev: Linux video capture interface: v2.00
s5p-jpeg fb600000.jpeg-codec: encoder device registered as /dev/video0
s5p-jpeg fb600000.jpeg-codec: decoder device registered as /dev/video1
s5p-mfc f1700000.codec: decoder registered as /dev/video2
s5p-mfc f1700000.codec: encoder registered as /dev/video3
s5p-fimc-md: Registered fimc.0.m2m as /dev/video4
s5p-fimc-md: Registered fimc.0.capture as /dev/video5
s5p-fimc-md: Registered fimc.1.m2m as /dev/video6
s5p-fimc-md: Registered fimc.1.capture as /dev/video7
s5p-fimc-md: Registered fimc.2.m2m as /dev/video8
s5p-fimc-md: Registered fimc.2.capture as /dev/video9
root@s5pv210:~# media-ctl -p
Media controller API version 5.3.8

Media device information
------------------------
driver          s5p-fimc-md
model           SAMSUNG S5P FIMC
serial
bus info
hw revision     0x0
driver version  5.3.8

Device topology
- entity 1: FIMC.0 (3 pads, 3 links)
            type V4L2 subdev subtype Unknown flags 0
            device node name /dev/v4l-subdev0
        pad0: Sink
                [fmt:YUYV8_2X8/640x480 colorspace:jpeg
                 crop.bounds:(0,0)/0x0
                 crop:(0,0)/640x480
                 compose.bounds:(0,0)/640x480
                 compose:(0,0)/640x480]
                <- "S5KA3DFX 0-0062":0 []
                <- "CE147 0-003c":0 [ENABLED]
        pad1: Sink
                [fmt:YUV10_1X30/640x480 colorspace:jpeg
                 crop.bounds:(0,0)/0x0
                 crop:(0,0)/640x480
                 compose.bounds:(0,0)/640x480
                 compose:(0,0)/640x480]
        pad2: Source
                [fmt:YUYV8_2X8/640x480 colorspace:jpeg]
                -> "fimc.0.capture":0 [ENABLED,IMMUTABLE]

- entity 5: fimc.0.capture (1 pad, 1 link)
            type Node subtype V4L flags 0
            device node name /dev/video3
        pad0: Sink
                <- "FIMC.0":2 [ENABLED,IMMUTABLE]

- entity 9: FIMC.1 (3 pads, 3 links)
            type V4L2 subdev subtype Unknown flags 0
            device node name /dev/v4l-subdev1
        pad0: Sink
                [fmt:YUYV8_2X8/640x480 colorspace:jpeg
                 crop.bounds:(0,0)/0x0
                 crop:(0,0)/640x480
                 compose.bounds:(0,0)/640x480
                 compose:(0,0)/640x480]
                <- "S5KA3DFX 0-0062":0 [ENABLED]
                <- "CE147 0-003c":0 []
        pad1: Sink
                [fmt:YUV10_1X30/640x480 colorspace:jpeg
                 crop.bounds:(0,0)/0x0
                 crop:(0,0)/640x480
                 compose.bounds:(0,0)/640x480
                 compose:(0,0)/640x480]
        pad2: Source
                [fmt:YUYV8_2X8/640x480 colorspace:jpeg]
                -> "fimc.1.capture":0 [ENABLED,IMMUTABLE]

- entity 13: fimc.1.capture (1 pad, 1 link)
             type Node subtype V4L flags 0
             device node name /dev/video6
        pad0: Sink
                <- "FIMC.1":2 [ENABLED,IMMUTABLE]

- entity 17: FIMC.2 (3 pads, 3 links)
             type V4L2 subdev subtype Unknown flags 0
             device node name /dev/v4l-subdev2
        pad0: Sink
                [fmt:YUYV8_2X8/640x480 colorspace:jpeg
                 crop.bounds:(0,0)/0x0
                 crop:(0,0)/640x480
                 compose.bounds:(0,0)/640x480
                 compose:(0,0)/640x480]
                <- "S5KA3DFX 0-0062":0 []
                <- "CE147 0-003c":0 []
        pad1: Sink
                [fmt:YUV10_1X30/640x480 colorspace:jpeg
                 crop.bounds:(0,0)/0x0
                 crop:(0,0)/640x480
                 compose.bounds:(0,0)/640x480
                 compose:(0,0)/640x480]
        pad2: Source
                [fmt:YUYV8_2X8/640x480 colorspace:jpeg]
                -> "fimc.2.capture":0 [ENABLED,IMMUTABLE]

- entity 21: fimc.2.capture (1 pad, 1 link)
             type Node subtype V4L flags 0
             device node name /dev/video9
        pad0: Sink
                <- "FIMC.2":2 [ENABLED,IMMUTABLE]

- entity 25: S5KA3DFX 0-0062 (1 pad, 3 links)
             type V4L2 subdev subtype Sensor flags 0
             device node name /dev/v4l-subdev3
        pad0: Source
                [fmt:YUYV8_2X8/640x480 field:none colorspace:jpeg]
                -> "FIMC.0":0 []
                -> "FIMC.1":0 [ENABLED]
                -> "FIMC.2":0 []

- entity 27: CE147 0-003c (1 pad, 3 links)
             type V4L2 subdev subtype Sensor flags 0
             device node name /dev/v4l-subdev4
        pad0: Source
                [fmt:YUYV8_2X8/640x480@1/30 field:none colorspace:jpeg]
                -> "FIMC.0":0 [ENABLED]
                -> "FIMC.1":0 []
                -> "FIMC.2":0 []


root@s5pv210:~# media-ctl --print-dot
digraph board {
        rankdir=TB
        n00000001 [label="{ {<port0> 0 | <port1> 1} | FIMC.0\n/dev/v4l-subdev0 | {<port2> 2} }", shape=Mrecord, style=filled, fillcolor=green]
        n00000001:port2 -> n00000005 [style=bold]
        n00000005 [label="fimc.0.capture\n/dev/video3", shape=box, style=filled, fillcolor=yellow]
        n00000009 [label="{ {<port0> 0 | <port1> 1} | FIMC.1\n/dev/v4l-subdev1 | {<port2> 2} }", shape=Mrecord, style=filled, fillcolor=green]
        n00000009:port2 -> n0000000d [style=bold]
        n0000000d [label="fimc.1.capture\n/dev/video6", shape=box, style=filled, fillcolor=yellow]
        n00000011 [label="{ {<port0> 0 | <port1> 1} | FIMC.2\n/dev/v4l-subdev2 | {<port2> 2} }", shape=Mrecord, style=filled, fillcolor=green]
        n00000011:port2 -> n00000015 [style=bold]
        n00000015 [label="fimc.2.capture\n/dev/video9", shape=box, style=filled, fillcolor=yellow]
        n00000019 [label="{ {} | S5KA3DFX 0-0062\n/dev/v4l-subdev3 | {<port0> 0}}", shape=Mrecord, style=filled, fillcolor=green]
        n00000019:port0 -> n00000001:port0 [style=dashed]
        n00000019:port0 -> n00000009:port0
        n00000019:port0 -> n00000011:port0 [style=dashed]
        n0000001b [label="{ {} | CE147 0-003c\n/dev/v4l-subdev4 | {<port0> 0}}", shape=Mrecord, style=filled, fillcolor=green]
        n0000001b:port0 -> n00000001:port0
        n0000001b:port0 -> n00000009:port0 [style=dashed]
        n0000001b:port0 -> n00000011:port0 [style=dashed]
}
root@s5pv210:~# v4l2-ctl --list-devices
__fimc_pipeline_open(): No sensor subdev
__fimc_pipeline_close(): No sensor subdev
Silicon Labs Si470x FM Radio Re ():
        /dev/radio0

s5p-mfc-dec (platform:f1700000.codec):
        /dev/video5
        /dev/video7

exynos4-fimc (platform:fb200000.fimc):
        /dev/video2
        /dev/video3

exynos4-fimc (platform:fb300000.fimc):
        /dev/video4
        /dev/video6

exynos4-fimc (platform:fb400000.fimc):
        /dev/video8
        /dev/video9

s5p-jpeg encoder (platform:fb600000.jpeg-codec):
        /dev/video0
        /dev/video1
```

 - https://github.com/xc-racer99/linux/commit/fb2767a8e845e6f7e38da68f31adc0bcdde82ffb
 - https://gitmemory.com/issue/PabloPL/linux/30/498365930

```
root@s5pv210:~# DISPLAY=:0.0 gst-launch-1.0 videotestsrc ! timeoverlay font-desc=60px ! ximagesink
```

 - [S5KA3DFX](http://www.zhopper.narod.ru/mobile/s5ka3dfx_full.pdf)
 - [Camera on Galaxy S3](https://blog.forkwhiletrue.me/posts/camera-on-galaxy-s3/)
 - [R-Car/Tests:rcar-vin](https://elinux.org/R-Car/Tests:rcar-vin) how to test the VIN and CSI-2 functionality

## Connectivity

First of all you need ``rfkill`` enabled with ``CONFIG_RFKILL``

```
root@s5pv210:~# rfkill
ID TYPE      DEVICE    SOFT      HARD
 0 bluetooth hci0   blocked unblocked
 1 wlan      phy0   blocked unblocked
root@s5pv210:~# rfkill unblock 0
root@s5pv210:~# rfkill unblock 1
root@s5pv210:~# rfkill
ID TYPE      DEVICE      SOFT      HARD
 0 bluetooth hci0   unblocked unblocked
 1 wlan      phy0   unblocked unblocked
```

### Wifi

```
root@s5pv210:~# ip link
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
2: sit0@NONE: <NOARP> mtu 1480 qdisc noop state DOWN mode DEFAULT group default qlen 1000
    link/sit 0.0.0.0 brd 0.0.0.0
3: wlan0: <NO-CARRIER,BROADCAST,MULTICAST,DYNAMIC,UP> mtu 1500 qdisc pfifo_fast state DOWN mode DORMANT group default qlen 1000
    link/ether xx:xx:xx:xx:xx:xx brd ff:ff:ff:ff:ff:ff
```

```
root@s5pv210:~# iw dev wlan0 scan
BSS xx:xx:xx:xx:xx:xx(on wlan0)
        last seen: 378.381s [boottime]
        TSF: 0 usec (0d, 00:00:00)
        freq: 2412
        beacon interval: 100 TUs
        capability: ESS Privacy ShortSlotTime RadioMeasure (0x1411)
        signal: -44.00 dBm
        last seen: 0 ms ago
        SSID: kebab
        Supported rates: 1.0* 2.0* 5.5* 11.0* 18.0 24.0 36.0 54.0
        DS Parameter set: channel 1
        ERP: <no flags>
        Extended supported rates: 6.0 9.0 12.0 48.0
        RSN:     * Version: 1
                 * Group cipher: CCMP
                 * Pairwise ciphers: CCMP
                 * Authentication suites: PSK
                 * Capabilities: 16-PTKSA-RC 1-GTKSA-RC (0x000c)
        BSS Load:
                 * station count: 0
                 * channel utilisation: 50/255
                 * available admission capacity: 0 [*32us]
        HT capabilities:
                Capabilities: 0x82c
                        HT20
                        SM Power Save disabled
                        RX HT20 SGI
                        No RX STBC
                        Max AMSDU length: 7935 bytes
                        No DSSS/CCK HT40
                Maximum RX AMPDU length 65535 bytes (exponent: 0x003)
                Minimum RX AMPDU time spacing: 8 usec (0x06)
                HT RX MCS rate indexes supported: 0-15
                HT TX MCS rate indexes are undefined
        HT operation:
                 * primary channel: 1
                 * secondary channel offset: no secondary
                 * STA channel width: 20 MHz
                 * RIFS: 1
                 * HT protection: no
                 * non-GF present: 0
                 * OBSS non-GF present: 0
                 * dual beacon: 0
                 * dual CTS protection: 0
                 * STBC beacon: 0
                 * L-SIG TXOP Prot: 0
                 * PCO active: 0
                 * PCO phase: 0
        Overlapping BSS scan params:
                 * passive dwell: 20 TUs
                 * active dwell: 10 TUs
                 * channel width trigger scan interval: 300 s
                 * scan passive total per channel: 200 TUs
                 * scan active total per channel: 20 TUs
                 * BSS width channel transition delay factor: 5
                 * OBSS Scan Activity Threshold: 0.25 %
        Extended capabilities:
                 * HT Information Exchange Supported
                 * Extended Channel Switching
                 * BSS Transition
                 * Operating Mode Notification
        WPS:     * Version: 1.0
                 * Wi-Fi Protected Setup State: 2 (Configured)
                 * AP setup locked: 0x01
                 * Response Type: 3 (AP)
                 * UUID: 6254a7cc-097f-5b2c-b024-07fdf89096a8
                 * Manufacturer: Technicolor
                 * Model: AGHP
                 * Model Number: 4132
                 * Serial Number: 1918SA5NM
                 * Primary Device Type: 6-0050f204-1
                 * Device name: DGA4132
                 * Config methods: Label, PBC, Keypad
                 * RF Bands: 0x3
                 * Unknown TLV (0x1049, 6 bytes): 00 37 2a 00 01 20
        WMM:     * Parameter version 1
                 * BE: CW 15-1023, AIFSN 3
                 * BK: CW 15-1023, AIFSN 7
                 * VI: CW 7-15, AIFSN 2, TXOP 3008 usec
                 * VO: CW 3-7, AIFSN 2, TXOP 1504 usec
BSS yy:yy:yy:yy:yy:yy(on wlan0)
 ...
```

```
root@s5pv210:~# wpa_passphrase <ESSID> <password>
network={
      ssid="testing"
      #psk="testingPassword"
      psk=131e1e221f6e06e3911a2d11ff2fac9182665c004de85300f9cac208a6a80531
}
root@s5pv210:~# wpa_supplicant -i wlan0 -c /etc/wpa_supplicant.conf -B
root@s5pv210:~# udhcpc -i wlan0
```

## Audio

```
root@s5pv210:~# arecord -l
**** List of CAPTURE Hardware Devices ****
card 0: Aries [Aries], device 0: HiFi wm8994-aif1-0 [HiFi wm8994-aif1-0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
root@s5pv210:~# aplay -l
**** List of PLAYBACK Hardware Devices ****
card 0: Aries [Aries], device 0: HiFi wm8994-aif1-0 [HiFi wm8994-aif1-0]
  Subdevices: 1/1
  Subdevice #0: subdevice #0
root@s5pv210:~# aplay -L
null
    Discard all samples (playback) or generate zero samples (capture)
pulse
    PulseAudio Sound Server
default
    Default ALSA Output (currently PulseAudio Sound Server)
sysdefault:CARD=Aries
    Aries, HiFi wm8994-aif1-0
    Default Audio Device
```

```
root@s5pv210:~# arecord -f S16_LE -d 10 -r 16000 --device="hw:0,0" /tmp/test-mic.wav
Recording WAVE '/tmp/test-mic.wav' : Signed 16 bit Little Endian, Rate 16000 Hz, Mono
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
 - [[A][SGS2][Serial] How to talk to the Modem with AT commands](https://forum.xda-developers.com/galaxy-s2/help/how-to-talk-to-modem-commands-t1471241)
 - https://redmine.replicant.us/projects/replicant/wiki/ExynosModemIsolation
 - https://forum.xda-developers.com/wiki/Samsung_Galaxy_S/GT-I9000
 - https://redmine.replicant.us/projects/replicant/wiki/GalaxySI9000LoadedFirmwares
 - https://bootlin.com/blog/creating-flashing-ubi-ubifs-images/
 - https://wiki.dave.eu/index.php/Memory_Tecnology_Device_(MTD)
 - https://bootlin.com/blog/managing-flash-storage-with-linux/
 - linux-mtd.infradead.org
 - https://forum.xda-developers.com/showthread.php?t=1699506
