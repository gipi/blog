---
layout: post
comments: true
title: "Capture USB packets and debug an Arduino bootloader"
tags: [Arduino, USB, wireshark, stk500]
---

For some reason my 3d printer, one day, didn't want to update its firmware
so I tried to debug the process that at end of the day is the same process
all the Arduinos use for the same thing, indeed the processing unit of my device
is an ATMega2560 ([datasheet](http://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-2549-8-bit-AVR-Microcontroller-ATmega640-1280-1281-2560-2561_datasheet.pdf)).

All happens via ``USB`` but in reality the underlying protocol is the ``stk500``,
a serial protocol that normally would be spoken via ``UART``.

## Sniff the USB

In Linux is possible to intercept the ``USB`` packets using the device file ``usbmon``
that is not active by default but must be enabled mounting the ``debugfs`` and
loading the ``usbmon`` module. These are the easy copy&paste instructions (also to allow
a normal user to access it):

```
# mount -t debugfs none_debugs /sys/kernel/debug
# modprobe usbmon
# sudo setfacl -m u:$USER:r /dev/usbmon*
```

When finally the device is created you can use you sniffer to intercept the
traffic; in my case I will use ``wireshark``.

The most important parameter you have to check is the ``bus id`` and ``device address``
of the device you want to listen to; to find it a simple ``lsusb`` is enough

```
$ lsusb 
Bus 002 Device 002: ID 8087:8000 Intel Corp. 
Bus 002 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 001 Device 002: ID 8087:8008 Intel Corp. 
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
Bus 004 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 003 Device 003: ID 04d9:1603 Holtek Semiconductor, Inc. Keyboard
Bus 003 Device 002: ID 045e:0040 Microsoft Corp. Wheel Mouse Optical
Bus 003 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
```

In the case above, if you want to listen to the keyboard's traffic,
use the following filter

    usb.bus_id == 3 && usb.device_address == 3

```
# echo '3-3:1.0' > /sys/bus/usb/drivers/usbhid/unbind
# lsusb -v -s 3:2

Bus 003 Device 002: ID 045e:0040 Microsoft Corp. Wheel Mouse Optical
Device Descriptor:
  bLength                18
  bDescriptorType         1
  bcdUSB               1.10
  bDeviceClass            0 (Defined at Interface level)
  bDeviceSubClass         0 
  bDeviceProtocol         0 
  bMaxPacketSize0         8
  idVendor           0x045e Microsoft Corp.
  idProduct          0x0040 Wheel Mouse Optical
  bcdDevice            3.00
  iManufacturer           1 Microsoft
  iProduct                3 Microsoft 3-Button Mouse with IntelliEye(TM)
  iSerial                 0 
  bNumConfigurations      1
  Configuration Descriptor:
    bLength                 9
    bDescriptorType         2
    wTotalLength           34
    bNumInterfaces          1
    bConfigurationValue     1
    iConfiguration          0 
    bmAttributes         0xa0
      (Bus Powered)
      Remote Wakeup
    MaxPower              100mA
    Interface Descriptor:
      bLength                 9
      bDescriptorType         4
      bInterfaceNumber        0
      bAlternateSetting       0
      bNumEndpoints           1
      bInterfaceClass         3 Human Interface Device
      bInterfaceSubClass      1 Boot Interface Subclass
      bInterfaceProtocol      2 Mouse
      iInterface              0 
        HID Device Descriptor:
          bLength                 9
          bDescriptorType        33
          bcdHID               1.10
          bCountryCode            0 Not supported
          bNumDescriptors         1
          bDescriptorType        34 Report
          wDescriptorLength      72
          Report Descriptor: (length is 72)
            Item(Global): Usage Page, data= [ 0x01 ] 1
                            Generic Desktop Controls
            Item(Local ): Usage, data= [ 0x02 ] 2
                            Mouse
            Item(Main  ): Collection, data= [ 0x01 ] 1
                            Application
            Item(Local ): Usage, data= [ 0x01 ] 1
                            Pointer
            Item(Main  ): Collection, data= [ 0x00 ] 0
                            Physical
            Item(Global): Usage Page, data= [ 0x09 ] 9
                            Buttons
            Item(Local ): Usage Minimum, data= [ 0x01 ] 1
                            Button 1 (Primary)
            Item(Local ): Usage Maximum, data= [ 0x03 ] 3
                            Button 3 (Tertiary)
            Item(Global): Logical Minimum, data= [ 0x00 ] 0
            Item(Global): Logical Maximum, data= [ 0x01 ] 1
            Item(Global): Report Size, data= [ 0x01 ] 1
            Item(Global): Report Count, data= [ 0x03 ] 3
            Item(Main  ): Input, data= [ 0x02 ] 2
                            Data Variable Absolute No_Wrap Linear
                            Preferred_State No_Null_Position Non_Volatile Bitfield
            Item(Global): Report Size, data= [ 0x05 ] 5
            Item(Global): Report Count, data= [ 0x01 ] 1
            Item(Main  ): Input, data= [ 0x01 ] 1
                            Constant Array Absolute No_Wrap Linear
                            Preferred_State No_Null_Position Non_Volatile Bitfield
            Item(Global): Usage Page, data= [ 0x01 ] 1
                            Generic Desktop Controls
            Item(Local ): Usage, data= [ 0x30 ] 48
                            Direction-X
            Item(Local ): Usage, data= [ 0x31 ] 49
                            Direction-Y
            Item(Local ): Usage, data= [ 0x38 ] 56
                            Wheel
            Item(Global): Logical Minimum, data= [ 0x81 ] 129
            Item(Global): Logical Maximum, data= [ 0x7f ] 127
            Item(Global): Report Size, data= [ 0x08 ] 8
            Item(Global): Report Count, data= [ 0x03 ] 3
            Item(Main  ): Input, data= [ 0x06 ] 6
                            Data Variable Relative No_Wrap Linear
                            Preferred_State No_Null_Position Non_Volatile Bitfield
            Item(Main  ): End Collection, data=none
            Item(Global): Usage Page, data= [ 0xff ] 255
                            Vendor Specific
            Item(Local ): Usage, data= [ 0x02 ] 2
                            (null)
            Item(Global): Logical Minimum, data= [ 0x00 ] 0
            Item(Global): Logical Maximum, data= [ 0x01 ] 1
            Item(Global): Report Size, data= [ 0x01 ] 1
            Item(Global): Report Count, data= [ 0x01 ] 1
            Item(Main  ): Feature, data= [ 0x22 ] 34
                            Data Variable Absolute No_Wrap Linear
                            No_Preferred_State No_Null_Position Non_Volatile Bitfield
            Item(Global): Report Size, data= [ 0x07 ] 7
            Item(Global): Report Count, data= [ 0x01 ] 1
            Item(Main  ): Feature, data= [ 0x01 ] 1
                            Constant Array Absolute No_Wrap Linear
                            Preferred_State No_Null_Position Non_Volatile Bitfield
            Item(Main  ): End Collection, data=none
      Endpoint Descriptor:
        bLength                 7
        bDescriptorType         5
        bEndpointAddress     0x81  EP 1 IN
        bmAttributes            3
          Transfer Type            Interrupt
          Synch Type               None
          Usage Type               Data
        wMaxPacketSize     0x0004  1x 4 bytes
        bInterval              10
Device Status:     0x0000
  (Bus Powered)
# echo '3-3:1.0' > /sys/bus/usb/drivers/usbhid/bind
```

    usb.bus_id == 3 && usb.device_address == 7 && usb.transfer_type == 0x03 && usb.data_len > 2 && usb.endpoint_number.direction ==1

## STK500

| Command name | Value |
|--------------|-------|
| CMD_SIGN_ON                          | 0x01 |
| CMD_SET_PARAMETER                    | 0x02 |
| CMD_GET_PARAMETER                    | 0x03 |
| CMD_SET_DEVICE_PARAMETERS            | 0x04 |
| CMD_OSCCAL                           | 0x05 |
| CMD_LOAD_ADDRESS                     | 0x06 |
| CMD_FIRMWARE_UPGRADE                 | 0x07 |
| CMD_CHECK_TARGET_CONNECTION          | 0x0D |
| CMD_LOAD_RC_ID_TABLE                 | 0x0E |
| CMD_LOAD_EC_ID_TABLE                 | 0x0F |
| CMD_ENTER_PROGMODE_ISP               | 0x10 |
| CMD_LEAVE_PROGMODE_ISP               | 0x11 |
| CMD_CHIP_ERASE_ISP                   | 0x12 |
| CMD_PROGRAM_FLASH_ISP                | 0x13 |
| CMD_READ_FLASH_ISP                   | 0x14 |
| CMD_PROGRAM_EEPROM_ISP               | 0x15 |
| CMD_READ_EEPROM_ISP                  | 0x16 |
| CMD_PROGRAM_FUSE_ISP                 | 0x17 |
| CMD_READ_FUSE_ISP                    | 0x18 |
| CMD_PROGRAM_LOCK_ISP                 | 0x19 |
| CMD_READ_LOCK_ISP                    | 0x1A |
| CMD_READ_SIGNATURE_ISP               | 0x1B |
| CMD_READ_OSCCAL_ISP                  | 0x1C |
| CMD_SPI_MULTI                        | 0x1D |


## Analyze captured data

Interesting query on the captured data

    $ tshark -r /opt/gipi.github.io/mendel.pcapng \
        -2 -R "usb.bus_id == 3 && usb.device_address == 7 && usb.transfer_type == 0x03 " \
        -T fields \
        -e usb.capdata \
        -Y usb.capdata | xxd -r -p | xxd | less

This below is an annotated hexdump

![]({{ site.baseurl }}/public/images/usb-stk500.png)

take in mind that the ``CMD_LOAD_ADDRESS`` has as argument an address expressed
as word (if you work with ``AVR`` you will learn that in the hard way),
so is right to ask for ``0x100`` bytes from address ``0x80000000`` and then
ask for ``0x100`` bytes from address ``0x80000080`` as  is performed in the dump around
address ``0x140`` and then ``0x260``.

## Dissector

```
$ git clone && cd
$ mkdir build && cd build && cmake ..
$ make
$ cmake -DCUSTOM_PLUGIN_SRC_DIR=plugins/stk500 ..
$ make -C plugins/stk500
```

```
usb.bus_id == 3 && usb.device_address == 7 && usb.transfer_type == 0x03 && usb.data_len > 0 && usb.endpoint_address.direction == 1
```

Example

```
#include <epan/reassemble.h>
   ...
save_fragmented = pinfo->fragmented;
flags = tvb_get_guint8(tvb, offset); offset++;
if (flags & FL_FRAGMENT) { /* fragmented */
    tvbuff_t* new_tvb = NULL;
    fragment_data *frag_msg = NULL;
    guint16 msg_seqid = tvb_get_ntohs(tvb, offset); offset += 2;
    guint16 msg_num = tvb_get_ntohs(tvb, offset); offset += 2;

    pinfo->fragmented = TRUE;
    frag_msg = fragment_add_seq_check(msg_reassembly_table,
        tvb, offset, pinfo,
        msg_seqid, NULL, /* ID for fragments belonging together */
        msg_num, /* fragment sequence number */
        tvb_captured_length_remaining(tvb, offset), /* fragment length - to the end */
        flags & FL_FRAG_LAST); /* More fragments? */

    new_tvb = process_reassembled_data(tvb, offset, pinfo,
        "Reassembled Message", frag_msg, &msg_frag_items,
        NULL, msg_tree);

    if (frag_msg) { /* Reassembled */
        col_append_str(pinfo->cinfo, COL_INFO,
                " (Message Reassembled)");
    } else { /* Not last packet of reassembled Short Message */
        col_append_fstr(pinfo->cinfo, COL_INFO,
                " (Message fragment %u)", msg_num);
    }

    if (new_tvb) { /* take it all */
        next_tvb = new_tvb;
    } else { /* make a new subset */
        next_tvb = tvb_new_subset_remaining(tvb, offset);
    }
} else { /* Not fragmented */
    next_tvb = tvb_new_subset_remaining(tvb, offset);
}

.....
pinfo->fragmented = save_fragmented;
```


it's possible to dump only the "Leftover data", this is
a special kind of data that is defined for generic USB packets (see ``packet-usb.c``); in the same
file there is also a function ``try_dissect_next_protocol()``

```
static gint
dissect_usb_payload(tvbuff_t *tvb, packet_info *pinfo,
                    proto_tree *parent, proto_tree *tree,
                    usb_conv_info_t *usb_conv_info, guint8 urb_type,
                    gint offset, guint16 device_address)
{
    ...
    if (tvb_captured_length_remaining(tvb, offset) > 0) {
        next_tvb = tvb_new_subset_remaining(tvb, offset);
        offset += try_dissect_next_protocol(parent, next_tvb, pinfo, usb_conv_info, urb_type, tree);
    }
    ...
}

static gint
try_dissect_next_protocol(proto_tree *tree, tvbuff_t *next_tvb, packet_info *pinfo,
        usb_conv_info_t *usb_conv_info, guint8 urb_type, proto_tree *urb_tree)
{
    ...
    switch(usb_conv_info->transfer_type) {
        case URB_BULK:
            heur_subdissector_list = heur_bulk_subdissector_list;
            usb_dissector_table = usb_bulk_dissector_table;
            break;
        ...
    }

    ...

    if (try_heuristics && heur_subdissector_list) {
        ret = dissector_try_heuristic(heur_subdissector_list,
                next_tvb, pinfo, tree, &hdtbl_entry, usb_conv_info);
        if (ret)
            return tvb_captured_length(next_tvb);
    }

    ...

}

```


https://ask.wireshark.org/questions/45944/decode-usb-interface-class-correctly

## Links

 - [Video](https://www.youtube.com/watch?v=F7NlCaaL3yU) with an introduction to the USB protocol
 - [Kernel documentation about USBmon](https://www.kernel.org/doc/Documentation/usb/usbmon.txt)
 - [Wireshark's reference for USB filter values](https://www.wireshark.org/docs/dfref/u/usb.html)
 - [Embedded USB - a brief tutorial](http://www.computer-solutions.co.uk/info/Embedded_tutorials/usb_tutorial.htm)
 - http://eleccelerator.com/tutorial-about-usb-hid-report-descriptors/
 - https://julien.danjou.info/blog/2012/logitech-k750-linux-support
 - http://www.usbmadesimple.co.uk/ums_5.htm
 - https://docs.mbed.com/docs/ble-hid/en/latest/api/md_doc_HID.html
 - https://nigibox.wordpress.com/2009/03/20/usb-sniffing-in-linux/
 - https://technolinchpin.wordpress.com/2016/01/11/usb-tracing-in-linux
 - https://github.com/DIGImend/usbhid-dump
 - [AVR068: STK500 Communication Protocol](http://www.atmel.com/images/doc2591.pdf)
 - Avrdude's 
   - [code](https://github.com/sigmike/avrdude/blob/master/usb_libusb.c) where it handles USB communications
   - [CMD_*](https://github.com/sigmike/avrdude/blob/master/stk500v2_private.h) codes
 - [Everything You Always Wanted to know about Arduino Bootloading but Were Afraid to Ask](http://baldwisdom.com/bootloading/)
 - [pyreshark](https://github.com/ashdnazg/pyreshark) A Wireshark plugin providing a simple interface for [writing](https://github.com/ashdnazg/pyreshark/wiki/Writing-Dissectors) dissectors in Python
 - [Dump packet 'Leftover Data Capture' field only?](https://ask.wireshark.org/questions/43330/dump-packet-leftover-data-capture-field-only)
 - [Maybe USB doesn't support desegmentation](https://stackoverflow.com/questions/38630416/wireshark-lua-dissector-reassembly-dissector-not-called-with-previous-tvbs-da)


