---
layout: post
comments: true
title: "Tips and tricks in debugging kernel drivers in Linux"
tags: [Linux, programming, debug, kernel, WIP]
---

This post includes a couple of notes about linux kernel debugging, in
particular the things that I keep forgetting.


## Navigation

If you are like me and use ``vim`` as a IDE you would like to have some
navigation functionality via ``ctags`` or ``cscope``: the linux kernel's
Makefile has some rules just for generating that

```
$ make tags ctags
```

## Log Levels

This is the most trivial thing and yet I forget it every single time

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

## Configuration

If you have an old config and you want to generate a new config having non pre-existing
configurations set to the default value you can issue a

```
$ make alldefconfig
```

If you don't want to use ``menuconfig`` is possible to set configuration options via command line using the following

```
$ ./scripts/config -e CONFIG_<your option>
```

Now some configuration values that can be useful when debugging

```
CONFIG_DEBUG_KERNEL:
  │
  │ Say Y here if you are developing drivers or trying to debug and
  │ identify kernel problems.
```

```
  │ CONFIG_DEBUG_INFO:
  │
  │ If you say Y here the resulting kernel image will include
  │ debugging info resulting in a larger kernel image.
  │ This adds debug symbols to the kernel and modules (gcc -g), and
  │ is needed if you intend to use kernel crashdump or binary object
  │ tools like crash, kgdb, LKCD, gdb, etc on the kernel.
  │ Say Y here only if you plan to debug the kernel.
```

```
  │ CONFIG_DEBUG_DRIVER:
  │
  │ Say Y here if you want the Driver core to produce a bunch of
  │ debug messages to the system log. Select this if you are having a
  │ problem with the driver core and want to see more of what is
  │ going on.
```

### GDB scripts

To help with debugging running systems it's possible to enable
some scripts to use with ``gdb``; this is possible with the
option

```
CONFIG_GDB_SCRIPTS
```

To load this script you need to enter in the kernel source tree
and start ``gdb``.

These are the available commands:

```
gef➤  apropos lx
function lx_current -- Return current task
function lx_module -- Find module by name and return the module variable
function lx_per_cpu -- Return per-cpu variable
function lx_task_by_pid -- Find Linux task by PID and return the task_struct variable
function lx_thread_info -- Calculate Linux thread_info from task variable
function lx_thread_info_by_pid -- Calculate Linux thread_info from task variable found by pid
lx-cmdline --  Report the Linux Commandline used in the current kernel
lx-cpus -- List CPU status arrays
lx-dmesg -- Print Linux kernel log buffer
lx-fdtdump -- Output Flattened Device Tree header and dump FDT blob to the filename
lx-iomem -- Identify the IO memory resource locations defined by the kernel
lx-ioports -- Identify the IO port resource locations defined by the kernel
lx-list-check -- Verify a list consistency
lx-lsmod -- List currently loaded modules
lx-mounts -- Report the VFS mounts of the current process namespace
lx-ps -- Dump Linux tasks
lx-symbols -- (Re-)load symbols of Linux kernel and currently loaded modules
lx-version --  Report the Linux Version of the current kernel
```

I think that are working correctly only after the system has completed
the initialization process.

### Dynamic debug

It's possible to have the debug messages enabled only when and where necessary:
[here the documentation](https://kernel.org/doc/html/v4.15/admin-guide/dynamic-debug-howto.html)

```
CONFIG_DYNAMIC_DEBUG:
  │
  │
  │ Compiles debug level messages into the kernel, which would not
  │ otherwise be available at runtime. These messages can then be
  │ enabled/disabled based on various levels of scope - per source file,
  │ function, module, format string, and line number. This mechanism
  │ implicitly compiles in all pr_debug() and dev_dbg() calls, which
  │ enlarges the kernel text size by about 2%.
  │
  │ If a source file is compiled with DEBUG flag set, any
  │ pr_debug() calls in it are enabled by default, but can be
  │ disabled at runtime as below.  Note that DEBUG flag is
  │ turned on by many CONFIG_*DEBUG* options.
   ...
  │   Depends on: PRINTK [=y] && DEBUG_FS [=y]
```

To control this feature is necessary to enable a pseudo
filesystem via the following option

```
CONFIG_DEBUG_FS:
    debugfs is a virtual file system that kernel developers use to put
    debugging files into.  Enable this option to be able to read and
    write to these files
```

that has to be mounted

```
# mount -t debugfs debugfs <debugfs>
$ cat <debugfs>/dynamic_debug/control
```

and can be used for example to enable all the debug messages
for drivers under ``sound/soc/``:

```
$ echo "file sound/soc/* +p" > /sys/kernel/debug/dynamic_debug/control
```

If you need something even before is possible to mount the debugfs, you can
use the ``dyndbg`` kernel argument at boot time, like ``dyndbg="<query>"``.

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



### Enable configuration option that is not selectable

If you build an external module that needs some options that
isn't selectable directly you can manually add a ``prompt`` line;
an example is ``VIDEOBUF_DMA_SG``

## Debugging

Take in mind that the kernel cannot be compiled without ``-O2`` so
optimization are a pain you have to live with (i.e. you can find
inlined function and optimized out variable when you are debugging
with ``gdb``).

If during debugging you find that doesn't make sense how 
the flow jumps here and there, probably some functions have been
inlined so try to single step instead of using the "next".

### Breakpoints

Setting breakpoints works as usual but obviously there are some particular
aspects of a operating system that you have to take into account, in particular
symbols; It's convenient to use the ``lx`` related functions to facilitate
debugging like in these examples

```
(gdb) br do_exit if $lx_current()->pid == 42
(gdb) br vfs_open if $_streq(path.dentry->d_iname, "test")
```

if you need to debug a kernel module, you cannot set a breakpoint directly (I'm not sure really)
but you can set a breakpoint to ``do_init_module()`` and then do whatever you want after you
trigger it via a modprobe of the module; remember to use ``lx-symbol`` to load automatically
the symbols

```
gef➤ lx-symbol /opt/r5u870/ /opt/r5u870/usbcam/
gef➤ b do_init_module
gef➤ c
Continuing.
 [meanwhile 'modprobe <module>' in the guest]
scanning for modules in /opt/r5u870/usbcam/
scanning for modules in /opt/r5u870/
scanning for modules in /hack/buildroot/output/build/linux-4.19.16
loading @0xffffffffc0000000: /opt/r5u870/usbcam//usbcam.ko

Breakpoint 1, do_init_module (mod=0xffffffffc000a440) at ./include/linux/slab.h:513
 ...
gef➤  print mod
$8 = (struct module *) 0xffffffffc000a440
gef➤  print mod->name
$9 = "usbcam", '\000' <repeats 49 times>
gef➤  print mod->core_layout.base
$7 = (void *) 0xffffffffc0000000 <usbcam_work_init>
gef➤  lx-lsmod 
Address            Module                  Size  Used by
0xffffffffc0000000 usbcam                0xd000  0x1
```

### Printk based debugging

Old but gold:

```
printk(KERN_ALERT "Debug: passed %s():%d\n", __FUNCTION__, __LINE__);
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

The Oops is what you probably find yourself staring at and is important
to remember that the crash happens at the ``RIP`` address, a lot of times
I'm distracted from the stacktrace; your usual Oops looks something like this

```
BUG: unable to handle kernel NULL pointer dereference at 0000000000000208
PGD 800000003dece067 P4D 800000003dece067 PUD 3ded0067 PMD 0
Oops: 0000 [#1] SMP PTI
CPU: 0 PID: 134 Comm: mpv/opener Tainted: G           O      4.19.16 #3
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.13.0-1 04/01/2014
RIP: 0010:dma_direct_map_sg+0x45/0xb0
 ...
```

You can use the ``scripts/decode_stacktrace.sh`` to obtain source information from an OOPS

```
$ cat /opt/r5u870/crash.log | ./scripts/decode_stacktrace.sh vmlinux . /opt/r5u870/usbcam/
```

or ``addr2line -e <kernel binary> <addr>``.

If you want to see the line in the code where the crash happened directly from
the debugger, ``list`` is your friend

```
gef➤  l *dma_direct_map_sg+0x45
0xffffffff8109c0f5 is in dma_direct_map_sg (./include/linux/dma-direct.h:42).
37       * and __dma_to_phys versions should only be used on non-encrypted memory for
38       * special occasions like DMA coherent buffers.
39       */
40      static inline dma_addr_t phys_to_dma(struct device *dev, phys_addr_t paddr)
41      {
42              return __sme_set(__phys_to_dma(dev, paddr));
43      }
44
45      static inline phys_addr_t dma_to_phys(struct device *dev, dma_addr_t daddr)
46      {
```

and in case the address you want to see is from a module

```
(gdb) list *<addr oops>
(gdb) add_symbol_file <path/to/the/module.ko> <base addr at runtime>
```

the base address at runtime can be read from ``/sys/modules/module name/sections/.text``
(``lx-symbol`` should do that for you but in case you have to work with an old kernel
knowing the general case can help).

## Qemu

It's possible to use ``qemu`` to debug the kernel take in mind some

 - use ``nokaslr`` to avoid randomization of the addresses
 - ``cd /path/to/linux/build/`` if you want to use the scripts from the kernel and
 - use ``add-auto-load-safe-path /path/to/linux/build/scripts/gdb/vmlinux-gdb.py`` in ``gdb``

To wait for the debugger to attach you can pass ``-s -S``.

### Forward USB devices to guest

It's possible to debug a physical USB device attached to the host
indicating the port it's attached to; here we see a webcam

```
$ lsusb -t
...
/:  Bus 02.Port 1: Dev 1, Class=root_hub, Driver=xhci_hcd/14p, 480M
    ...
    |__ Port 14: Dev 36, If 0, Class=Imaging, Driver=, 480M
/:  Bus 01.Port 1: Dev 1, Class=root_hub, Driver=ehci-pci/2p, 480M
...
```

and since we need an high speed device we are telling ``qemu`` to
use ``ehci``

```
-usb -device usb-ehci,id=ehci -device usb-host,hostport=14
```

## Miscellanea

```errno``` is defined in ``include/uapi/asm-generic/errno.h``

Under the directory named ``tools`` there a certain numbers of script useful to debug.

If you want to install the modules in another path use this

```
$ make INSTALL_MOD_PATH=/path/where/to/install/modules modules_install
```

## Links

 - https://opensourceforu.com/2011/01/understanding-a-kernel-oops/
 - http://mokosays.com/work/?p=22
 - http://henryhermawan.blogspot.com/2011/02/bigger-buffer-log-dmesg-size.html
 - https://www.kernel.org/doc/html/v4.14/dev-tools/gdb-kernel-debugging.html
 - https://developer.ibm.com/articles/l-kernel-memory-access/
 - https://d3s.mff.cuni.cz/files/teaching/nswi161/slides/06_debugging.pdf
 - https://www.starlab.io/using-gdb-linux-kernel/
 - https://sysprogs.com/VisualKernel/documentation/kernelsymbols
 - https://www.oreilly.com/library/view/linux-device-drivers/0596005903/ch04.html
 - http://www.makelinux.net/ldd3/
