---
layout: post
comments: true
title: "Reusing old shit: laptop keyboard"
tags: [keyboard, AVR, arduino]
---

Here we are with another experiment in reusing otherwise trash-destined
electronics material, this episode we are going to refurbish a keyboard,
from the recovering of the internal "matrix" to the design of the PCB destined
as the controller board, to finally reworking of an existing firmware to create
a new USB keyboard.

The keyboard under recovery is the following

![keyboard]({{ site.baseurl }}/public/images/keyboard/keyboard.jpg)

extracted from an HP pavillon, model AT8A. It has a ribbon cable with 26(?) pins
and pitch of 1.0mm.

## Matrix recovery

The underlying working of a keyboard is described by a matrix of nodes
corresponding to each key; a set of signals act as inputs and the remaining as
outputs: when a key is pressed the corresponding couple of input/output lines
are connected allowing to detect it. In order to work the hardware needs to act
upon the inputs one at the times.

In order to do that I'm using the following program, in this case I'm using the
Arduino Mega because of the big number of signals available to it: I'm using a
breakout board as adapter to connect the FPC cable to the pins 22-51 of the
Arduino·

{% github_sample_ref gipi/electronics-notes/blob/master/AVR/KeyboardMatrixRecovery/KeyboardMatrixRecovery.ino %}
{% highlight c++ %}
{% github_sample gipi/electronics-notes/blob/master/AVR/KeyboardMatrixRecovery/KeyboardMatrixRecovery.ino %}
{% endhighlight %}

From pressing any key in order, I obtain the following array contaning all the
couple of pins that each key triggers (reworked to be used directly in python)

```python
>>> keys = [
  (25,15), (14,13), (17,13), (18,13), (25,13), (17,16), (18,16), (25,16), (16,14), (17, 4), (18, 4), (25, 4), (14, 4), (25, 9), (14, 5), (25, 2), (14, 2),
  (17,15), (23,15), (23,16), (23,13), (23,12), (17,12), (17,10), (23,10), (23, 9), (23, 4), (23, 3), (17, 3), (14, 3), (25, 5), (18, 2),
  (18,15), (24,15), (24,16), (24,13), (24,12), (18,12), (18,10), (24,10), (24, 9), (24, 4), (24, 3), (18, 3), (18, 9), (21, 5), (17, 2),
  (15,14), (21,15), (21,16), (21,13), (21,12), (25,12), (25,10), (21,10), (21, 9), (21, 4), (21, 3), (25, 3), (17, 5), (21, 2),
  (22,20), (17, 9), (20,15), (20,16), (20,13), (20,12), (14,12), (14,10), (20,10), (20, 9), (20, 4), (20, 3), (24,22), (24, 5), (20, 2),
  (19,18), (17,11), (25, 8), (23, 6), (20, 5), (14, 6), (17, 7), (21,19), (24, 2), (23, 5), (23, 2),
]
```

At this point I can massage the data to look for the matrix

```python
>>> get = lambda x: set([_ for _ in keys if _[1] == x or _[0] == x])
>>> get(2)
{(14, 2), (17, 2), (18, 2), (20, 2), (21, 2), (23, 2), (24, 2), (25, 2)}
>>> [(_, len(get(_))) for _ in range(30)]
[(0, 0),
 (1, 0),
 (2, 8),
 (3, 8),
 (4, 8),
 (5, 7),
 (6, 2),
 (7, 1),
 (8, 1),
 (9, 7),
 (10, 8),
 (11, 1),
 (12, 8),
 (13, 8),
 (14, 10),
 (15, 8),
 (16, 8),
 (17, 12),
 (18, 10),
 (19, 2),
 (20, 11),
 (21, 11),
 (22, 2),
 (23, 11),
 (24, 11),
 (25, 11),
 (26, 0),
 (27, 0),
 (28, 0),
 (29, 0)]
```

Since I'm looking for "round numbers" it's interesting to see that a couple of signals are
linked to 8 others, in particular if we look for example to the signals
activated by the number line identified by the id 2

```python
>>> get(2)
{(14, 2), (17, 2), (18, 2), (20, 2), (21, 2), (23, 2), (24, 2), (25, 2)}
```

they are all linked to more than 8 signals; after analyzing I can split the
matrix with the following scheme of 8 inputs and 16 outputs

| **Rows** | 14 | 17 | 18 | 20 | 21 | 23 | 24 | 25 |
| **Columns** | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 15 | 16 | 19 | 22 |

**NOTE:** although there are \\(8*16 = 128\\) possible keys, only 88 are used,
so some signals are underused.

## Controller board design and firmware

Since my intention is to use the ATMega32U4 (the main advantage is the builtin
USB) I need to find a way to minimize pin  usage: 24 pins are not available in
this chip so I decideded to use 8 pins for the inputs (possibly from the same
bank, ``PDx`` for example) and the remaining 16, the output pins, to be handled
via two daisy-chained shift registers (the [74HC165](https://www.sparkfun.com/datasheets/Components/General/sn74hc165.pdf))
communicating via ``SPI`` protocol.

Reading the chip
[datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7766-8-bit-AVR-ATmega16U4-32U4_Datasheet.pdf)
at section 17, and the application note
[AVR151: Setup and Use of the SPI](https://ww1.microchip.com/downloads/en/AppNotes/Atmel-2585-Setup-and-Use-of-the-SPI_ApplicationNote_AVR151.pdf),
I have all the information needed to interact with the ``SPI`` subsystem.

| Signal | pin | Description |
|--------|-----|-------------|
| ``SS`` | ``PB0`` | chip select |
| ``SCK`` | ``PB1`` | clock |
| ``MOSI`` | ``PB2`` | Master Output Slave Input |
| ``MISO`` | ``PB3`` | Master Input Slave Output |

For my use case the ``MOSI`` is not necessary since we are not going to communicate
data to the shift register but I don't think is possible to reuse anyway. For
latching the data on the shift registers I need one more signal but at the end
I'm going to use 5 signals instead of 16.

## Links

 - [FIGURING OUT A KEY MATRIX (SCAN MATRIX)](https://www.instructables.com/id/Figuring-out-a-Key-Matrix-Scan-Matrix/)
 - [How a Key Matrix Work](http://pcbheaven.com/wikipages/How_Key_Matrices_Works/)
 - [Arduino Keyboard Matrix Code and Hardware Tutorial](https://www.baldengineer.com/arduino-keyboard-matrix-tutorial.html)
 - [ATMega32u4 HID Keyboard](https://github.com/kmani314/ATMega32u4-HID-Keyboard)
