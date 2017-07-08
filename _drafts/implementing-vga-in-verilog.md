---
layout: post
comments: true
title: "Implementing VGA interface with verilog"
tags: [electronics, VGA, verilog, FPGA]
---

**VGA** stands for **Video graphics array** and it's one of the most
diffuse standard for video transmission; it roots its definition from
the way old catodic tube worked: an electron beam travel horizontally
for each line and at the end the beam passes to the next one.

The signals of this interface are the following

| Signal | Logic level | Description |
|--------|-------------|-------------|
| VSYNC  | 5V          | Tells the monitor when a screen has been completed |
| HSYNC  | 5V | Tells the monitor that a line has been completed |
| R      | 0.7V | red color channel |
| G | 0.7V | green color channel |
| B | 0.7V | blue color channel |

Below a time diagram stolen from this [page of the VGA](https://eewiki.net/pages/viewpage.action?pageId=15925278)

![stolen VGA timing diagram](https://eewiki.net/download/attachments/15925278/signal_timing_diagram.jpg?version=1&modificationDate=1368220404290&api=v2)

There are a lot of possibilities for a VGA signal, we can change its
resolution, its refresh rate but I choosen to stick with 640x480@60Hz

This is the verilog code, it simply uses two counters ``CounterX`` and ``CounterY``
in order to assign the logic level of ``vga_h_sync`` and ``vga_v_sync``; moreover
when ``inDisplayArea`` is true, then the counters are also the coordinates
of the pixel being draw:

```verilog
module hvsync_generator(
    input clk,
    output vga_h_sync,
    output vga_v_sync,
    output reg inDisplayArea,
    output reg [9:0] CounterX,
    output reg [8:0] CounterY
  );
reg vga_HS, vga_VS;

wire CounterXmaxed = (CounterX == 800); // 16 + 48 + 96 + 640
wire CounterYmaxed = (CounterY == 525); // 10 + 2 + 33 + 480

  // Module get from <http://www.fpga4fun.com/PongGame.html>
always @(posedge clk)
if (CounterXmaxed)
  CounterX <= 0;
else
  CounterX <= CounterX + 1;

always @(posedge clk)
begin
  if (CounterXmaxed)
  begin
    if(CounterYmaxed)
      CounterY <= 0;
    else
      CounterY <= CounterY + 1;
  end
end

always @(posedge clk)
begin
  vga_HS <= (CounterX > (640 + 16) && (CounterX < (640 + 16 + 96)));   // active for 96 clocks
  vga_VS <= (CounterY > (480 + 10) && (CounterY < (480 + 10 + 2)));   // active for 2 clocks
end

always @(posedge clk)
begin
	inDisplayArea <= (CounterX < 640) && (CounterY < 480);
end

assign vga_h_sync = ~vga_HS;
assign vga_v_sync = ~vga_VS;

endmodule
```

This code suppose that ``clk`` is a clock with a frequency of 25MHz.

From the hardware side of the interface you have to know that the monitor
has an impedance of 75 Ohm for each color channel, so to obtain a 0.7V from
a 3V3 logic level you have to use a serie resistor of 270 Ohm.

To note here that without using a DAC you can have only 8 colors.

![vga schematics]({{ site.baseurl }}/public/images/vga-schematics.png)
