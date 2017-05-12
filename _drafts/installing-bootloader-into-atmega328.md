---
layout: post
comments: true
title: "Installing bootloader into ATMega328p"
tags: [atmega, arduino, optiboot, breadboard, electronics]
---

This is a standard thing to do with an ATMega328p, the core of
the Arduino development board: burn a bootloader into it and then
use a ``USB`` connection to flash code into it.

There a lot of posts about this procedure, but are scattered
all over the internet but without precise schematics and
the _low level_ stuffs.

In particular I want to install a bootloader into a pristine
chip without external crystal and with a prescaler of 8 (i.e.
the chip is running at 1MHz). This last condition is problematic
if you want your bootloader to work with the correct baud rate.

## AVR

For more informations read the [datasheet](http://www.atmel.com/images/doc8161.pdf).

First of all we are using an ``AVR`` chip that has an **Harvard architecture**
i.e. the memory address for ``RAM`` and executable code are separated: in
particular the flash (where the code you write will live after the uploading)
technically named **program memory** it's divided in two sections

 - Boot loader section located in the upper part of the program memory
 - Application program section located at the start of the program memory

the start of the bootloader part is not fixed but can be configured via the fuses.

## Optiboot

This is a common bootloader that can be used with the Arduino IDE
(the page for the standard Arduino bootloader is [here](https://www.arduino.cc/en/Hacking/Bootloader)).

Before to compile we need to download the source code

```text
$ git clone https://github.com/optiboot/optiboot && cd optiboot
```

The source for the bootloader is a little deep

```
$ cd optiboot/bootloaders/optiboot/
```

If your system is configured for autocompletion a ``make <TAB><TAB>`` should show you all the
available targets

```
atmega1280             atmega168p             atmega32_isp           attiny84               FORCE                  luminet                pro16_isp              virboot328             wildfirev3_isp
atmega1284             atmega168p_isp         atmega644p             baudcheck              isp                    luminet_isp            pro20                  virboot328_isp         xplained168pb
atmega1284_isp         atmega32               atmega8                bobuino                isp-stk500             mega1280               pro20_isp              virboot8               xplained328p
atmega1284p            atmega328              atmega88               bobuino_isp            lilypad                mega1280_isp           pro8                   wildfire               xplained328pb
atmega16               atmega328_isp          atmega88_isp           clean                  lilypad_isp            mighty1284             pro8_isp               wildfirev2             
atmega168              atmega328_pro8         atmega88p_isp          diecimila              lilypad_resonator      mighty1284_isp         sanguino               wildfirev2_isp         
atmega168_isp          atmega328_pro8_isp     atmega8_isp            diecimila_isp          lilypad_resonator_isp  pro16                  sanguino_isp           wildfirev3
```

Before to finally compile it I have two issues with respect to a standard system:
I'm using the [bus pirate]() as ``ISP`` programmer and my chip has not an external
crystal and this cause problem with the default baud rate.

Luckily we can configure that using some variables

```
$ make atmega328 ISPTOOL=buspirate ISPPORT=/dev/ttyUSB0 AVR_FREQ=1000000L BAUD_RATE=9600 ISPSPEED=-b115200
```

## Breadboard

In my case I have a 

![]({{ site.baseurl }}/public/images/bootloader.png)

The thing important to note is the capacitor between ``DTR`` and ``RESET``,
without it the chip won't be reset and won't enter the bootloader. I don't
understand why: someone says that "[the level on this signal line changes when
the serial bridge is connected (enabled in software).
However on the reset you only want a pulse. The capacitor acts as
a differentiator](http://forum.arduino.cc/index.php?topic=26877.0)".


## Programming

``Optiboot`` declares that uses the [stk500v1](https://github.com/Optiboot/optiboot/wiki/HowOptibootWorks) protocol

```
$ avrdude -c arduino -p m328p -P /dev/ttyUSB0 -b 9600
```

A minimal snippet of code that toggle the logic level
of pin ``PB5`` is the following

```c
#include <avr/io.h>
#include <util/delay.h>

#define BLINK_DELAY_MS 1000

int main() {
 /* set pin 5 of PORTB for output*/
 DDRB |= _BV(DDB5);
 
 while(1) {
  /* set pin 5 high to turn led on */
  PORTB |= _BV(PORTB5);
  _delay_ms(BLINK_DELAY_MS);
 
  /* set pin 5 low to turn led off */
  PORTB &= ~_BV(PORTB5);
  _delay_ms(BLINK_DELAY_MS);
 }
}
```

This is also very good to check that the internal clock is
set correctly e we haven't screw up the fuses settings.

We can use the Arduino build system to save time

```
BOARD_TAG    = uno
F_CPU        = 1000000L
MONITOR_PORT = /dev/ttyUSB0

AVRDUDE_ARD_BAUDRATE   = 9600

include /usr/share/arduino/Arduino.mk
```

and compile and upload with

```
$ make -C source_dir/ upload
```

**Note that the source file, the Makefile must be in the same directory.**
