---
layout: post
comments: true
title: "Simple stepping an ATmega with a FPGA"
tags: [electronics, atmega, FPGA, mojo]
---

As continuation of the post about the internals of the [clock]({% post_url 2018-03-15-clock-atmega %})
of an ATMega, I decided to test the possibilities of simulating a clock
using a FPGA, in particular a [mojo development board]({% post_url 2016-10-30-mojo-devlopment-board %}).

## PLL

First of all we need to generate a 16MHz clock to feed into the ``XTAL1`` pin,
for a Spartan-6 FPGA we have available the ``DCM_SP`` primitive


From this information we know that to create a clock of 16MHz from the
50MHz clock of the mojowe need to apply a factor of \\({8\over 25}\\),
so that the module reads as follow (some parameters and pins have been removed
for clarity)

```
  DCM_SP
  #(.CLKDV_DIVIDE          (2.000),
    .CLKFX_DIVIDE          (25),
    .CLKFX_MULTIPLY        (8),
    .CLKIN_DIVIDE_BY_2     ("FALSE"),
    .CLKIN_PERIOD          (20.0),
    .CLKOUT_PHASE_SHIFT    ("NONE"),
    .CLK_FEEDBACK          ("1X"),
    .DESKEW_ADJUST         ("SYSTEM_SYNCHRONOUS"),
    .PHASE_SHIFT           (0),
    .STARTUP_WAIT          ("FALSE"))
  dcm_sp_inst
    // Input clock
   (.CLKIN                 (clkin1),
    .CLKFB                 (clkfb),
    // Output clocks
    .CLK0                  (clk0),
    .CLK90                 (),
    .CLK180                (),
    .CLK270                (),
    .CLK2X                 (),
    .CLK2X180              (),
    .CLKFX                 (CLK_OUT1),
    .CLKFX180              (CLK_OUT1pi),
    .CLKDV                 (),
    // Other control and status signals
    .LOCKED                (locked_int),
    .STATUS                (status_int),
    .RST                   (RESET));
```
