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
with one extruder, one bed and one fan; the code associated with that in the original firmware
is ``33`` that corresponds to ``BOARD_RAMPS_13_EFB`` in Marlin.

After that I checked the pins definition in ``Marlin/pins_RAMPS.h`` for differences
I started to enable features: my printer has a display that is possible to enable with
``REPRAP_DISCOUNT_SMART_CONTROLLER`` and also a SD Card, enabled with ``SDSUPPORT``.

Now I arrive to the settings that are dangerous, in the sense that can damage your
printer if you set it wrong: until are you sure all is working right, **stay very near
to the printer with a finger on the power switch**.

The first import option is ``X_MIN_ENDSTOP_INVERTING`` that in my case was not correct:
to check that use the ``M119`` code, if you see triggered as in the example below

```
anet> query M119
Reporting endstop status
x_min: TRIGGERED
y_min: TRIGGERED
z_min: TRIGGERED
ok

```

probably means that you have to check this option.

## Find free pins
