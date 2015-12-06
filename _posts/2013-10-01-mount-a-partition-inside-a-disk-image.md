---
layout: post
title: 'Mount a partition inside a disk image'
comments: true
---
This little trick can help you if retrieve contents from a dumped image is needed: let's suppose we have a file named ``dump.img`` obtained by ``dd if=/dev/sdd of=dump.img``

After that you can mount it using a **loop device**, but in order to access a partition you need to indicate an offset (otherwise the ``mount`` command will refuse to mount it) that can be read from the output of the ``parted`` command:

```
 # parted dump.img -s unit b print
 Model:  (file)
 Disk /home/gipi/dump.img: 4022337024B
 Sector size (logical/physical): 512B/512B
 Partition Table: msdos
 
 Number  Start        End          Size         Type     File system  Flags
  1      1048576B     1050673151B  1049624576B  primary  fat32        boot
  2      1050673152B  4021288959B  2970615808B  primary
```
We are interested in the second partition, so the number to use is 1050673152:

    # losetup --offset 1050673152  -f dump.img

In order to know the loop device to pass as argument to ``mount``, ``losetup`` has a ``--all`` option

```
 # losetup --all
 /dev/loop0: [0823]:6685472 (/home/gipi/dump.img)
```

So finally we can mount the partition with

    # mount /dev/loop0 /mnt/dump/
