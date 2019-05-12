---
layout: post
comments: true
title: "Reversing the USB update process of a device"
tags: [reversing,MFC,C++,windows,ghidra]
---

I'm again at it: I have a device that I want to know how it works and I start
to reverse it, this time without any particular reason if not curiosity.

I want to describe the process of using Ghidra to reverse.

## Context

The device is the **EZCast** bought on Aliexpress for like ten euro, I never used much
since I have a Chromecast but out of curiosity I have opened it and soldered the serial
on the two exposed pads and accessed the (root) shell.

It has an update process via ``USB`` by a Windows application that you can download from their site.
The ``md5`` of this application is ``8cad508dddcbb11f67297e79609c2561`` (I have seen two different versions
during my experiments).

I never run it since I'm a Linux guy; some time ago I started playing with it and with a spell of mine
I found out an interesting ``URL``:

```
$ strings MiraScreen/EZCastToolDriver/EZUpdate.exe  | grep http
 ...
https://www.iezvu.com/upgrade/ota_rx.php
 ...
```

right now I don't remember how (probably I stumbled upon some json strings), but I found the right payload for a request

```
$ curl -X POST -H "Content-type: application/json; charset=utf-8" -i https://www.iezvu.com/upgrade/ota_rx.php -d'{
        "version":      1,
        "vendor":       "ezcast",
        "mac_address":  "authorshxj",
        "softap_ssid":  "000000-00000000",
        "firmware_version":     "0"
}'
HTTP/2 200
server: nginx
date: Wed, 16 Aug 2017 16:03:02 GMT
content-type: text/html; charset=utf-8
vary: Accept-Encoding
x-powered-by: PHP/5.5.9-1ubuntu4.21

{"ota_conf_file":"http://cdn.iezvu.com/upgrade/ezcast/ezcast-16224000.conf","ota_fw_file":"http://cdn.iezvu.com/upgrade/ezcast/ezcast-16224000.gz","ota_enforce":true}
$ curl -X POST -H "Content-type: application/json; charset=utf-8" -i https://www.iezvu.com/upgrade/ota_rx.php -d'{
        "version":      1,
        "vendor":       "mirawire_8252n",
        "mac_address":  "authorshxj",
        "softap_ssid":  "000000-00000000",
        "firmware_version":     "0"
}'
HTTP/2 200
server: nginx
date: Wed, 16 Aug 2017 16:14:38 GMT
content-type: text/html; charset=utf-8
vary: Accept-Encoding
x-powered-by: PHP/5.5.9-1ubuntu4.21

{"ota_conf_file":"http://cdn.iezvu.com/upgrade/mirawire_8252n_8M/mirawire_8252n_8M-16285000.conf","ota_fw_file":"http://cdn.iezvu.com/upgrade/mirawire_8252n_8M/mirawire_8252n_8M-16285000.gz","ota_enforce":false}
```

and downloaded the firmware update at the url indicated in the field ``ota_fw_file``.

Analyzing the firmware opened a can of worms, since now I wanted to know how they work.

## MFC C++

Obviously I had no idea of what I was doing so the initial phase was to start jumping
around the calls tree: my first thing that I do when reversing something is to rename
functions, variables etc... with labels that indicates something about them, if not just
to remember that is something I have already seen. It can seem something boring and useless
but I assure you that the brain is very good at spotting patterns (maybe too much)
and this helps a lot during the reversing process.

However, at some point, walking up to the call tree you arrive to a function that is not
called from no one and you are like "uhm, how is this possible?"; for example
the function at ``0x0040a050`` (that by the way is the function at the end calls
the one the uses the url described above).

Maybe the address is indicated somewhere, or the code is not disassembled yet;
using Ghidra you can look for direct reference using the menu ``Search > For Direct References``

![]({{ site.baseurl }}/public/images/reversing-usb-update-process/menu-search-direct-references.png)

and found that at ``0x004e02a4`` there is 4 bytes value corresponding at that address.

Right clicking and choosing ``Data > pointer`` you can inform Ghidra that address stores
a pointer to a function (you can also define a shortcut for data type you use frequently,
I suggest you one for ``dword``).

Continuing to define as ``dword`` the values next to it you can see there is a pattern

![]({{ site.baseurl }}/public/images/reversing-usb-update-process/message-map-raw.png)

As I said previously, it is all about recognizing patterns, **reversing patterns**, and
in this case if you search for something related to reversing ``MFC`` you can find
an old [post](https://quequero.org/2008/08/guidelines-to-mfc-reversing/) of Quequero
where he describes the structure of this kind of application, in particular this
``struct``

```
struct AFX_MSGMAP_ENTRY
{
        UINT nMessage;   // windows message
        UINT nCode;      // control code or WM_NOTIFY code
        UINT nID;        // control ID (or 0 for windows messages)
        UINT nLastID;    // used for entries specifying a range of control id's
        UINT_PTR nSig;       // signature type (action) or pointer to message #
        AFX_PMSG pfn;    // routine to call (or special value)
};
```

that corresponds perfectly with what we are looking for.

At the end the scheme is

```
getMessageMap()
ptr to AFX_MSGMAP_ENTRY array

AFX_MSGMAP_ENTRY array

vtable
```
