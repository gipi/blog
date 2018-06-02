---
layout: post
comments: true
title: "Implement Text mode for a VGA controller in Verilog"
tags: [VGA, verilog, FPGA]
---

After having written about [implementing a VGA controller in Verilog]({% post_url 2018-01-23-implementing-vga-in-verilog %}) I wanted
to complete it with a new functionality: the **Text mode**.

The Text mode is described in an excellent way by [Wikipedia](https://en.wikipedia.org/wiki/Text_mode)

    Text mode is a computer display mode in which content is internally represented
    on a computer screen in terms of characters rather than individual pixels.i
    Typically, the screen consists of a uniform rectangular grid of character cells,
    each of which contains one of the characters of a character set

It's not a difficult project but it's worth making. I'll start laying out the diagram
of the controller:

![Text mode controller diagram]()

With respect to the previous VGA controller here we have two new elements: the ``ROM`` with
the predefined glyph and the Text ``RAM`` containing the characters I want to display on
screen.

## Memory

Since I'm using a spartan-6 FPGA I have access to some primitive useful to generate memories
using the **Core generator** and there is a guide:
[Spartan-6 FPGA Block RAM Resources](https://www.xilinx.com/support/documentation/user_guides/ug383.pdf).

Generally for a memory you need a **chip select** signal to enable the device
and interact with. Another signal is the **output enable** (``OE``) that connects with a buffer that
allows the device to output the values. In my case these are not necessary since the
memory is always connected and used. In particular the ``OE`` is not present in the
primitive provided by Xilinx.

For the ``ROM`` I have the following diagram

![]({{ site.baseurl }}/public/images/vga_text_rom_diagram.png)

the **clock** (``CLKA``) signal is obvious, the other are the address
line (``ADDRA``) and the output (``DOUTA``); the width of these lines
are determined by the organization of the memory you need.

In my case I need the ``ROM`` to contain the data necessary to draw
the pixel of the single character: I'll use 128 ``ASCII`` characters
and each one will be represented with a 8x16 grid; in this way I'll
need 16384 bits. Since I want to access the bits individually I configure
the memory to be ``16Kx1``

![]({{ site.baseurl }}/public/images/vga_text_rom_width.png)

Different story is the ``RAM``: I need a read and write memory device
that will contain an ``ASCII`` character index for each one of the block
in which the screen is divided; being the size of each character be 8x16
we have, for a resolution of 640x480, 80 columns and 30 rows.

This means the we need 2400 bytes, i.e. the memory organized as 2400x8.

![]({{ site.baseurl }}/public/images/vga_text_ram_diagram.png)

Since I need to write there are two signal lines (``DINA`` and ``ADDRB``)


## Implementation

The idea here is that the value of the pixel is decided calculating in which
\\(column, row\\) belong: using its coordinates \\((x, y\\) this can be calculated
with a division respectively by 8 and 16; that is simpler to implement in digital logic taking only
from the 3rd and fourth bits of the signals

```
// (column, row) = (x / 8, y / 16)
assign column = x[9:3];
assign row = y[8:4];
```

and at this point we can calculate the address into the text memory in order to
extract the ``ASCII`` character we need

```
assign text_address = column + (row * 80);

text_memory tm(
  .clka(clk), // input clka
  .wea(wea), // input [0 : 0] wea
  .addra(text_address), // input [11 : 0] addra
  .dina(dina), // input [7 : 0] dina
  .clkb(clk), // input clkb
  .addrb(text_address), // input [11 : 0] addrb
  .doutb(text_value) // output [7 : 0] doutb
);
```

The final value of the pixel is obtained using the modulo of the pixel's coordinates
as index for the glyph into the ``ROM``

```
// here we get the remainder
assign glyph_x = x[2:0];
assign glyph_y = y[3:0];
                     // text_value * 128 + glyph_x + (glyph_y * 8)
assign glyph_address = (text_value << 7) + glyph_x + (glyph_y << 3);

blk_mem_gen_v7_3 glyph_rom(
  .clka(clk), // input clka
  .addra(glyph_address), // input [13 : 0] addra
  .douta(pixel[0]) // output [0 : 0] douta
);
```

Also here the multiplications by power of two are implemented with simpler left shifts.

## Memory


## Glyph and ROM

To display characters I need obviously some of them; for this project I used the
[Unicode VGA font](http://www.inp.nsk.su./~bolkhov/files/fonts/univga/). This font
is distributed using the ``BDF`` format.

This format is simply put a text format 

```
STARTCHAR space
ENCODING 32
SWIDTH 480 0
DWIDTH 8 0
BBX 8 16 0 -4
BITMAP
00
00
00
00
00
00
00
00
00
00
00
00
00
00
00
00
ENDCHAR
```

In order to be used into the ``Xilinx`` IDE, the glyph must be converted into a ``COE``
format, that is simply a binary representation of the words into the memory.

Since I didn't know any program that does that I modified an existing program that
converts ``BDF`` glyphs into ``C`` header files and added the option to dump in the
needed format: the repo is here [bdf2c](https://github.com/gipi/bdf2c) but don't look
at the code, is very ugly :P.


```
$ cat fpga/mojo/VGAGlyph/font/uni_vga/u_vga16.bdf  | /opt/bdf2c/bdf2c -z glyph.coe -b
```

## Sync

The first attempt for this controller had some issues with timing
something like described [here](http://blog.andyselle.com/2014/12/04/vga-character-generator-on-an-fpga/).

## Summary

At the end it seems to work just fine :)

![](https://github.com/gipi/electronics-notes/raw/master/fpga/mojo/VGAGlyph/monitor-glyph.png)

