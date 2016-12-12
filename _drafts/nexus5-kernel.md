---
layout: post
comments: true
title: "Nexus 5 and the quest for the kernel"
tags: [android,git]
---

# Title

The [Nexus5](https://en.wikipedia.org/wiki/Nexus_5) is a great smartphone, now unsupported.

The hardware components are

- [Qualcomm Snapdragon](https://en.wikipedia.org/wiki/Qualcomm_Snapdragon) SoC


## History recovery

All starts with this commit

```
$ git log 3159fc5 -1 --stat
commit 3159fc579fa092e4caa0bace83a1b3fc4253ef43
Author: Devin Kim <dojip.kim@lge.com>
Date:   Sat Mar 30 00:03:31 2013 -0700

    hammerhead: Initial board files
    
    --Add hammerhead specific board files
    --Add arm/dt for hammerhead
    
    Change-Id: I5788f4eec5237d729110f92a5e3ade7499411c7c

 arch/arm/boot/dts/msm8974-hammerhead-rev-f.dts                      |  24 +++++
 arch/arm/boot/dts/msm8974-hammerhead/msm8974-hammerhead-camera.dtsi |  88 ++++++++++++++++++
 arch/arm/boot/dts/msm8974-hammerhead/msm8974-hammerhead-hdmi.dtsi   |  34 +++++++
 arch/arm/boot/dts/msm8974-hammerhead/msm8974-hammerhead-input.dtsi  | 135 +++++++++++++++++++++++++++
 arch/arm/boot/dts/msm8974-hammerhead/msm8974-hammerhead-misc.dtsi   |  85 +++++++++++++++++
 arch/arm/boot/dts/msm8974-hammerhead/msm8974-hammerhead-panel.dtsi  | 135 +++++++++++++++++++++++++++
 arch/arm/boot/dts/msm8974-hammerhead/msm8974-hammerhead-pm.dtsi     | 130 ++++++++++++++++++++++++++
 arch/arm/boot/dts/msm8974-hammerhead/msm8974-hammerhead-rev-f.dtsi  | 661 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 arch/arm/boot/dts/msm8974-hammerhead/msm8974-hammerhead-rtc.dtsi    |  35 +++++++
 arch/arm/boot/dts/msm8974-hammerhead/msm8974-hammerhead-usb.dtsi    |  24 +++++
 arch/arm/boot/dts/msm8974-lge-common/msm8974-lge-common.dtsi        |  40 ++++++++
 arch/arm/boot/dts/msm8974-lge-common/msm8974-lge-hdmi.dtsi          |  12 +++
 arch/arm/boot/dts/msm8974-lge-common/msm8974-lge-input.dtsi         |  17 ++++
 arch/arm/boot/dts/msm8974-lge-common/msm8974-lge-misc.dtsi          |  12 +++
 arch/arm/boot/dts/msm8974-lge-common/msm8974-lge-panel.dtsi         |  12 +++
 arch/arm/boot/dts/msm8974-lge-common/msm8974-lge-pm.dtsi            |  12 +++
 arch/arm/boot/dts/msm8974-lge-common/msm8974-lge-sensor.dtsi        |  12 +++
 arch/arm/boot/dts/msm8974-lge-common/msm8974-lge-usb.dtsi           |  12 +++
 arch/arm/boot/dts/msm8974-lge-common/msm8974-lge.dtsi               |  18 ++++
 arch/arm/boot/dts/msm8974-lge-common/msm8974-v2-lge.dtsi            |  19 ++++
 arch/arm/configs/hammerhead_defconfig                               | 476 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 arch/arm/mach-msm/Kconfig                                           |   2 +
 arch/arm/mach-msm/Makefile                                          |   4 +
 arch/arm/mach-msm/Makefile.boot                                     |   5 +
 arch/arm/mach-msm/include/mach/board_lge.h                          |  60 ++++++++++++
 arch/arm/mach-msm/lge/Kconfig                                       |  17 ++++
 arch/arm/mach-msm/lge/Makefile                                      |   4 +
 arch/arm/mach-msm/lge/board-8974-hammerhead-gpiomux.c               | 686 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 arch/arm/mach-msm/lge/board-8974-hammerhead.c                       | 188 +++++++++++++++++++++++++++++++++++++
 arch/arm/mach-msm/lge/devices_lge.c                                 | 111 ++++++++++++++++++++++
 30 files changed, 3070 insertions(+)
```

The *prefix* ``msm8974`` refers to the ``SoC``. The files inside the ``dts/`` directory
are **Device Tree** related (see [this slides](http://free-electrons.com/pub/conferences/2013/elce/petazzoni-device-tree-dummies/petazzoni-device-tree-dummies.pdf) for more info)

Now I want to see where this variable is used into the code:

```
$ git grep -C 3 --show-function console_disabled
drivers/tty/serial/msm_serial_hs_lite.c=static inline int get_console_state(struct uart_port *port) { return -ENODEV; };
drivers/tty/serial/msm_serial_hs_lite.c-#endif
drivers/tty/serial/msm_serial_hs_lite.c-
drivers/tty/serial/msm_serial_hs_lite.c:static bool msm_console_disabled = false;
drivers/tty/serial/msm_serial_hs_lite.c-
drivers/tty/serial/msm_serial_hs_lite.c-static struct dentry *debug_base;
drivers/tty/serial/msm_serial_hs_lite.c-static inline void wait_for_xmitr(struct uart_port *port);
--
drivers/tty/serial/msm_serial_hs_lite.c-
drivers/tty/serial/msm_serial_hs_lite.c=void msm_console_set_enable(bool enable)
drivers/tty/serial/msm_serial_hs_lite.c-{
drivers/tty/serial/msm_serial_hs_lite.c:        msm_console_disabled = !enable;
drivers/tty/serial/msm_serial_hs_lite.c-}
drivers/tty/serial/msm_serial_hs_lite.c-
drivers/tty/serial/msm_serial_hs_lite.c:static bool console_disabled(void)
drivers/tty/serial/msm_serial_hs_lite.c-{
drivers/tty/serial/msm_serial_hs_lite.c:        return msm_console_disabled;
drivers/tty/serial/msm_serial_hs_lite.c-}
drivers/tty/serial/msm_serial_hs_lite.c-
drivers/tty/serial/msm_serial_hs_lite.c-/**
--
drivers/tty/serial/msm_serial_hs_lite.c=static void msm_hsl_start_tx(struct uart_port *port)
drivers/tty/serial/msm_serial_hs_lite.c-{
drivers/tty/serial/msm_serial_hs_lite.c-        struct msm_hsl_port *msm_hsl_port = UART_TO_MSM(port);
drivers/tty/serial/msm_serial_hs_lite.c-
drivers/tty/serial/msm_serial_hs_lite.c:        if (is_console(port) && console_disabled())
drivers/tty/serial/msm_serial_hs_lite.c-                return;
drivers/tty/serial/msm_serial_hs_lite.c-
drivers/tty/serial/msm_serial_hs_lite.c-        msm_hsl_port->imr |= UARTDM_ISR_TXLEV_BMSK;
--
drivers/tty/serial/msm_serial_hs_lite.c=static unsigned int msm_hsl_tx_empty(struct uart_port *port)
--
drivers/tty/serial/msm_serial_hs_lite.c-        unsigned int ret;
drivers/tty/serial/msm_serial_hs_lite.c-        unsigned int vid = UART_TO_MSM(port)->ver_id;
drivers/tty/serial/msm_serial_hs_lite.c-
drivers/tty/serial/msm_serial_hs_lite.c:        if (is_console(port) && console_disabled())
drivers/tty/serial/msm_serial_hs_lite.c-                return 1;
drivers/tty/serial/msm_serial_hs_lite.c-
drivers/tty/serial/msm_serial_hs_lite.c-        ret = (msm_hsl_read(port, regmap[vid][UARTDM_SR]) &
--
drivers/tty/serial/msm_serial_hs_lite.c=static void msm_hsl_console_write(struct console *co, const char *s,
--
drivers/tty/serial/msm_serial_hs_lite.c-
drivers/tty/serial/msm_serial_hs_lite.c-        BUG_ON(co->index < 0 || co->index >= UART_NR);
drivers/tty/serial/msm_serial_hs_lite.c-
drivers/tty/serial/msm_serial_hs_lite.c:        if (console_disabled())
drivers/tty/serial/msm_serial_hs_lite.c-                return;
drivers/tty/serial/msm_serial_hs_lite.c-
drivers/tty/serial/msm_serial_hs_lite.c-        port = get_port_from_line(co->index);
```

It's importanto to know that ``msm_serial_hs_lite.c`` is introduced well before the ``nexus5`` with this

```
commit 1e7d178e29d5aaa4ee714f9587792ad262c563bb
Author: David Brown <davidb@codeaurora.org>
Date:   Thu Jan 17 14:25:55 2013 -0800

    tty: serial: Add MSM "LITE" UART driver
    
    Non DMA console-type serial driver for the MSM's HS uart, being run in
    legacy mode.
    
    Signed-off-by: David Brown <davidb@codeaurora.org>

 drivers/tty/serial/msm_serial_hs_lite.c | 1575 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 1575 insertions(+)
 create mode 100644 drivers/tty/serial/msm_serial_hs_lite.c
```

[Someone tried](https://lwn.net/Articles/560018/) to introduce this in the regular kernel.

## UART

The ``UART`` is accessible from the audio jack: the jack to use is the one having 4 poles (starting from the tip):

 - left (``TX``)
 - right (``RX``)
 - ``GND``
 - ``MIC``

The last one is the signal that allows to activate the serial console with a voltage level of 3.3 volts

## Links

 - [Building and booting Nexus 5 kernel](http://marcin.jabrzyk.eu/posts/2014/05/building-and-booting-nexus-5-kernel)
 - [A better audio jack console cable for Google Nexus devices](http://www.pabr.org/consolejack/consolejack.en.html)
 - [Repo](https://android.googlesource.com/device/google/debugcable) for the audio debug cable
 - Google's headset [specification](https://source.android.com/devices/accessories/headset/specification.html)
 - [Ifixit's teardown](https://it.ifixit.com/Teardown/Nexus+5+Teardown/19016)
