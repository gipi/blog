<!--
.. title: Reusing old shit: lcd screen
.. slug: reuse-old-laptop-screen
.. date: 2021-01-31 00:00:00
.. tags: old shit,LVDS,LCD,WIP
.. category: 
.. link: 
.. description: 
.. type: text
-->


It's happened in the past that someone gifted me of very old (and not working
anymore) laptops that otherwise would have been thrown in the garbage; my idea
for them was of reusing some parts that are more valuable: battery, disks,
    keyboards, etc...

<!-- TEASER_END -->

One of the things more valuable are the LCD displays: the first thing to do is
tear down the laptop and uncover the LCD panel itself; in the back there are few
labels, one of them contains a code that identifies the model of the panel
itself. Which one? I don't know but you can try all of them, is a problem
solvable in polynomial time :)

![](/images/lcd-label.png)

At this point you can use the site [panelook.com](http://www.panelook.com/) to
find the technical details: in my case the code is ``CLAA154WA01AQ``
corresponding to this
[model](http://www.panelook.com/CLAA154WA01AQ_CPT_15.4_LCM_parameter_2716.html);
the important parameters are the ones indicated in the image below

![](/images/lcd-parameters.png)

 - resolution: will be used to configure the controller board
 - signal interface: to choose the correct cable between the controller board and the LCD
 - lamp type: to choose the correct illumination power source

## Signal interface

In our example we see that we need a ``LVDS (1 ch, 6-bit) , 30 pins , Connector``

On Aliexpress you can find this [cable](https://www.aliexpress.com/item/14-inches-15-inches-15-4-inch-notebook-screen-line-30-pin-FIX-solo-6-an/32733053803.html).

## Lamp type

The LCD screen needs a **backlight**, without it the luminance of the display is
not powerful enough; technically is called **inverter** (probably because unlike
a normal power supply, it raises the voltage, by a lot!) and is powered externally from
the controller board.

The parameters that distinguish inverters from each others is the number of connectors to the LCD itself and the
type: led or CCFL. In the majority of cases the second one is used.

These are links on Aliexpress (I don't know these sellers, YMMV) just to give
you an idea of what I am talking about

 - [LVDS cable](https://www.aliexpress.com/item/10-x-Common-LVDS-Cables-for-LCD-Display-Panel-Controller/32222031400.html)
 - [LCD controller board](https://www.aliexpress.com/item/V29-Universal-LCD-Controller-Board-TV-Motherboard-VGA-HDMI-AV-TV-USB/32764451599.html)
 - [CCFL inverter](https://www.aliexpress.com/item/5Pcs-lot-2-Lamp-Backlight-Universal-LCD-CCFL-10V-28V-Inverter-For-10-Inch-To-22/32767424250.html)

## Controller board

Now we need something that can drive the panel from a video source: on
Aliexpress you can search for it using terms like "lcd controller board"; check
for the inputs you are interested in (``HDMI``, ``VGA`` etc...) and if it has a
compliant connector for lamp type and signal cable.

One example is this [one](https://it.aliexpress.com/item/1005002070410194.html)
but obviously double check yourself.

Read accurately the description of the product and the resolutions supported,
sometimes you can see that is possible to "update" the board with a specific
firmware to support specific a resolution.

### V29 Universal LCD Controller Board

The one used by me is the **V29 controller board**, usually comes with a remote
and a "keyboard", that has the possibility to
flash a different firmware to adapt to the correct resolution of the screen; the
procedure is the following

 - put the firmware (usually named ``LAMV29_something.bin``) into an USB drive
 - connect the USB drive to the USB slot of the board disconnected from the
   power supply
 - turn on the power and you should see the light of the keyboard blinking
 - when the led stops blinking then the update is completed

## FPGA

**TODO:** An interesting project for the future would be to implement a LDVS controller
for my [mojo board](link://slug/mojo-devlopment-board).


 - https://iamzxlee.wordpress.com/2014/10/21/from-old-laptop-into-a-new-monitor/
 - https://sites.google.com/site/lcd4hobby/5-lcd-as-pc-hdmi-av-tv-multidisplay
 - [LVDS Fundamentals](https://learnabout-electronics.org/Downloads/LVDS%20Fairchild%20AN-5017.pdf)
 - [Driving a Laptop LCD using an FPGA](https://www.element14.com/community/community/designcenter/zedboardcommunity/minized/blog/2019/03/04/driving-a-laptop-lcd-using-an-fpga)
