<!--
.. title: Yocto: using U-Boot as bootloader with a RaspberryPi Zero
.. slug: u-boot-rpi0
.. date: 2018-10-28 00:00:00
.. tags: embedded,rpi,u-boot,WIP
.. category: 
.. link: 
.. description: 
.. type: text
-->


This is a guide about building and configuring a Yocto build for a raspberry pi zero with u-boot.

<!-- TEASER_END -->

## Yocto and Repo

You can obtain an out-of-the-box configured Yocto tree using a manifest in
the following way

```
$ mkdir rpi-yocto && cd rpi-yocto
$ repo init -u https://github.com/gipi/rpi0-repo -b sumo
$ repo sync
$ source sources/oe-init-build-env build/
$ bitbake rpi-basic-image
$ sudo dd if=tmp/deploy/images/raspberrypi0/rpi-basic-image-raspberrypi0.rpi-sdimg of=/dev/sdd
$ bitbake rpi-basic-image -c populate_sdk
```

This way of configuring a project composed of multiple git repositories is inspired of the
way Android works: there is manifest (i.e. a simple ``XML`` file) containing the description
of the repository with the specific revision and path that is needed to checkout in order
to have a correctly configured project. In my case I created a manifest with the minimal
layers in order to boot up a raspberry pi zero with ``U-Boot`` and configured to enable
the debugging via ``JTAG``.

In the rest of the post I try to summarize how this is done.

## U-Boot

``U-Boot`` is a bootloader, i.e. a program that is used to setup the essential peripherals
(like RAM and flash) and to load the intended kernel with the correct parameters.

In order to use it with ``meta-raspberry`` you need only to set in ``local.conf``
the following

```
RPI_USE_U_BOOT = "1"
```

Since I want to save the manual procedure for future use, what follows is the
explanation for the configuration, if you use the layer indicated above all this
is unecessary.

### Boot sequence

The raspberry pi, in particular the Broadcom chip, follows this
sequence to bootup

 - **stage 1:** is the on-chip ROM, loads stage2 in the L2 cache
 - **stage 2:** is ``bootcode.bin``. Enable SDRAM and loads stage 3
 - **stage 3:** is ``loader.bin``. It loads ``start.elf``
 - ``start.elf`` loads ``kernel.img``

``kernel.img`` is usually the linux kernel, we want to substitute it with ``u-boot``.
This is achievable renaming accordingly the file or changing the right variable (named ``kernel``)
in the ``config.txt`` file. ``cmdline.txt`` instead contains the arguments for the kernel.

``cmdline.txt``

```
dwc_otg.lpm_enable=0 console=serial0,115200 root=/dev/mmcblk0p2 rootfstype=ext4 rootwait console=tty0
```

The complicated thing that happens with this device is that the ``start.elf`` prepare
already the ``fdt`` (**flat device tree**) at a specific address and doesn't need to be loaded from the
SD card. The address is passed as environment variable in ``u-boot``.

Take in mind that some document uses ``fdt_addr_r`` instead of the mainline's ``fdt_addr``.

### Configuration

If you don't have already ``u-boot`` compiled you can use Yocto via these variables

```
PREFERRED_PROVIDER_virtual/bootloader = "u-boot"

KERNEL_IMAGETYPE = "zImage"
KERNEL_BOOTCMD = "bootz"
```

The command to boot are indicated in 

``boot.cmd`` that is obtained compiling ``boot.scr``

```
fdt addr ${fdt_addr} && fdt get value bootargs /chosen bootargs
fatload mmc 0:1 ${kernel_addr_r} zImage
bootz ${kernel_addr_r} - ${fdt_addr}
```

## GPIOs

For future use I want to set the pins needed to use ``JTAG`` with the board.

The chip of the raspberry pi has 54 pins configurable via 41 32-bit registers; the start
address is different between board models, for a pi zero is ``0x7e200000`` but to use
it directly to modify the registers is a pain in the ass.

There are several options to go with to set the desired pins, each one needs (but the first one)
a recent version of the firmware (you can see the version of your system using ``vcgencmd version``)

 - create a device driver and move the pins using it
 - ``dt-blob.bin``
 - ``config.txt`` and its ``gpio`` variable

The simplest way (with a modern firmware) is to use the last option: in my case I can
add directly in the ``config.txt`` the following lines

```
gpio=22-27=a4
```

or using the layer ``meta-raspberrypi`` you can set it via the ``RPI_EXTRA_CONFIG``
variable in your ``local.conf``.

In order to check if all is ok you can use the ``wiringpi`` library and in particular
the ``gpio`` program in the running system:

```
root@raspberrypi0:~# gpio readall
 +-----+-----+---------+------+---+-Pi Zero--+---+------+---------+-----+-----+
 | BCM | wPi |   Name  | Mode | V | Physical | V | Mode | Name    | wPi | BCM |
 +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
 |     |     |    3.3v |      |   |  1 || 2  |   |      | 5v      |     |     |
 |   2 |   8 |   SDA.1 |   IN | 1 |  3 || 4  |   |      | 5v      |     |     |
 |   3 |   9 |   SCL.1 |   IN | 1 |  5 || 6  |   |      | 0v      |     |     |
 |   4 |   7 | GPIO. 7 |   IN | 1 |  7 || 8  | 1 | ALT0 | TxD     | 15  | 14  |
 |     |     |      0v |      |   |  9 || 10 | 1 | ALT0 | RxD     | 16  | 15  |
 |  17 |   0 | GPIO. 0 |   IN | 0 | 11 || 12 | 0 | IN   | GPIO. 1 | 1   | 18  |
 |  27 |   2 | GPIO. 2 | ALT4 | 0 | 13 || 14 |   |      | 0v      |     |     |
 |  22 |   3 | GPIO. 3 |   IN | 0 | 15 || 16 | 0 | IN   | GPIO. 4 | 4   | 23  |
 |     |     |    3.3v |      |   | 17 || 18 | 0 | ALT4 | GPIO. 5 | 5   | 24  |
 |  10 |  12 |    MOSI |   IN | 0 | 19 || 20 |   |      | 0v      |     |     |
 |   9 |  13 |    MISO |   IN | 0 | 21 || 22 | 0 | ALT4 | GPIO. 6 | 6   | 25  |
 |  11 |  14 |    SCLK |   IN | 0 | 23 || 24 | 1 | IN   | CE0     | 10  | 8   |
 |     |     |      0v |      |   | 25 || 26 | 1 | IN   | CE1     | 11  | 7   |
 |   0 |  30 |   SDA.0 |   IN | 1 | 27 || 28 | 1 | IN   | SCL.0   | 31  | 1   |
 |   5 |  21 | GPIO.21 |   IN | 1 | 29 || 30 |   |      | 0v      |     |     |
 |   6 |  22 | GPIO.22 |   IN | 1 | 31 || 32 | 0 | IN   | GPIO.26 | 26  | 12  |
 |  13 |  23 | GPIO.23 |   IN | 0 | 33 || 34 |   |      | 0v      |     |     |
 |  19 |  24 | GPIO.24 |   IN | 0 | 35 || 36 | 0 | IN   | GPIO.27 | 27  | 16  |
 |  26 |  25 | GPIO.25 | ALT4 | 0 | 37 || 38 | 0 | IN   | GPIO.28 | 28  | 20  |
 |     |     |      0v |      |   | 39 || 40 | 0 | IN   | GPIO.29 | 29  | 21  |
 +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
 | BCM | wPi |   Name  | Mode | V | Physical | V | Mode | Name    | wPi | BCM |
 +-----+-----+---------+------+---+-Pi Zero--+---+------+---------+-----+-----+
```

How you can see the configuration is correct.

## Links

 - [RPi Boot flow](https://www.raspberrypi.org/documentation/hardware/raspberrypi/bootmodes/bootflow.md)
 - [DEVICE TREES, OVERLAYS, AND PARAMETERS](https://www.raspberrypi.org/documentation/configuration/device-tree.md)
 - [Zero Client: Boot kernel and root filesystem from network with a Raspberry Pi2 or Pi3](https://michaelfranzl.com/2017/03/21/zero-client-boot-kernel-root-filesystem-network-raspberry-pi2-pi3/)
 - https://www.denx.de/wiki/view/DULG/UBootEnvVariables
 - https://www.denx.de/wiki/DULG/UBootCmdFDT
 - https://elinux.org/RPi_U-Boot#Test_U-Boot
 - https://dius.com.au/2015/08/19/raspberry-pi-uboot/
 - https://bootlin.com/blog/dt-overlay-uboot-libfdt/
 - https://www.raspberrypi.org/documentation/configuration/config-txt/gpio.md
 - https://www.raspberrypi.org/documentation/configuration/pin-configuration.md
 - https://www.mjoldfield.com/atelier/2017/03/rpi-devicetree.html
 - https://pinout.xyz/pinout/jtag
 - https://www.suse.com/c/debugging-raspberry-pi-3-with-jtag/
 - https://sysprogs.com/VisualKernel/tutorials/raspberry/jtagsetup/
 - https://media.readthedocs.org/pdf/meta-raspberrypi/latest/meta-raspberrypi.pdf
 - https://github.com/FrankBau/raspi-repo-manifest/wiki
 - https://www.yoctoproject.org/docs/2.4.2/dev-manual/dev-manual.html#creating-partitioned-images-using-wic
 - https://www.yoctoproject.org/docs/2.4.2/dev-manual/dev-manual.html#flashing-images-using-bmaptool
 - https://www.raspberrypi.org/documentation/hardware/raspberrypi/schematics/rpi_SCH_Zero_1p3_reduced.pdf
 - https://cdn.sparkfun.com/assets/learn_tutorials/6/7/6/PiZero_1.pdf
 - https://elinux.org/RPI_vcgencmd_usage
 - https://www.raspberrypi.org/app/uploads/2012/02/BCM2835-ARM-Peripherals.pdf
 - http://www.pieter-jan.com/node/15

[post](http://www.jumpnowtek.com/rpi/Raspberry-Pi-Systems-with-Yocto.html)
if you want to use Yocto to build all from scratch.
