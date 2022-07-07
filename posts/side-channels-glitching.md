<!--
.. title: side channels: glitching
.. slug: side-channels-glitching
.. date: 2022-03-02 08:43:26 UTC
.. has_math: true
.. status: draft
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->


Until now I observed the specimen under the microscope provided by the ADC of
the chipwhisperer, but what if I would poke and perturbe its behaviour?

The model of the processor is fine and good but obviously is a model, its
**correct** behaviour is dependent of the voltage and clock "quality" that I'm
providing to it: a latch needs some margins both for clock and voltage
parameters to work in the way is intended.

It's not used specifically in the attacks that follow but doesn't hurt to know a
little more in detail: a flip-flop-like device has some specific parameters

 - **setup time** \\(t_s\\): input **must** be present and stable for at least
   this time before the clock transition
 - **hold time** \\(t_h\\): input **must** be present and stable for at least this time
   after the clock transition
 - **propagation time** \\(t_p\\): the time after which the output is expected
   to be stable after the clock transition

{{% wavedrom %}}
{ "signal": [
	{ "node": "...A..BC.." },
	{ "name": "D",   "wave": "x..2...x..", "data": ["data must be stable"] },
	{ "name": "CLK", "wave": "0.....1..." },
	{ "node": "...G..HI.." },
	{ "node": "...D..EF.." }
  ], "edge": [
	"A|D",
	"B|E",
	"C|F",
	"G<->H ts",
	"H<->I th"
], "config": { "hscale": 2 }}
{{% /wavedrom %}}

the maximum usable clock frequency of a processor is determined by the maximum delay among its elements,
in the sense that, if the operating frequency is so high that doesn't give enough time
to the signals to pass through all the logic gates to accomplish all its functions.

And this is one of the mechanisms that we are going to explit :) the other is the stability
of the voltage provided to the device: if there is not enough charge to switch the state of
an internal transistor, the final state is wrong.

## How to

This is the code for manual triggering the glitch

```python
scope.io.glitch_lp = True            # low power mosfet

scope.glitch.clk_src = 'clkgen'      # 
scope.glitch.output = 'enable_only'  # this doesn't take the clock into account
scope.glitch.repeat = 10             #
scope.glitch.width = 20              #
scope.glitch.trigger_src = 'manual'  # we are not using external triggering
```

```
scope.glitch.manual_trigger()
```

## A realt target

[USB packets](https://www.usbmadesimple.co.uk/ums_3.htm)

[MAX3421E Programming Guide](https://pdfserv.maximintegrated.com/en/an/AN3785.pdf)

[MAX3421E datasheet](https://www.sparkfun.com/datasheets/DevTools/Arduino/MAX3421E.pdf)

## Code

[Application note AVR1307](http://ww1.microchip.com/downloads/en/AppNotes/doc8049.pdf)

First of all, create all the one-bit-away instructions from the original one

```
$ public/code/fi/flip.py > public/code/fi/code.bin
$ avr-objdump -b binary -m avr:5 -D public/code/fi/code.bin

public/code/fi/code.bin:     formato del file binary


Disassemblamento della sezione .data:

00000000 <.data>:
   0:   00 2c           mov     r0, r0
   2:   01 2c           mov     r0, r1
   4:   02 2c           mov     r0, r2
   6:   04 2c           mov     r0, r4
   8:   08 2c           mov     r0, r8
   a:   10 2c           mov     r1, r0
   c:   20 2c           mov     r2, r0
   e:   40 2c           mov     r4, r0
  10:   80 2c           mov     r8, r0
  12:   00 2d           mov     r16, r0
  14:   00 2e           mov     r0, r16
  16:   00 28           or      r0, r0
  18:   00 24           eor     r0, r0
  1a:   00 3c           cpi     r16, 0xC0       ; 192
  1c:   00 0c           add     r0, r0
  1e:   00 6c           ori     r16, 0xC0       ; 192
  20:   00 ac           ldd     r0, Z+56        ; 0x38
```

the first line is the original instruction, I choosen this as a alias
for ``nop``, and then follow the 16 one-bit-distant instructions; lucky
us they aren't flow related. The original instruction executes in 1 cycle.

Now I need some instruction to actual printing out of the UART some data from
which I can deduce the effects of glitching: from the actual code of the
firmware

```c
#define USART USARTC0

	while(!USART_IsTXDataRegisterEmpty(&USART));
	USART_PutChar(&USART, 'A');
```

results in this code

```text
.-> 74a:   80 91 a1 08     lds     r24, 0x08A1 (2)
|   74e:   85 ff           sbrs    r24, 5      (1/2/3)
'-- 750:   fc cf           rjmp    .-8         (2)
    752:   81 e4           ldi     r24, 0x41   (1)
    754:   80 93 a0 08     sts     0x08A0, r24 (2)
    758:   80 e0           ldi     r24, 0x00   (1)
    75a:   90 e0           ldi     r25, 0x00   (1)
    75c:   08 95           ret                 (4/5)
```

note that this is the "slower" part of the code since the target uses a baud
rate of 38400 baud, this means the in one second can send 38400 bits or 4800
bytes.

If the target run at speed of 8MHz (as indicated by the value in
``scope.clock.clkgen_freq``) we have each cycle takes 1667 cycle for each bytes
so, since we are printing the string "hello" we have a total of around 8.3k cycles

Thsi is the macro to set a register with a predefined value:

```c
/* nice: ldi can be used only with registers r16-r31 */
#define set_r(r,value) __asm__( \
    "ldi r31, " #value "\n\  (1)
     mov r" #r ", r31 "   \  (1)
    )
```

it executes in two clock cycles, since there are 32 of them, we have 64 clock
cycles

To summarise: we have three part in our firmware:

 1. the setup part where we initialize the hardware and print out "hello"
 2. the setup of the registers with predefined value ~ 64 clock cycles
 3. a nop sled with 1 clock cycle for entry
 4. print out the content of the registers

```
$ ./chipw.py hardware/victims/firmware/simpleserial-experiments/simpleserial-experiments-CW303.hex 
Serial baud rate = 38400
XMEGA Programming flash...
XMEGA Reading flash...
Verified flash OK, 2459 bytes
'\x00hello\x80\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f'
```

## Glitching

[Chipwisperer documentation about glitch module](https://chipwhisperer.readthedocs.io/en/latest/api.html#chipwhisperer.scopes.OpenADC.glitch)


