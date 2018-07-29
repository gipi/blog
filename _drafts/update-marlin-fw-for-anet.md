---
layout: post
comments: true
title: "Updating my Anet A8 to the newest Marlin firmware"
tags: [Anet, 3d printer, Marlin]
---

How you already know, I own a cheap 3d printer [my chinese 3D printer](https://www.aliexpress.com/item/Newest-Upgraded-Reprap-Prusa-i3-3D-Printer-kits-High-Quality-Desktop-CNC-Full-colors-3d-printer/32705999543.html)
that I use to, you know, 3d print stuffs, but also I want to utilize for 
example as a little milling or a laser engraver and I need some extra pins to drive these devices.

Looking at the [GCODE](http://marlinfw.org/meta/gcode/) you can see that exist some codes that allow
to handle pins: 
 - [M 42](http://marlinfw.org/docs/gcode/M042.html) Set Pin State
 - [M 43](http://marlinfw.org/docs/gcode/M043.html) Debug Pins
 - [M 43 T](http://marlinfw.org/docs/gcode/M043-T.html) Toggle

you need to activate these functionalities using ``PINS_DEBUGGING`` when compiling.

The other adventure will be find out which pins exposed free on the board
are which

![]({{ site.baseurl }}/public/images/anet-a8-ramp13.jpg)

By the way, in order to have these functionalities I need to update my firmware since
the firmware (with source) provided with the printer has not these activated.

## Porting

First of all we need the source code: this is available at the github repo

```
$ git clone
$ cd Marlin
$ git checkout --track origin/1.1.x
```

if you want you can create a branch for your printer. Now I can compare the options
between the original firmware and the default settings; there is [configuration guide](http://marlinfw.org/docs/configuration/configuration.html)
on the firmware home site with step to step instructions, here I will document the more
important options and some advices.

First off all you need to know what kind of board you have, in my case I have a RAMPS 1.3,
(or maybe RAMP 1.4, it's not very clear the distiction, from what I see the only
things changing are the extra pins but check your case).

However it has one extruder, one bed and one fan; the code associated with that in the original firmware
is ``33`` that corresponds to ``BOARD_RAMPS_13_EFB`` in Marlin.

After that I checked the pins definition in ``Marlin/pins_RAMPS.h`` for differences
I started to enable features: my printer has a display that is possible to enable with
``REPRAP_DISCOUNT_SMART_CONTROLLER`` and also a SD Card, enabled with ``SDSUPPORT``.

Now I arrive to the settings that are dangerous, in the sense that can damage your
printer if you set it wrong: until are you sure all is working right, **stay very near
to the printer with a finger on the power switch**, in particular if you have intention
to move the head, calling the home procedure for example.

The first important options are

 - ``X_MIN_ENDSTOP_INVERTING``
 - ``Y_MIN_ENDSTOP_INVERTING``
 - ``Z_MIN_ENDSTOP_INVERTING``

that in my case was not correct: the default configuration for my printer
caused it to think that the head was always at the end of the ???.

To check that use the ``M119`` code, if you see triggered as in the example below

```
anet> query M119
Reporting endstop status
x_min: TRIGGERED
y_min: TRIGGERED
z_min: TRIGGERED
ok

```

probably means that you have to check this option.

Another option that was inverted was that for the direction of the extruder, i.e.
``INVERT_E0_DIR``.

Another **very important** setting is the ``DEFAULT_AXIS_STEPS_PER_UNIT`` that indicates
how many steps for unit of measurement the stepper motors have to move: in my case it was
very out, the z axis had ten times the correct value (indeed when tested the first
time the high speed of it had raise attention from my part).

There are other options less dangerous but important for a good print quality

 - ``DEFAULT_MAX_FEEDRATE``
 - ``DEFAULT_XJERK``, ``DEFAULT_YJERK`` and ``DEFAULT_ZJERK``
 - ``HOMING_FEEDRATE_XY``
 - ``HOMING_FEEDRATE_Z``

Finally some options that are new with respect to the original firmware are
the ``THERMAL_PROTECTION_HOTENDS`` ``THERMAL_PROTECTION_BED`` and the related
options: in my case, when the fan started spinning, the extruder temperature
was dropping of ten degrees and it was unable to make it raise fast enough
and printer was halting to prevent temperature runaway; increasing the acceptable
temperature difference and/or the time allowed to balance it fixed the problem.

At the end obviously the main way to test all is correct is to test some
[calibration cube](https://www.thingiverse.com/thing:1278865).


## Find free pins

My board has like four usable extra pins near the stepper motor ones, named
``A11``, ``A12``, ``D11`` and ``D12``; each one is placed in a column with another two
pins, ``GND`` (in the middle) and ``5V`` (the lower one).
