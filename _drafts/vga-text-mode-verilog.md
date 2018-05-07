---
layout: post
comments: true
title: "Implement Text mode for a VGA controller in Verilog"
tags: [VGA, verilog, FPGA]
---

After having written about [implementing a VGA controller in Verilog]({% post_url 2018-01-23-implementing-vga-in-verilog %}) I wanted
to complete it with a new functionality: the **Text mode**.

The Text mode is described in an excellent way by [Wikipedia](https://en.wikipedia.org/wiki/Text_mode)

    Text mode is a computer display mode in which content is
    internally represented on a computer screen in terms of
    characters rather than individual pixels. Typically, the screen consists of
    a uniform rectangular grid of character cells, each of which contains one of
    the characters of a character set

It's not a difficult project but it's worth making. I'll start laying out the diagram
of the controller:

![Text mode controller diagram]()

With respect to the previous VGA controller here we have two new elements: the ``ROM`` with
the predefined glyph and the Text ``RAM`` containing the characters I want to display on
screen.

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

## Summary

At the end it seems to work just fine :)

![](https://github.com/gipi/electronics-notes/raw/master/fpga/mojo/VGAGlyph/monitor-glyph.png)

