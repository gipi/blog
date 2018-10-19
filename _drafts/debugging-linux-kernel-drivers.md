---
layout: post
comments: true
title: "Tips and tricks in debugging kernel drivers in Linux"
tags: [Linux, programming, debug]
---

```errno``` is defined in ``include/uapi/asm-generic/errno.h``

```
DEBUG_KERNEL
CONFIG_DEBUG_INFO=y
CONFIG_DEBUG_DRIVER
CONFIG_DYNAMIC_DEBUG
```

Under the directory named ``tools`` there a certain numbers of script useful to debug.

To see ``dev_dbg`` or you set ``debug`` from the kernel command line or you do a think
like the following

```
#define DEBUG

// some stuff
#include <linux/device.h>
```
To use ``pr_debug`` you can abilitate it with

```
CFLAGS_<filename>.o = -DDEBUG
```
```
$ cat <debugfs>/dynamic_debug/control
$ echo "file sound/soc/* +p" > /sys/kernel/debug/dynamic_debug/control
```

but at boot time you can use ```dyndbg="<query>"```

```
printk(KERN_ALERT "Debug: passed %s():%d\n", __FUNCTION__, __LINE__);
```

```
$ make INSTALL_MOD_PATH=/path/where/to/install/modules modules_install
```

## OOPS

You can use the ``scripts/decode_stacktrace.sh`` to obtain information from an OOPS or
``addr2line -e <kernel binary> <addr>``

```
(gdb) list *<addr oops>
(gdb) add_symbol_file <path/to/the/module.ko> <addr at runtime>
```

the address can be read from ``/sys/modules/<name>/sections/.text

## Links

 - https://opensourceforu.com/2011/01/understanding-a-kernel-oops/
 - http://mokosays.com/work/?p=22
 - http://henryhermawan.blogspot.com/2011/02/bigger-buffer-log-dmesg-size.html
