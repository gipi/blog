---
layout: post
comments: true
title: "Reusing old shit: lcd screen"
---

It's happened in the past that someone gifted me of very old laptops that otherwise would have been thrown
in the garbage: since I don't want to waste any resource I learned during the years to reuse what is possible.

One of the things more valuable are the LCD displays: the first thing to do is tear down the laptop and uncover
the LCD panel itself; in the back there are few labels, one of them contains a code that identifies the model
of the panel itself.

![]({{ site.baseurl }}/public/images/lcd-label.png)

At this point you can use the site [panelook.com](http://www.panelook.com/) to find the technical details: in my
case the code is ``CLAA154WA01AQ`` corresponding to this [page](http://www.panelook.com/CLAA154WA01AQ_CPT_15.4_LCM_parameter_2716.html);
the important parameters are the ones indicated in the image below

![]({{ site.baseurl }}/public/images/lcd-parameters.png)

 - resolution: will be used to configure the controller board
 - signal interface: to choose the correct cable between the controller board and the LCD
 - lamp type: to choose the correct illumination power source

## Signal interface

In our example we see that we need a ``LVDS (1 ch, 6-bit) , 30 pins , Connector``

On Aliexpress you can find this [cable](https://www.aliexpress.com/item/14-inches-15-inches-15-4-inch-notebook-screen-line-30-pin-FIX-solo-6-an/32733053803.html).

## Lamp type

The LCD screen needs a particular type of light, called **backlight** that is powered externally from the
controller board, indeed with a very high voltage.

The parameters that distinguish inverters each others is the number of connectors to the LCD itself and the
type: led or CCFL. In the majority of cases the second one is used.

[LVDS cable](https://www.aliexpress.com/item/10-x-Common-LVDS-Cables-for-LCD-Display-Panel-Controller/32222031400.html)
[LCD controller board](https://www.aliexpress.com/item/V29-Universal-LCD-Controller-Board-TV-Motherboard-VGA-HDMI-AV-TV-USB/32764451599.html)
[CCFL inverter](https://www.aliexpress.com/item/5Pcs-lot-2-Lamp-Backlight-Universal-LCD-CCFL-10V-28V-Inverter-For-10-Inch-To-22/32767424250.html)


 - https://iamzxlee.wordpress.com/2014/10/21/from-old-laptop-into-a-new-monitor/
 - https://sites.google.com/site/lcd4hobby/5-lcd-as-pc-hdmi-av-tv-multidisplay
 - [LVDS Fundamentals](https://www.fairchildsemi.com/application-notes/AN/AN-5017.pdf)
