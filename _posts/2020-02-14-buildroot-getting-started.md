---
layout: post
comments: true
title: "Build embedded systems with buildroot"
tags: [embedded, buildroot, Linux, WIP]
---

[Buildroot](https://buildroot.org/) is an integration system used to obtain complete bootable
embedded systems; it uses a KConfig configuration mechanism (the ``menuconfig`` thing).

This post is a simple way for me to take notes about it, refer to the [official documentation](https://buildroot.org/docs.html)
for anything serious.

## Source

First of all you need to download the source code with ``git``

```
$ git clone git://git.buildroot.net/buildroot
```

and then enter in the new created directory. 

## Configuration

Now it's possible to configure
the system you want to build; if you want to try first a system already
configured you can use one of the existing ``*_defconfig``

```
$ find ./configs -name '*_defconfig'
./configs/qemu_microblazebe_mmu_defconfig
./configs/mx6udoo_defconfig
./configs/ci20_defconfig
./configs/orangepi_prime_defconfig
./configs/nanopi_m1_defconfig
./configs/qemu_mips64_malta_defconfig
./configs/qemu_nios2_10m50_defconfig
./configs/imx6-sabresd_qt5_defconfig
./configs/beagleboardx15_defconfig
./configs/at91sam9rlek_defconfig
 ...
./configs/nanopi_m1_plus_defconfig
./configs/at91sam9260eknf_defconfig
./configs/stm32f469_disco_defconfig
./configs/atmel_sama5d3_xplained_mmc_defconfig
./configs/qemu_arm_versatile_nommu_defconfig
./configs/freescale_imx6dlsabresd_defconfig
./configs/raspberrypi3_qt5we_defconfig
./configs/snps_archs38_vdk_defconfig
```

For example I want to create a test ``x86_64`` system to use with ``QEmu``,
so I use ``qemu_x86_64_defconfig``.

```
$ make qemu_x86_64_defconfig
```

## Building

```
$ make -j8
```

All the created files are in ``output``; in our example the files we care about are in ``output/images/``:
in this case a ``bzImage`` and a root filesystem ``rootfs.ext2``; what remains to do is to launch
``qemu`` with the right options:

```
$ qemu-system-x86_64 \
    -hda output/images/rootfs.ext2 \
    -m 1024 \
    -enable-kvm \
    -kernel linux_image/boot/vmlinuz-3.2.0-23-generic \
    -append 'root=/dev/sda' \
    -net nic,model=virtio -net user,hostfwd=tcp::2222-:22
```

During the package compiling process, Buildroot will record the compiling
process via some identification files and save those files to the related
directory of the package. All those identification files are:

```
.stamp_configured
.stamp_downloaded
.stamp_extracted
.stamp_patched
.stamp_staging_installed
.stamp_target_installe
```

These identification files mainly control the download, decompression,
packaging, configuration, compilation, installation, etc. of this package.

Read ``docs/manual/rebuilding-packages.txt`` for more informations (seriously, read it,
it's full of information).

## Cheat sheet

### Save configuration

You can set the file where to save the configuration

```
Build options ---->
   (configs/whatever_defconfig) Location to save buildroot config
```

and once exited from ``menuconfig`` you can do

```
$ make savedefconfig
```

### Save kernel configuration

```
Kernel --->
    (board/vendor/linux.config) Configuration file path
```

### Packages

For each package is available a set of commands

```
  <pkg>                  - Build and install <pkg> and all its dependencies
  <pkg>-source           - Only download the source files for <pkg>
  <pkg>-extract          - Extract <pkg> sources
  <pkg>-patch            - Apply patches to <pkg>
  <pkg>-depends          - Build <pkg>'s dependencies
  <pkg>-configure        - Build <pkg> up to the configure step
  <pkg>-build            - Build <pkg> up to the build step
  <pkg>-graph-depends    - Generate a graph of <pkg>'s dependencies
  <pkg>-dirclean         - Remove <pkg> build directory
  <pkg>-reconfigure      - Restart the build from the configure step
  <pkg>-rebuild          - Restart the build from the build step
```

### Force rebuild target

```
$ rm -rf output/target
$ find output/ -name ".stamp_target_installed" |xargs rm -rf
```

### Enable keymap

Enable package ``kbd`` in order to use ``loadkeys`` and the correct
localization for your keyboard

```
  │     -> Target packages
  │       -> Hardware handling
                kbd
```

### Enable ssh

You can connect to it using the redirection in the last line

```
    -net nic,model=virtio -net user,hostfwd=tcp::2222-:22
```

```
$ ssh -p 2222 root@127.0.0.1 -o StrictHostKeyChecking=off
```

Remember to set

```
PermitRootLogin yes
PermitEmptyPassword yes
```

into ``/etc/ssh/sshd_config`` and restart the service with ``/etc/init.d/50sshd restart``.

Bad enough, with qemu is happened that the machine hangs at boot probably during the ``ssh-keygen``,
maybe you can use ``CONFIG_RANDOM_TRUST_CPU`` or something indicated [here](https://wiki.debian.org/BoottimeEntropyStarvation)
or [here](https://daniel-lange.com/archives/152-Openssh-taking-minutes-to-become-available,-booting-takes-half-an-hour-...-because-your-server-waits-for-a-few-bytes-of-randomness.html)
or maybe, hit the keyboard a couple times or
maybe [rng-tools](https://unix.stackexchange.com/questions/442698/when-i-log-in-it-hangs-until-crng-init-done).

In some cases it's possible that ``sshd`` doesn't start because the keys are
not present, in such case is possible to do

```
$ ssh-keygen -A -f output/target/ # generate the keys
$ make                            # rebuild the filesystem
```

### Enable X11

This is tricky: for now I was able to make work only the modular
X server with a configuration like the following:

```
BR2_PACKAGE_XAPP_TWM=y
BR2_PACKAGE_XAPP_XCALC=y
BR2_PACKAGE_XAPP_XCLOCK=y
BR2_PACKAGE_XAPP_XEYES=y
BR2_PACKAGE_XAPP_XINIT=y
BR2_PACKAGE_XDRIVER_XF86_INPUT_KEYBOARD=y
BR2_PACKAGE_XDRIVER_XF86_INPUT_MOUSE=y
BR2_PACKAGE_XDRIVER_XF86_VIDEO_CIRRUS=y
BR2_PACKAGE_XDRIVER_XF86_VIDEO_FBDEV=y
BR2_PACKAGE_XDRIVER_XF86_VIDEO_VESA=y
BR2_PACKAGE_XORG7=y
BR2_PACKAGE_XSERVER_XORG_SERVER=y
BR2_PACKAGE_XTERM=y
BR2_TOOLCHAIN_BUILDROOT_CXX=y
BR2_TOOLCHAIN_BUILDROOT_WCHAR=y
BR2_USE_WCHAR=y
```

### Customize filesystem

If you need to add, remove or whatever to the final image, you can indicate
a post build script, take for example ``pc_x86_64_bios_defconfig``

```
BR2_ROOTFS_POST_BUILD_SCRIPT="board/pc/post-build.sh"
```

```bash
#!/bin/sh

set -e

BOARD_DIR=$(dirname "$0")

# Detect boot strategy, EFI or BIOS
if [ -f "$BINARIES_DIR/efi-part/startup.nsh" ]; then
    cp -f "$BOARD_DIR/grub-efi.cfg" "$BINARIES_DIR/efi-part/EFI/BOOT/grub.cfg"
else
    cp -f "$BOARD_DIR/grub-bios.cfg" "$TARGET_DIR/boot/grub/grub.cfg"

    # Copy grub 1st stage to binaries, required for genimage
    cp -f "$HOST_DIR/lib/grub/i386-pc/boot.img" "$BINARIES_DIR"
fi
```

### Linux kernel

If you want to configure it

```
$ make linux-menuconfig
```

and then

```
$ make linux
```

to build it.

### Build out-of-tree modules

This is as usual

```
$ cd /path/to/module/code/
$ make KDIR=/path/to/buildroot/output/build/linux-x.y.z/ M=$PWD
```

## Linkography

 - [Official documentation](https://buildroot.org/docs.html)
 - http://nairobi-embedded.org/qemu_serial_port_system_console.html
 - https://www.viatech.com/en/2015/06/buildroot/
 - https://elinux.org/images/2/2a/Using-buildroot-real-project.pdf
 - http://www.linux-kvm.org/page/USB_Host_Device_Assigned_to_Guest
 - https://stackoverflow.com/questions/31617575/how-to-use-usb-camera-in-qemu
 - https://stackoverflow.com/questions/47320800/how-to-clean-only-target-in-buildroot
 - https://techfortalk.co.uk/2017/06/15/how-to-addcompile-a-kernel-module-as-a-new-buildroot-package/
 - http://wiki.t-firefly.com/en/Firefly-PX3-SE/buildroot_introduction.html
 - https://unix.stackexchange.com/questions/70931/how-to-install-x11-on-my-own-linux-buildroot-system
 - https://www.kraxel.org/blog/2019/09/display-devices-in-qemu/
