---
layout: post
comments: true
title: "Mojo FPGA development board"
tags: [electronics, FPGA, Mojo]
---

I have a new shiny toy, a [Mojo V3](https://embeddedmicro.com/mojo-v3.html) development board: it's primarly intended as **FPGA**
playground, but what's this ``FPGA`` you are talking about?

## FPGA

Simply put, an ``FPGA`` is a technology that allows to *design chip using software* i.e.
a ``FPGA`` is not **programmed** but **configured** using a special kind of language, a **hardware description language**
([HDL](https://en.wikipedia.org/wiki/Hardware_description_language)). The most common
is ``Verilog``.

Its primary scope is to design and test a chip before to start to build it for real:
if you are used to design software you know that bug in production are a bad thing,
but you also know that a fix can be done in order of hours and hypotetically
(depending on your platform) be deployed in a time scale of a day maybe.

With hardware design this is not obviously the case: first of all who design a
chip doesn't have at his disposal the machinery needed to create it, the design
must be sent to a factory that after a delay of several months return to you
the final product.

Any error in the real chip causes the entire process to be repeated! Take in mind
that the cost of all of this is around the million dollars scale!

This [video](https://www.youtube.com/watch?v=eDmv0sDB1Ak) talks about the problems
in designing a chip like the ``x86`` one.

## Mojo

The mojo can be described as an arduino for ``FPGA``: not only because has an
``ATMega`` chip that is used to program the board.

Normally a ``FPGA``
has appositely crafted programmer to put the configuration in them (doc
[here](http://www.xilinx.com/support/documentation/user_guides/ug380.pdf)) in
this board instead the arduino-like chip presents on it, acts as programmer
thanks to a special [bootloader](https://github.com/embmicro/mojo-arduino)
burned into it: the ``ATMega`` loads the bitstream into the flash, the ``FPGA``
when resets, loads the code from there.

**An important thing to remember is that the configuration is stored temporary
on the memory of the FPGA, after a new power-up the chip needs to be
re-configured again.** By the way the Mojo allows to store a resident bitstream
into the flash that is loaded using the ``ATMega`` when the board is powered.

The specs of the board are 

 - ``Spartan 6 XC6SLX9``: ([Spartan-6 Family Overview](http://www.xilinx.com/support/documentation/data_sheets/ds160.pdf)) contains 9152 logic cells and 11440 flip-flops
 - 84 digital pins
 - 8 analog pins
 - package ``TQG144``
 - speed grade -2



### Pinout

The pinout is a little strange at first, [here](http://www.xilinx.com/support/packagefiles/s6packages/6slx9tqg144pkg.txt) the reference for the chip with the
correct pinout naming and [here](http://www.xilinx.com/support/documentation/user_guides/ug385.pdf) the complete reference.

For reference I made a grab of the layout of the board:

![Mojo V3 pinout]({{ site.baseurl }}/public/images/mojo-pinout.png)

The pins used in a design must be indicated in a file with extension ``ucf`` (stands for **user constraints file**) that
pratically indicate to the design which signals are exposed and where.

Like any other documentation is a big [pdf](http://www.xilinx.com/itp/xilinx10/books/docs/cgd/cgd.pdf).

## Development environment

The bad side of writing code for this technology is that the toolsets are pratically only proprietary, with all the
programs pretty heavy (``ISE`` occupy approximately 20GB on disk).

In order to use this board you need to install the ``Xilinx`` software named ``ISE``, the instruction
are [here](https://embeddedmicro.com/tutorials/mojo-software-and-updates/installing-ise).

However to start as beginner you can use the [mojo ide](https://embeddedmicro.com/tutorials/mojo-software-and-updates/mojo-ide).

## Links

 - [Mojo page](https://embeddedmicro.com/tutorials/mojo/)
 - [Mojo schematics](https://embeddedmicro.com/media/wysiwyg/mojo/v3-sch.pdf)
 - [Mojo Eagle files](https://embeddedmicro.com/media/wysiwyg/mojo/mojo-eagle-v3.zip)
 - [Altering the FPGA clock frequency of the Mojo](http://www.smolloy.com/2016/01/altering-the-fpga-clock-frequency-of-the-mojo/)
 - [Controlling A Seven Segment Display Using Mojo](https://coolcapengineer.wordpress.com/2013/06/03/controlling-seven-segment-display-using-mojo/)
