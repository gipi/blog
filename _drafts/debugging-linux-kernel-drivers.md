---
layout: post
comments: true
title: "Tips and tricks in debugging kernel drivers in Linux"
tags: [Linux, programming, debug]
---

First of all

```
$ make alldefconfig
$ make tags ctags
```

```errno``` is defined in ``include/uapi/asm-generic/errno.h``

```
DEBUG_KERNEL
CONFIG_DEBUG_INFO=y
CONFIG_DEBUG_DRIVER
CONFIG_DYNAMIC_DEBUG
CONFIG_GDB_SCRIPTS
```

```
$ ./scripts/config -e CONFIG_DEBUG_INFO
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

```
loglevel=       All Kernel Messages with a loglevel smaller than the
                    console loglevel will be printed to the console. It can
                    also be changed with klogd or other programs. The
                    loglevels are defined as follows:

                    0 (KERN_EMERG)          system is unusable
                    1 (KERN_ALERT)          action must be taken immediately
                    2 (KERN_CRIT)           critical conditions
                    3 (KERN_ERR)            error conditions
                    4 (KERN_WARNING)        warning conditions
                    5 (KERN_NOTICE)         normal but significant condition
                    6 (KERN_INFO)           informational
                    7 (KERN_DEBUG)          debug-level messages
```

```
/*
 * Print out info about fatal segfaults, if the show_unhandled_signals
 * sysctl is set:
 */
static inline void
show_signal_msg(struct pt_regs *regs, unsigned long error_code,
		unsigned long address, struct task_struct *tsk)
{
	...
	printk("%s%s[%d]: segfault at %lx ip %p sp %p error %lx",
		task_pid_nr(tsk) > 1 ? KERN_INFO : KERN_EMERG,
		tsk->comm, task_pid_nr(tsk), address,
		(void *)regs->ip, (void *)regs->sp, error_code);
	...
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
 - https://www.kernel.org/doc/html/v4.14/dev-tools/gdb-kernel-debugging.html
 - https://developer.ibm.com/articles/l-kernel-memory-access/
