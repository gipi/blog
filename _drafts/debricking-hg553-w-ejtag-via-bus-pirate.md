---
layout: post
comments: true
title: "Debricking an HG553 with EJTAG using a Bus Pirate"
tags: [JTAG,EJTAG, Bus Pirate, electronics, HG553, router]
---

## Prologue

A friend of mine gave to me a couple of years ago an old _Vodafone Station_, a famous
home router for ADSL used in Italy.

He asked to me to install OpenWRT on it; He tried to follow the standard procedure
but without success and knowning that I have some fancy gadget told me to
use ``JTAG`` for do magic.

``JTAG`` is an interface (but not a protocol) used by manufacturer in order to
physically test the well functioning of a board: it allows to access pins and
devices attached to this interface. If you want to know more this [post](http://blog.senr.io/blog/jtag-explained) is
enough.

The standard tool to interact with it is [OpenOCD](), a software client that allows the user
to read/write the cpu's register, memory and flash and also to single step the cpu.
There are only two things to configure: the **adapter** and the **target**.

The first is the device that you use to connect your computer to the ``JTAG`` interface,
the last is the device that you want to control via this interface.

The first tries were not so successfully, some times the cpu were recognized and
the commands worked very well, some times the cpu resumed. After experimenting
and reading all over the fucking internet I discovered that ``MIPS`` SOCs implement
a proprietary extension of ``JTAG``, called **EJTAG**.

Without going to deep into explanation of the differences between the two interfaces,
the thing you need to know is that in order to make the interface work you have to pull-up
the ``TRST`` pin with a 300 Ohm resistor; **it's so fucking simple**.

What puzzles me is that fact that is indicated as optional signal but without it doesn't
work! I mean, it's indicated with a negative logic but nowhere there is an example with
the bus pirate where is indicated this connection.

## Present

After introduced the scenario, follow me in the procedure: first of all the pinout of the ``JTAG`` header is the following

```
        GND  10  9  TDI (orange)
      nTSRT   8  7  N/C
   nSRST(?)   6  5  TMS (red)
        VCC   4  3  TDO (brown)
(black) GND   2  1  TCK (yellow)
```

where the colors are of the [Bus Pirate cable](https://electronics-notes.readthedocs.io/en/latest/buspirate/#pinouts).
The only difference is that I have put a a jumper between ``VCC`` and ``nTRST`` with a 300 Ohm resistor in it.

OpenOCD needs a configuration file, doesn't exist one for this router, but you can
create easily one: below the file used by me

```
# https://www.sodnpoo.com/posts.xml/jtag_flashing_bcm6348_devices_with_a_bus_pirate_and_openocd.xml
source [find interface/buspirate.cfg]

# copied from <bcm6348>
set _CHIPNAME bcm6358
set _CPUID 0x0635817f

jtag newtap $_CHIPNAME cpu -irlen 5 -ircapture 0x1 -irmask 0x1f -expected-id $_CPUID

set _TARGETNAME $_CHIPNAME.cpu
target create $_TARGETNAME mips_m4k -endian big -chain-position $_TARGETNAME
# see http://dangerousprototypes.com/docs/Gonemad's_Bus_Pirate/OpenOCD_walk_through#F.29_Connecting_OpenOCD_to_your_board.2Fdevice:
buspirate_vreg 0
buspirate_mode open-drain
buspirate_pullup 1

reset_config none

buspirate_port /dev/ttyUSB0

set _FLASHNAME $_CHIPNAME.flash
# this model has 16mib
# I don't know bc starts at 0xbe000000 instead of 0xbfc00000
# but I found the address into this post <https://onetransistor.blogspot.it/2016/02/debrick-huawei-hg553-brcm6358-cfe.html>
flash bank $_FLASHNAME cfi 0xbe000000 0x1000000 2 2 $_TARGETNAME
```

Now it's possible to start OpenOCD with the following command:

```
$ openocd -f vodafone.cfg
 ...
```

To enter commands you need to connect via ``telnet`` to the port 4444

```
$ telnet localhost 4444
>
```

the first command is ``targets``, it shows what OpenOCD sees with the ``JTAG``

```
> targets
    TargetName         Type       Endian TapName            State       
--  ------------------ ---------- ------ ------------------ ------------
 0* bcm6358.cpu        mips_m4k   big    bcm6358.cpu        halted
```

Now I can try to solve my friend's problem: in order to install OpenWRT you have
to somehow write it in the flash, usually is done by the bootloader but this version
has it locked down; to overcome this limitation I need to overwrite the bootloader
with an unlocked one with OpenOCD.

Exists a command called ``write_flash``

With the Bus Pirate this procedure elapsed for 5 hours! In a near future I probably
write a post about configuring a raspberry pi as a ``JTAG`` adapter, it's like ten times
quicker.

## Epilogue

By the way, if you are interested in stuff that I tear down in my spare time, there
is a [repo](https://github.com/gipi/teardown) for that. It's an infinite work in progress.

