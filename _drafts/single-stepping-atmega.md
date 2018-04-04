---
layout: post
comments: true
title: "Simple stepping an ATmega with a FPGA"
tags: [electronics, atmega, FPGA, mojo]
---

As continuation of the post about the internals of the [clock]({% post_url 2018-03-15-clock-atmega %})
of an ATMega, I decided to test the possibilities of simulating a clock
using a FPGA, in particular using my loyal [mojo development board]({% post_url 2016-10-30-mojo-devlopment-board %}).

My intent is to create a system to generate glitching with an external clock, but since
I like to proceed one step at times I start creating a 16MHz clock that can be switched
to a manual pulse to create a **single step** atmega.

The process included the use of a FPGA, a minimal circuit with a microcontroller
and some ``C`` code.

## FPGA

### PLL

First of all we need to generate a 16MHz clock to feed into the ``XTAL1`` pin,
for a Spartan-6 FPGA we have available the ``DCM_SP`` primitive

Internally it uses a **Phase Locked Loop**: it's a system that allows to
create a suitable frequency starting from a source clock; the explanation
of its functioning is out of scope of this post, there are a ton of resources
on the internet that can explain better than me this stuff.

The primitive ``DCM_SP`` allows to indicate the ratio of the new clock
with respect to the source clock: since we need an output clock of 16MHz from the
50MHz clock of the mojo we need to apply a factor of \\({8\over 25}\\).

Generally you can use ``Coregen`` to create an appropriate clock but since
I want to learn a little more about primitives of Xilinx's FPGA this is the
code needed: (some parameters and pins have been removed for clarity)

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

### BUFGMUX

[Spartan-6 FPGA Clocking Resources](https://www.xilinx.com/support/documentation/user_guides/ug382.pdf)

The second step included the adding of a multiplexer for the clock signal: a FPGA usually has
dedicated resources to deal with the particular kind of signals that are the clocks; in our case
we need to switch from a continous clock to a pulse one.

In order to do that I used the ``BUFGMUX``

## Circuit

Obviously to single step the microcontroller I need to connect it to the FPGA: at first I tried
to use a breadboard but with my huge disappointment I discovered that because of the noise
induced by the jumper wires and the breadboard itself, also without pumping the clock inside
the ``XTAL1`` pin, the ATMega was running at like a few kHz.

To riduce parassitic signals I soldered a protoboard with only the ``UART``, ``VCC``, ``GND``
and the ``XTAL1`` pins connected externally. If you want the schematics is pratically equal
to the circuit described in [this old post]({% post_url 2017-06-27-installing-bootloader-into-atmega328 %})

At that point the system worked flawlessy.


## Code

To test my device I re-adapted the simplest program for a microcontroller: the **blink sketch**:
it simply lights a led for 5 seconds when started and then alternates between on and off
without delay

```
/*
 * A simple sketch that blink a led on pin A5 (port PC5)
 */
#include <avr/io.h>
#include <util/delay.h>

int main() {
    DDRC  = (1 << PC5);       //Sets the direction of the PC7 to output

    PORTC |= (1 << PC5);       //Sets PC7 high
    _delay_ms(5000);
    PORTC &= ~(1 << PC5);       //Sets PC7 low
    _delay_ms(1000);

    cli();
    while (1) {
        PORTC |= (1 << PC5);
        PORTC &= ~(1 << PC5);
    }
}
```

it uses directly the I/O memory port of the ATMega in order to avoid the overhead
of calling ``digitalWrite()`` that is used in normal Arduino sketches.
If you want to understand what ``PORTC``, ``DDRC`` etc... refer to, use the
[datasheet](http://ww1.microchip.com/downloads/en/DeviceDoc/ATmega328_P%20AVR%20MCU%20with%20picoPower%20Technology%20Data%20Sheet%2040001984A.pdf)
and look for the **I/O-Ports** section.

To check the assembly instruction obtained compiling this code I used ``radare2``:

```
$ r2 -AA -a avr fpga/mojo/GlitchGen/avr/build-uno/avr.elf
[0x00000000]> pdf @ sym.main
/ (fcn) sym.main 52
|   sym.main ();
|              ; CALL XREF from 0x00000080 (sym.main)
|           0x00000080      80e2           ldi r24, 0x20
 ; set value of I/O addr 0x07 (Port C Data Direction Register) to 0x20
|           0x00000082      87b9           out 0x07, r24
 ; set 5th bit of I/O addr 0x08 (Port C Data Register)
|           0x00000084      459a           sbi 0x08, 5  
|           0x00000086      2fef           ser r18       ; r18 = 0xff
|           0x00000088      83e2           ldi r24, 0x23
|           0x0000008a      94ef           ldi r25, 0xf4
|              ; JMP XREF from 0x00000092 (sym.main)
|       .-> 0x0000008c      2150           subi r18, 0x01
|       :   0x0000008e      8040           sbci r24, 0x00
|       :   0x00000090      9040           sbci r25, 0x00
|       `=< 0x00000092      e1f7           brne 0x8c       ; loop for 0xf423 cycles
|       ,=< 0x00000094      00c0           rjmp 0x96
|       |      ; JMP XREF from 0x00000094 (sym.main)
|       `-> 0x00000096      0000           nop
|           0x00000098      4598           cbi 0x08, 5     ; clear 5th bit of I/O addr 0x08
|           0x0000009a      2fef           ser r18
|           0x0000009c      83ed           ldi r24, 0xd3
|           0x0000009e      90e3           ldi r25, 0x30
|              ; JMP XREF from 0x000000a6 (sym.main)
|       .-> 0x000000a0      2150           subi r18, 0x01
|       :   0x000000a2      8040           sbci r24, 0x00
|       :   0x000000a4      9040           sbci r25, 0x00
|       `=< 0x000000a6      e1f7           brne 0xa0       ; loop for 0x30d3
|       ,=< 0x000000a8      00c0           rjmp 0xaa
|       |      ; JMP XREF from 0x000000a8 (sym.main)
|       `-> 0x000000aa      0000           nop
\           0x000000ac      f894           cli
[0x00000000]> pdf @ fcn.000000ae
/ (fcn) fcn.000000ae 6
|   fcn.000000ae ();
|              ; JMP XREF from 0x000000b2 (fcn.000000ae)
|       .-> 0x000000ae      459a           sbi 0x08, 5
|       :   0x000000b0      4598           cbi 0x08, 5
\       `=< 0x000000b2      fdcf           rjmp 0xae
```

The last three instructions are what interest me; using
the [Instruction set cheat sheet](http://www.avr-tutorials.com/sites/default/files/Instruction%20Set%20Summary.pdf)
as reference for the number of clock cycles for instruction we have the following table

| Instruction | Clock cycles |
|-------------|--------------|
| sbi | 2 |
| cbi | 2 |
| rjmp | 2 |


