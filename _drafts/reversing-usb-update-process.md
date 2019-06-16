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

At the end the layout in memory of a MFC class is the following

```
+ Message Map data   <----------------------------------------.
 + ptr to MFC42.DLL::<super class>::messageMap()              |
 + ptr to AFX_MSGMAP_ENTRY array -.                           |
 + AFX_MSGMAP_ENTRY array  <------'                           |
  + 0th element                                               |
  + 1th element                                               |
   ...                                                        |
  + last element (all elements are NULL)                      |
+ MFC class' vtable                                           |
 + GetRuntimeClass()                                          |
 + Destructor()                                               |
 + null()                                                     |
 + null()                                                     |
 + null()                                                     |
 + OnCmdMsg()                                                 |
  ...                                                         |
 + messageMap() (returns a pointer to) -----------------------'
  ...
```

All the destructors have a structure like

```
CDialog * __thiscall FUN_0040a4d0(void *this,byte param_1)

{
  FUN_0040a4f0((CDialog *)this);
  if ((param_1 & 1) != 0) {
    operator_delete(this);
  }
  return (CDialog *)this;
}
```


You can read on the [official documentation](https://docs.microsoft.com/en-us/cpp/mfc/tn006-message-maps).

https://docs.microsoft.com/en-us/cpp/mfc/reference/ccmdtarget-class?view=vs-2019#syntax

## Firmware downloading and parsing

00408d80 download_firmware()

After downloading the file from the remote server and saving it in ``Upgrade.tmp`` (this path is
set by the routine that starts at ``0x0040882c``) the application parses it.

The core of what interest us is at ``0x00408d50``:

```
int __cdecl update(CDialogUpdateClass *this)

{
  int downloadStatus;
  
  downloadStatus = download_firmware(this);
  if (downloadStatus != 0) {
    setState(this,8);
    return 0;
  }
  firmware_open_and_parse(this);
  return 1;
}
```

The function ``firmware_open_and_parse()`` located at ``0x00408b00`` then opens the
downloaded firmware using a global ``CFile`` instance located at ``0x00593858``
that will be used from other parts of the application to act on the firmware itself
or on other kind of files.

The next step parses finally the firmware at ``0x0040e7a0``: first of all the first
16 bytes **must contain** the header of the firmware with the string ``ActionsFirmware``

A interesting part is the handling of the ``CHECkSUM`` section

```

00000020 43 48 45 43 4b  char[16]  "CHECKSUM"              checksum
         53 55 4d 00 00 
         00 00 00 00 00
00000030 40 00 00 00     ddw       40h                     start
00000034 c0 ed 66 00     ddw       66EDC0h                 ???
00000038 00 00 00 00     ddw       0h                      encriptedFlag
0000003c 5a fa ad 12     ddw       12ADFA5Ah               checksum
```

### Intermezzo: stack_adjust

This is particular function that I encountered during my trip in the assembly land

```
        004dbf50   0    51                  PUSH                         ECX             <-- it's going to use ECX
        004dbf51 004    3d 00 10 00 00      CMP                          EAX,0x1000      <-- EAX must be passed as argument
        004dbf56 004    8d 4c 24 08         LEA                          ECX,[ESP + 0x8] <-- ECX = addr of 1st arg
 .----- 004dbf5a 004    72 14               JC                           LAB_004dbf70
 |                           LAB_004dbf5c
 | .--> 004dbf5c 004    81 e9 00 10         SUB                          ECX,0x1000
 | |                    00 00
 | |    004dbf62 004    2d 00 10 00 00      SUB                          EAX,0x1000
 | |    004dbf67 004    85 01               TEST                         dword ptr [ECX],EAX  <--- here it's make an AND between
 | |    004dbf69 004    3d 00 10 00 00      CMP                          EAX,0x1000
 | '--- 004dbf6e 004    73 ec               JNC                          LAB_004dbf5c
 |                           LAB_004dbf70
 '----> 004dbf70 004    2b c8               SUB                          ECX,EAX              <--- ECX points to addr 1st arg - EAX
        004dbf72 004    8b c4               MOV                          EAX,ESP              <--- EAX now points to the stack frame
        004dbf74 004    85 01               TEST                         dword ptr [ECX],EAX  <--- USELESS???
        004dbf76 004    8b e1               MOV                          ESP,ECX              <--- now use ECX as stack pointer (ghidra goes banana)
        004dbf78 - ? -  8b 08               MOV                          ECX,dword ptr [EAX]  <--- restore ECX
        004dbf7a - ? -  8b 40 04            MOV                          EAX,dword ptr [EAX + 0x4] <---. 
        004dbf7d - ? -  50                  PUSH                         EAX   <-----------------------'-- restore the return address so that
        004dbf7e - ? -  c3                  RET <------------------------------------------------------'   we jump back to the caller
```

probably is a "dynamic" allocation routine that uses the stack: it moves the stack pointer ``EAX`` bytes
below: indeed at the end of each function that uses this method there is a ``ADD ESP, <offset>`` that
restore the correct frame for the caller.

## Firmware uploading

## Internal state

There is a global variable used to handle the internal state of the GUI at ``0x00594e78``
and it's processed mainly at ``0x00409a20`` by a function named by me ``setState()``;
this function is pretty interesting since allows to know what state corresponds to what
number via the messages that presents to the user and so you can create a wonderful enum :)

Also there are pieces of the interfaces that are set, like the PNGs etc...
