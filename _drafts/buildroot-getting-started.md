---
layout: post
comments: true
title: "Build embedded systems with buildroot"
tags: [embedded, buildroot, linux]
---

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

You can connect to it using the redirection in the last line

```
$ ssh -p 2222 root@127.0.0.1 -o StrictHostKeyChecking=off
```

Remember to set

```
PermitRootLogin yes
PermitEmptyPassword yes
```

into ``/etc/ssh/sshd_config`` and restart the service with ``/etc/init.d/50sshd restart``.

http://nairobi-embedded.org/qemu_serial_port_system_console.html
