---
layout: post
comments: true
title: "Nexus 5 and the quest for the kernel"
tags: [kernel,linux,git,embedded]
---

Since I own an old [Nexus5](https://en.wikipedia.org/wiki/Nexus_5) (a great smartphone by the way) that is now unsupported
I decided to take a look on how update the system on it.

This device's hardware components are

 - [Qualcomm Snapdragon](https://en.wikipedia.org/wiki/Qualcomm_Snapdragon) SoC
  (listed as ``msm8974`` in the kernel source code) composed of an ``ARMv7`` cpu
  named [Krait](https://en.wikipedia.org/wiki/Krait_(CPU)) that isn't a
  Cortex-A15 :P
 - [bq24190](http://www.ti.com/lit/pdf/slusaw5) charger and OTG


I'm lucky enough that the linux kernel [seems](https://www.phoronix.com/scan.php?page=news_item&px=Linux-4.9-ARM-Pull)
to support this cellphone from version 4.9.

With a simple git magic I see that a lot of stuff seems supported

```
$ git log --oneline  -- arch/arm/boot/dts/qcom-msm8974-lge-nexus5-hammerhead.dts
231cb93c06ac ARM: dts: qcom: msm8974-hammerhead: add support for bluetooth
489bacb29818 ARM: dts: qcom: msm8974-hammerhead: add support for display
030b6d48ebfb ARM: dts: qcom: msm8974-hammerhead: add support for backlight
48100d10c93f ARM: dts: qcom: msm8974-hammerhead: add touchscreen support
fb143fcbb9ad ARM: dts: qcom: msm8974-hammerhead: add USB OTG support
ec4c6c57af57 ARM: dts: qcom: msm8974-hammerhead: add WiFi support
0567022c019a ARM: dts: qcom: msm8974-hammerhead: correct gpios property on magnetometer
bd9392507588 ARM: dts: qcom: msm8974-hammerhead: add device tree bindings for ALS / proximity
fe8d81fe7d9a ARM: dts: qcom: msm8974-hammerhead: add device tree bindings for mpu6515
03864e57770a ARM: dts: qcom: msm8974-hammerhead: increase load on l20 for sdhci
b24413180f56 License cleanup: add SPDX GPL-2.0 license identifier to files with no license
a511e97c495f ARM: dts: qcom: msm8974-hammerhead: Add sdhci1 node
f7af7de89fd5 ARM: dts: msm8974-hammerhead: Introduce gpio-keys nodes
b8066645f6c1 ARM: dts: msm8974-hammerhead: Add regulator nodes for hammerhead
b1100d8c31a9 ARM: dts: qcom: Add initial DTS for LG Nexus 5 Phone
```

But before starting to build it I need to introduce you to some aspects that
will help with the procedure.

## UART

The ``UART`` is accessible from the audio jack: the jack to use is the one having 4 poles with the following signals (starting from the tip):

 - left (``TX``) yellow
 - right (``RX``) orange
 - ``GND`` black
 - ``MIC`` red

The last one is the signal that allows to activate the serial console with a voltage level of 3.3 volts;
**be sure that has the correct voltage otherwise you risk to burn the device**.
In my experience I didn't check the ``UART`` adapter and I was feeding with 5v
obtaining a mal functioning display.

## Fastboot

You can enter in fastboot mode pressing volume-up, volume-down and power
simultaneously, the following is the output from the serial:

```
welcome to hammerhead bootloader
[10] Power on reason 80
[10] DDR: elpida
[100] Loaded IMGDATA at 0x11000000
[110] Display Init: Start
[190] MDP GDSC already enabled
[190] bpp 24
[230] Config MIPI_CMD_PANEL.
[230] display panel: ORISE
[230] display panel: Default setting
[360] Turn on MIPI_CMD_PANEL.
[410] Display Init: Done
[410] cable type from shared memory: 8
[410] vibe
[610] USB init ept @ 0xf96b000
[630] secured device: 1
[630] fastboot_init()
[680] splash: fastboot_op
 FASTBOOT MODE
 PRODUCT_NAME - hammerhead
 VARIANT - hammerhead D821(E) 16GB
 HW VERSION - reserved
 BOOTLOADER VERSION - HHZ12d
 BASEBAND VERSION - M8974A-2.0.50.2.30
 CARRIER INFO - None
 SERIAL NUMBER - 07b31aed0337d580
 SIGNING - production
 SECURE BOOT - enabled
 LOCK STATE - unlocked
[790] splash: start
[1820] Fastboot mode started
[1820] udc_start()
```

**Note:** Usually entering fastboot mode would show the tipical image of the
android "opened" for repair but with the serial attached the display won't show anything! When you use the volume buttons
to move between options these are printed in the console.

From the host computer this will appear in ``dmesg`` output

```
[1266973.240241] usb 2-5: new high-speed USB device number 67 using xhci_hcd
[1266973.395309] usb 2-5: New USB device found, idVendor=18d1, idProduct=4ee0, bcdDevice= 1.00
[1266973.395317] usb 2-5: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[1266973.395320] usb 2-5: Product: Android
[1266973.395323] usb 2-5: Manufacturer: Google
[1266973.395326] usb 2-5: SerialNumber: 07b31aed0337d580
```

and you can connect with ``fastboot``

```
$ fastboot devices -l
07b31aed0337d580       fastboot usb:2-5
```

## Building and packing the kernel image

You need the ``mkbootimg`` tool installed and a cross compiler for ``ARM``
architecture. Let's start building the kernel:

```
$ make mrproper
$ export ARCH=arm
$ export CROSS_COMPILE=arm-linux-gnueabi-
$ make qcom_defconfig
$ make -j 8
```

With the kernel is necessary to have the correct device tree, that in out case
is located at ``arch/arm/boot/dts/qcom-msm8974-lge-nexus5-hammerhead.dtb``; you
need to concatenate it together with the kernel

```
$ cat arch/arm/boot/zImage arch/arm/boot/dts/qcom-msm8974-lge-nexus5-hammerhead.dtb > zImage_w_dtb
```

Finally you need to craft a particular format understood by fastboot

```
$ mkbootimg \
    --base 0 \
    --pagesize 2048 \
    --kernel_offset 0x00008000 \
    --ramdisk_offset 0x02900000 \
    --second_offset 0x00f00000 \
    --tags_offset 0x02700000 \
    --cmdline 'console=tty0 console=ttyMSM0,115200,n8 androidboot.hardware=hammerhead debug earlyprintk user_debug=31 maxcpus=2 msm_watchdog_v2.enable=1' \
    --kernel zImage_w_dtb \
    --ramdisk /hack/buildroot/output/images/rootfs.cpio.gz \
    -o boot.img
```

**Note:** the device path for the serial is ``ttyMSM0`` instead of ``ttyHSL0``
as indicated in the Android's kernel!

## Booting

A correct boot looks like this

```
welcome to hammerhead bootloader
[10] Power on reason 91
[10] DDR: elpida
[110] Loaded IMGDATA at 0x11000000
[110] Display Init: Start
[190] MDP GDSC already enabled
[190] bpp 24
[230] Config MIPI_CMD_PANEL.
[230] display panel: ORISE
[280] Found Appeneded Flattened Device tree
[280] DTB: Use the first DTB (not found proper DTB)
[320] Set panel ON cmds [35]
[440] Turn on MIPI_CMD_PANEL.
[490] Display Init: Done
[490] cable type from shared memory: 8
[490] reboot_mode restart reason = reboot_by_key
[540] vibe
[640] splash: boot
[680] splash: unlocked
[720] use_signed_kernel=0, is_unlocked=1, is_tampered=1.
[720] Loading boot image (9373696): start
[1050] Loading boot image (9373696): done
[1060] Found Appeneded Flattened Device tree
[1060] DTB: Use the first DTB (not found proper DTB)
[1070] get_display_kcal = 0, 0, 0, x
```

## Playing

```
# fdisk -l /dev/mmcblk1
Found valid GPT with protective MBR; using GPT

Disk /dev/mmcblk1: 30777344 sectors, 2740M
Logical sector size: 512
Disk identifier (GUID): 98101b32-bbe2-4bf2-a06e-2bb33d000c20
Partition table holds up to 32 entries
First usable sector is 34, last usable sector is 30777310

Number  Start (sector)    End (sector)  Size Name
     1            1024          132095 64.0M modem
     2          132096          134143 1024K sbl1
     3          134144          135167  512K rpm
     4          135168          136191  512K tz
     5          136192          137215  512K sdi
     6          137216          138239  512K aboot
     7          138240          142335 2048K pad
     8          142336          144383 1024K sbl1b
     9          144384          145407  512K tzb
    10          145408          146431  512K rpmb
    11          146432          147455  512K abootb
    12          147456          153599 3072K modemst1
    13          153600          159743 3072K modemst2
    14          159744          160767  512K metadata
    15          160768          193535 16.0M misc
    16          193536          226303 16.0M persist
    17          226304          232447 3072K imgdata
    18          232448          277503 22.0M laf
    19          277504          322559 22.0M boot
    20          322560          367615 22.0M recovery
    21          367616          373759 3072K fsg
    22          373760          374783  512K fsc
    23          374784          375807  512K ssd
    24          375808          376831  512K DDR
    25          376832         2473983 1024M system
    26         2473984         2535423 30.0M crypto
    27         2535424         3969023  700M cache
    28         3969024        30777299 12.7G userdata
    29        30777300        30777310  5632 grow
```

```
# echo 0 > /sys/class/backlight/lcd-backlight/brightness
```

## Links

 - [Building and booting Nexus 5 kernel](https://web.archive.org/web/20190430060717/http://marcin.jabrzyk.eu:80/posts/2014/05/building-and-booting-nexus-5-kernel)
 - [masneyb/nexus-5-upstream](https://github.com/masneyb/nexus-5-upstream) current development efforts to port the upstream Linux Kernel to the LG Nexus 5
 - [A better audio jack console cable for Google Nexus devices](http://www.pabr.org/consolejack/consolejack.en.html)
 - [Repo](https://android.googlesource.com/device/google/debugcable) for the audio debug cable
 - Google's headset [specification](https://source.android.com/devices/accessories/headset/specification.html)
 - [Ifixit's teardown](https://it.ifixit.com/Teardown/Nexus+5+Teardown/19016)
 - [eLinux's fastboot documentation](https://elinux.org/Android_Fastboot)
