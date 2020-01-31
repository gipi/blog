---
layout: post
comments: true
title: "Experiments around fault injection"
tags: [AVR, fault injection, firmware]
---

The **target** attached to the chipwhisperer is identified in the wiki as the [CW303](https://wiki.newae.com/CW303_XMEGA_Target).
It has as microcontroller an Atmel's XMEGA128 ([datasheet](https://static.chipdip.ru/lib/279/DOC000279729.pdf)).

## Installation steps

This part is primarly for me in order to remember what I did to getting started,
you can see a more precise procedure in the [documentation](https://chipwhisperer.readthedocs.io/en/latest/installing.html).

```
$ git clone https://github.com/newaetech/chipwhisperer.git && cd chipwhisperer
$ git submodule update --init jupyter                        # To get the jupyter notebook tutorials
$ python3 -m pip install -r jupyter/requirements.txt --user
$ jupyter nbextension enable --py widgetsnbextension         # enable jpyter interactive widgets
$ python3 -m pip install -e . --user                         # use pip to install in develop mode
```

the jupyter part is related to the tutorials, if you don't need them, only clone and install.

```
$ avr-gcc \
    -Wall \
    -mmcu=atxmega128d3 \
    -o public/code/fi/firmware \
    public/code/fi/firmware.c
$ avr-objdump -d public/code/fi/firmware | less
```

```
$ make -C hardware/victims/firmware/simpleserial-base PLATFORM=CW303
```

```
python3
Python 3.7.5 (default, Oct 27 2019, 15:43:29)
[GCC 9.2.1 20191022] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import chipwhisperer as cw
>>> scope = cw.scope()
>>> scope
cwlite Device
gain =
    mode = low
    gain = 0
    db   = 5.5
adc =
    state      = False
    basic_mode = low
    timeout    = 2
    offset     = 0
    presamples = 0
    samples    = 24400
    decimate   = 1
    trig_count = 226703590
clock =
    adc_src       = clkgen_x1
    adc_phase     = 0
    adc_freq      = 96000000
    adc_rate      = 96000000.0
    adc_locked    = True
    freq_ctr      = 0
    freq_ctr_src  = extclk
    clkgen_src    = system
    extclk_freq   = 10000000
    clkgen_mul    = 2
    clkgen_div    = 1
    clkgen_freq   = 192000000.0
    clkgen_locked = True
trigger =
    triggers = tio4
    module   = basic
io =
    tio1       = serial_tx
    tio2       = serial_rx
    tio3       = high_z
    tio4       = high_z
    pdid       = high_z
    pdic       = high_z
    nrst       = high_z
    glitch_hp  = False
    glitch_lp  = False
    extclk_src = hs1
    hs2        = None
    target_pwr = True
glitch =
    clk_src     = target
    width       = 10.15625
    width_fine  = 0
    offset      = 10.15625
    offset_fine = 0
    trigger_src = manual
    arm_timing  = after_scope
    ext_offset  = 0
    repeat      = 1
    output      = clock_xor
>>> target = cw.target(scope)
Serial baud rate = 38400
```

However you need to call the ``default_setup()`` in order to have all configured
correctly

```python
class OpenADC(ScopeTemplate, util.DisableNewAttr):
    """OpenADC scope object.  ..."""

    def default_setup(self):
        """Sets up sane capture defaults for this scope

         *  45dB gain
         *  5000 capture samples
         *  0 sample offset
         *  rising edge trigger
         *  7.37MHz clock output on hs2
         *  4*7.37MHz ADC clock
         *  tio1 = serial rx
         *  tio2 = serial tx

        .. versionadded:: 5.1
            Added default setup for OpenADC
        """
        self.gain.db = 25
        self.adc.samples = 5000
        self.adc.offset = 0
        self.adc.basic_mode = "rising_edge"
        self.clock.clkgen_freq = 7.37e6
        self.trigger.triggers = "tio4"
        self.io.tio1 = "serial_rx"
        self.io.tio2 = "serial_tx"
        self.io.hs2 = "clkgen"

        self.clock.adc_src = "clkgen_x4"

        ...
```

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
us they aren't flow related

```c
#define USART USARTC0

	while(!USART_IsTXDataRegisterEmpty(&USART));
	USART_PutChar(&USART, 'A');
```

we obtain this code

```
.-> 74a:   80 91 a1 08     lds     r24, 0x08A1
|   74e:   85 ff           sbrs    r24, 5
'-- 750:   fc cf           rjmp    .-8
    752:   81 e4           ldi     r24, 0x41
    754:   80 93 a0 08     sts     0x08A0, r24
    758:   80 e0           ldi     r24, 0x00
    75a:   90 e0           ldi     r25, 0x00
    75c:   08 95           ret
```


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

## Links

 - [AVR instruction set manual](http://ww1.microchip.com/downloads/en/devicedoc/atmel-0856-avr-instruction-set-manual.pdf)
 - https://pbpython.com/interactive-dashboards.html
 - https://jakevdp.github.io/PythonDataScienceHandbook/04.08-multiple-subplots.html
 - https://towardsdatascience.com/subplots-in-matplotlib-a-guide-and-tool-for-planning-your-plots-7d63fa632857
