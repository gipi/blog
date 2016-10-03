---
layout: post
comments: true
title: "Mojo FPGA development board"
---

I have a new shiny toy, a [Mojo V3](https://embeddedmicro.com/mojo-v3.html) development board: it's primarly intended as **FPGA**
playground, but what's this ``FPGA`` you are talking about?

## FPGA

Simply put, an ``FPGA`` is a technology that allows to *design chip using software* i.e. this kind
of chip is not **programmed** but **configured** using a special kind of language, a **hardware description language**
([HDL](https://en.wikipedia.org/wiki/Hardware_description_language))

## Mojo

The mojo can be described as an arduino for ``FPGA``: also because has an
``ATMega`` chip that is useful to program the board: normally this kind of chip
has appositely crafted programmer to put the configuration in them (doc
[here](http://www.xilinx.com/support/documentation/user_guides/ug380.pdf)) in
this board instead the arduino-like chip presents on it act as programmer
thanks to a special [bootloader](https://github.com/embmicro/mojo-arduino)
burned into it: the ``ATMega`` loads the bitstream into the flash, the ``FPGA``
when reset loads the code from there.

**An important thing to remember is that the configuration is stored temporary
on the memory of the FPGA, after a new power-up the chip needs to be
re-configured again.**

The specs are 

 - ``Spartan 6 XC6SLX9``
 - 84 digital pins
 - 8 analog pins
 - package ``TQG144``
 - speed grade -2

## Pinout

The pinout is a little strange at first, [here](http://www.xilinx.com/support/packagefiles/s6packages/6slx9tqg144pkg.txt) the reference for the chip with the
correct pinout naming and [here](http://www.xilinx.com/support/documentation/user_guides/ug385.pdf) the complete reference.

![Mojo V3 pinout]({{ site.baseurl }}/public/images/mojo-pinout.png)

The pins used in a design must be indicated in a file with extension ``ucf`` (stands for **user constraints file**) that
pratically indicate to the design which signals are exposed and where.

Like any other documentation is a big [pdf](http://www.xilinx.com/itp/xilinx10/books/docs/cgd/cgd.pdf).

## Development environment

The bad side of writing code for this technology is that the toolsets are pratically only proprietary, with all the
programs pretty heavy (``ISE`` occupy approximately 20GB on disk).

## Links

 - [Altering the FPGA clock frequency of the Mojo](http://www.smolloy.com/2016/01/altering-the-fpga-clock-frequency-of-the-mojo/)
 - [Controlling A Seven Segment Display Using Mojo](https://coolcapengineer.wordpress.com/2013/06/03/controlling-seven-segment-display-using-mojo/)
