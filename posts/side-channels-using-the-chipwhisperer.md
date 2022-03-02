<!--
.. title: side channels: using the chipwhisperer
.. slug: side-channels-using-the-chipwhisperer
.. date: 2022-03-02 08:43:12 UTC
.. tags: side channels, hardware
.. category: 
.. link: 
.. description: 
.. type: text
-->

This is a post in a series regarding side channels, from the theoretical and
pratical point of view; the posts are

 - introduction on the model of computing devices (to be finished)
 - using the Chipwhisperer (this post)
 - power analysis (to be finished)
 - glitching (to be finished)

<!-- TEASER_END -->

All the practical experimentations performed in these posts are done using my own Chipwhisperer's board,
the [CWLITE](https://rtfm.newae.com/Capture/ChipWhisperer-Lite/) one, it's an open source, open
hardware device that allows to quickly setup and execute side channels related
attacks. 

This model come along with its own target board attached
(named [CW303](https://rtfm.newae.com/Targets/CW303%20XMEGA/) with an an Atmel's XMEGA128
([datasheet](https://static.chipdip.ru/lib/279/DOC000279729.pdf))) and in the
official repository of the project are available a couple of firmwares to
experiment with.

## Installation steps

This part is primarly for me in order to remember what I did to getting started,
you can see a more precise (an up to date) procedure in the [documentation](https://chipwhisperer.readthedocs.io/en/latest/installing.html).

```
$ git clone https://github.com/newaetech/chipwhisperer.git && cd chipwhisperer
$ git submodule update --init jupyter                        # To get the jupyter notebook tutorials
$ python3 -m pip install -r jupyter/requirements.txt --user
$ jupyter nbextension enable --py widgetsnbextension         # enable jpyter interactive widgets
$ python3 -m pip install -e . --user                         # use pip to install in develop mode
```

the jupyter part is related to the tutorials, if you don't need them, only clone and install.


The compilation of the firmware for the target can be done in this way, where
the ``-C`` flag tells which firmware we want (``PLATFORM`` tells the build
sistem that the target is the XMega)

```
$ make -C hardware/victims/firmware/simpleserial-base PLATFORM=CW303
```

If instead you want to compile some code "out of the tree" you can use directly
the compiler with the right flags:

```
$ avr-gcc \
    -Wall \
    -mmcu=atxmega128d3 \
    -o <output ELF file \
    <c source file>
$ avr-objcopy -O ihex <ELF file> <HEX file>
```

the last line generates the ``HEX`` file that is the format needed for flashing.

In general is very useful to double check the generated code; you can use ``avr-objdump``

```
$ avr-objdump -d <ELF file> | less
```

The ChipWhisperer's library is implemented in python and you can use the
``REPL`` to interact with the device, for the example the following is a snippet
of a session

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

If you want to flash the firmware you can do it directly from python

```
scope = cw.scope()
prog = cw.programmers.XMEGAProgrammer
cw.program_target(
        scope,
        prog,
        <path_fw>)
```

## Pinout

There is a header with 20 pin at the edge of the board intended to be the
interface between the board and the target. This allows to power the board (but
only with 3.3 Volts), to provide clock, to interact with the serial and to program it (XMega and AVR
protocols).

From the [original documentation](https://rtfm.newae.com/Capture/ChipWhisperer-Lite/#20-pin-connector)

| Left | number | number | Right |
|------|--------|--------|-------|
| 5V (not connected in this model)  | 1 | 2 | GND |
| 3V3  | 3 | 4 | HS1/I (clock input) |
| nRST | 5 | 6 | HS2/O (output clock and glitch) |
| MISO (``SPI`` and ``AVR`` programming) |  7 |  8 | VREF |
| MOSI (``SPI`` and ``AVR`` programming) |  9 | 10 | IO1 (serial RX) |
| SCK  (``SPI`` and ``AVR`` programming) | 11 | 12 | IO2 (serial TX) |
| PC  (XMega128 programming pin) | 13 | 14 | IO3 |
| PD  (XMega128 programming pin) | 15 | 16 | IO4 (used as a trigger) |
| GND  | 17 | 18 | 3V3 |
| GND  | 19 | 20 | 5V (not connected in this model) |

## Firmware updating

It's possible to update the firmware that runs on the ChipWhisperer itself via
python: issuing the following

```python
import chipwhisperer as cw
scope = cw.scope()
programmer = cw.SAMFWLoader(scope=scope)
programmer.enter_bootloader(really_enter=True)
programmer.program('/dev/ttyACM0', hardware_type='cwlite')
```

you should see a device appearing in the ``dmesg`` log.

```
[1111253.064641] usb 2-10: USB disconnect, device number 27
[1111253.449854] usb 2-10: new high-speed USB device number 28 using xhci_hcd
[1111253.602083] usb 2-10: New USB device found, idVendor=03eb, idProduct=6124, bcdDevice= 1.10
[1111253.602086] usb 2-10: New USB device strings: Mfr=0, Product=0, SerialNumber=0
[1111253.630152] cdc_acm 2-10:1.0: ttyACM0: USB ACM device
[1111253.630322] usbcore: registered new interface driver cdc_acm
[1111253.630324] cdc_acm: USB Abstract Control Model driver for USB modems and ISDN adapters
```

