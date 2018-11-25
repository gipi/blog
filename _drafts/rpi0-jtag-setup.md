---
layout: post
comments: true
title: "Setup JTAG debugging on a Raspberry Pi zero using J-Link"
---

## JTAG

You can use a J-Link debugger

```
adapter_khz 1000
adapter_nsrst_delay 400
reset_config none
 
if { [info exists CHIPNAME] } {
set _CHIPNAME $CHIPNAME
} else {
set _CHIPNAME rspi
}
 
if { [info exists CPU_TAPID ] } {
set _CPU_TAPID $CPU_TAPID
} else {
set _CPU_TAPID 0x07b7617F
}
 
jtag newtap $_CHIPNAME arm -irlen 5 -expected-id $_CPU_TAPID
 
set _TARGETNAME $_CHIPNAME.arm
target create $_TARGETNAME arm11 -chain-position $_TARGETNAME
rspi.arm configure -event gdb-attach { halt }

```

```
$ openocd -f interface/jlink.cfg -f rpi.conf
Open On-Chip Debugger 0.10.0
Licensed under GNU GPL v2
For bug reports, read
	http://openocd.org/doc/doxygen/bugs.html
adapter speed: 1000 kHz
adapter_nsrst_delay: 400
none separate
Info : auto-selecting first available session transport "jtag". To override use 'transport select <transport>'.
Info : No device selected, using first device.
Info : J-Link ARM V8 compiled Nov 28 2014 13:44:46
Info : Hardware version: 8.00
Info : VTarget = 3.313 V
Info : clock speed 1000 kHz
Info : JTAG tap: rspi.arm tap/device found: 0x07b7617f (mfg: 0x0bf (Broadcom), part: 0x7b76, ver: 0x0)
Info : found ARM1176
Info : rspi.arm: hardware has 6 breakpoints, 2 watchpoints
```

```
$ telnet localhost 4444
Trying ::1...
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
Open On-Chip Debugger
> halt
target halted in ARM state due to debug-request, current mode: Supervisor
cpsr: 0x60000093 pc: 0xc001e0d4
> targets
    TargetName         Type       Endian TapName            State
--  ------------------ ---------- ------ ------------------ ------------
 0* rspi.arm           arm11      little rspi.arm           halted
> reg
===== ARM registers
(0) r0 (/32): 0xDA428F80 (dirty)
(1) r1 (/32): 0x00000000
(2) r2 (/32): 0xFFFFFFFF
(3) r3 (/32): 0x00000000
(4) r4 (/32): 0xFFFFE000
(5) r5 (/32): 0x00000000
(6) r6 (/32): 0xC09430A4
(7) r7 (/32): 0xC09CB6EE
(8) r8 (/32): 0x00000001
(9) r9 (/32): 0xC07A0CF0
(10) r10 (/32): 0xC091CA28
(11) r11 (/32): 0xC0941F4C
(12) r12 (/32): 0xC0941F50
(13) sp_usr (/32)
(14) lr_usr (/32)
(15) pc (/32): 0xC001E0D4
(16) r8_fiq (/32)
(17) r9_fiq (/32)
(18) r10_fiq (/32)
(19) r11_fiq (/32)
(20) r12_fiq (/32)
(21) sp_fiq (/32)
(22) lr_fiq (/32)
(23) sp_irq (/32)
(24) lr_irq (/32)
(25) sp_svc (/32): 0xC0941F40
(26) lr_svc (/32): 0xC0010848
(27) sp_abt (/32)
(28) lr_abt (/32)
(29) sp_und (/32)
(30) lr_und (/32)
(31) cpsr (/32): 0x60000093
(32) spsr_fiq (/32)
(33) spsr_irq (/32)
(34) spsr_svc (/32)
(35) spsr_abt (/32)
(36) spsr_und (/32)
(37) sp (/32)
(38) lr (/32)
(39) sp_mon (/32)
(40) lr_mon (/32)
(41) spsr_mon (/32)
```

```
$ gdb-multiarch -q tmp/work/raspberrypi0-poky-linux-gnueabi/linux-raspberrypi/1_4.14.68+gitAUTOINC+8c8666ff6c-r0/linux-raspberrypi0-standard-build/vmlinux 
GEF for linux ready, type `gef' to start, `gef config' to configure
51 commands loaded for GDB 7.12.0.20161007-git using Python engine 3.6
[*] 5 commands could not be loaded, run `gef missing` to know why.
Reading symbols from tmp/work/raspberrypi0-poky-linux-gnueabi/linux-raspberrypi/1_4.14.68+gitAUTOINC+8c8666ff6c-r0/linux-raspberrypi0-standard-build/vmlinux...(no debugging symbols found)...done.
gef➤  target remote :3333
Remote debugging using :3333
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────[ registers ]────
$r0   : 0xda428f80  →  0xc07a07a0  →  0x00757063  →  0xb3e90d42  →  0xaaaaaaaa  →  0x55555555  →  0xaaaaaaaa  →  [loop detected]
$r1   : 0x00000000  →  0xe3a00000  →  0xaaaaaaaa  →  0x55555555  →  0xaaaaaaaa  →  [loop detected]
$r2   : 0xffffffff
$r3   : 0x00000000  →  0xe3a00000  →  0xaaaaaaaa  →  0x55555555  →  0xaaaaaaaa  →  [loop detected]
$r4   : 0xffffe000  →  0xaaaaaaaa  →  0x55555555  →  0xaaaaaaaa  →  [loop detected]
$r5   : 0x00000000  →  0xe3a00000  →  0xaaaaaaaa  →  0x55555555  →  0xaaaaaaaa  →  [loop detected]
$r6   : 0xc09430a4  →  0x00000000  →  0xe3a00000  →  0xaaaaaaaa  →  0x55555555  →  0xaaaaaaaa  →  [loop detected]
$r7   : 0xc09cb6ee  →  0x00000000  →  0xe3a00000  →  0xaaaaaaaa  →  0x55555555  →  0xaaaaaaaa  →  [loop detected]
$r8   : 0x00000001  →  0x04e3a000  →  0x55555555  →  0xaaaaaaaa  →  0x55555555  →  [loop detected]
$r9   : 0xc07a0cf0  →  0x7273752f  →  0x55555555  →  0xaaaaaaaa  →  0x55555555  →  [loop detected]
$r10  : 0xc091ca28  →  0x00000000  →  0xe3a00000  →  0xaaaaaaaa  →  0x55555555  →  0xaaaaaaaa  →  [loop detected]
$r11  : 0xc0941f4c  →  0xc001081c  →  0xe52de004  →  0xaaaaaaaa  →  0x55555555  →  0xaaaaaaaa  →  [loop detected]
$r12  : 0xc0941f50  →  0xc0941f84  →  0xc005447c  →  0xe52de004  →  0xaaaaaaaa  →  0x55555555  →  0xaaaaaaaa  →  [loop detected]
$sp   : 0xc0941f40  →  0xc0941f5c  →  0xc0650fc0  →  0xe52de004  →  0xaaaaaaaa  →  0x55555555  →  0xaaaaaaaa  →  [loop detected]
$lr   : 0xc0010848  →  0xeafffffa  →  0x55555555  →  0xaaaaaaaa  →  0x55555555  →  [loop detected]
$pc   : 0xc001e0d4  →  0xe1a00000  →  0xaaaaaaaa  →  0x55555555  →  0xaaaaaaaa  →  [loop detected]
$cpsr : [negative ZERO CARRY overflow INTERRUPT fast thumb]
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────[ stack ]────
0xc0941f40│+0x00: 0xc0941f5c  →  0xc0650fc0  →  0xe52de004  →  0xaaaaaaaa  →  0x55555555  →  0xaaaaaaaa  →  [loop detected]	 ← $sp
0xc0941f44│+0x04: 0xc0941f50  →  0xc0941f84  →  0xc005447c  →  0xe52de004  →  0xaaaaaaaa  →  0x55555555  →  0xaaaaaaaa
0xc0941f48│+0x08: 0xc0650fe8  →  0xebe9d84c  →  0xaaaaaaaa  →  0x55555555  →  0xaaaaaaaa  →  [loop detected]
0xc0941f4c│+0x0c: 0xc001081c  →  0xe52de004  →  0xaaaaaaaa  →  0x55555555  →  0xaaaaaaaa  →  [loop detected]	 ← $r11
0xc0941f50│+0x10: 0xc0941f84  →  0xc005447c  →  0xe52de004  →  0xaaaaaaaa  →  0x55555555  →  0xaaaaaaaa  →  [loop detected]	 ← $r12
0xc0941f54│+0x14: 0xc0941f60  →  0xc094be90  →  0x00000002  →  0x1004e3a0  →  0x55555555  →  0xaaaaaaaa  →  0x55555555
0xc0941f58│+0x18: 0xc0054508  →  0xe10f3000  →  0x1a2ef611  →  0x005bd580  →  0x03a02000  →  0xaaaaaaaa  →  0x55555555
0xc0941f5c│+0x1c: 0xc0650fc0  →  0xe52de004  →  0xaaaaaaaa  →  0x55555555  →  0xaaaaaaaa  →  [loop detected]
───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────[ code:arm ]────
   0xc001e0bc <cpu_v6_proc_fin+24> nop    ; (mov r0,  r0)
   0xc001e0c0 <cpu_v6_do_idle+0> mov    r1,  #2
   0xc001e0c4 <cpu_v6_do_idle+4> subs   r1,  r1,  #1
   0xc001e0c8 <cpu_v6_do_idle+8> nop    ; (mov r0,  r0)
   0xc001e0cc <cpu_v6_do_idle+12> mcreq  15,  0,  r1,  cr7,  cr10,  {4}
   0xc001e0d0 <cpu_v6_do_idle+16> mcreq  15,  0,  r1,  cr7,  cr0,  {4}
 → 0xc001e0d4 <cpu_v6_do_idle+20> nop    ; (mov r0,  r0)
   0xc001e0d8 <cpu_v6_do_idle+24> nop    ; (mov r0,  r0)
   0xc001e0dc <cpu_v6_do_idle+28> nop    ; (mov r0,  r0)
   0xc001e0e0 <cpu_v6_do_idle+32> bne    0xc001e0c4 <cpu_v6_do_idle+4>
   0xc001e0e4 <cpu_v6_do_idle+36> bx     lr
   0xc001e0e8 <cpu_v6_dcache_clean_area+0> mcr    15,  0,  r0,  cr7,  cr10,  {1}
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────[ threads ]────
[#0] Id 1, Name: "", stopped, reason: SIGINT
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────[ trace ]────
[#0] 0xc001e0d4 → Name: cpu_v6_do_idle()
[#1] 0xc0010848 → Name: arch_cpu_idle()
[#2] 0xc0650fe8 → Name: default_idle_call()
[#3] 0xc0054508 → Name: do_idle()
[#4] 0xc00547d8 → Name: cpu_startup_entry()
[#5] 0xc064bb00 → Name: rest_init()
[#6] 0xc08d4d70 → Name: start_kernel()
───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
0xc001e0d4 in cpu_v6_do_idle ()
```

https://www.segger.com/downloads/jlink/UM08001
