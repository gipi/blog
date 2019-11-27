---
layout: post
comments: true
title: "Reversing the USB update process of a device"
tags: [reversing,MFC,C++,windows,ghidra]
---

I'm again at it: I have a device that I want to know how it works and I start
to reverse it, this time without any particular reason if not curiosity.

In this post I want to describe without any particular order, how to reverse
a C++ application and the USB protocol that it uses to update the firmware
on the device.

I will use Ghidra and I will try to show how to do some specific steps.

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

and in particular ``GetRuntimeClass()`` gives us the class this vtable
belongs to; instead if you want the constructor you need to look at the
function referencing the vtable:

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

Some of these tables have as the first function something that ghidra doesn't recognize
as a ``GetRuntimeClass()``:

```
					 **************************************************************
					 *                          FUNCTION                          *
					 **************************************************************
					 undefined * * __stdcall FUN_004192b0(void)
	 undefined * *     EAX:4          <RETURN>
					 FUN_004192b0                                    XREF[1]:     004e0d40(*)  
004192b0   0      b8 90 0c        MOV        EAX=>PTR_s_CPage_ECDkey_004e0c90,PTR_s_CPage_E   = 0055fcf4
				  4e 00
004192b5   0      c3              RET
```

but in reality this is a custom object so the function returns the [CRuntimeStructure](https://docs.microsoft.com/en-us/cpp/mfc/reference/cobject-class?view=vs-2019#getruntimeclass)
for that object:

```
					 PTR_s_CPage_ECDkey_004e0c90                     XREF[2]:     FUN_004192b0:004192b0(*), 
																				  FUN_004192b0:004192b0(*)  
004e0c90          f4 fc 55 00     addr       s_CPage_ECDkey_0055fcf4                          = "CPage_ECDkey"
004e0c94          6c 41 00 00     ddw        416Ch
004e0c98          ff ff 00 00     ddw        FFFFh
004e0c9c          50 92 41 00     addr       FUN_00419250
004e0ca0          b0 3f 42 00     addr       FUN_00423fb0
004e0ca4          00 00 00 00     ddw        0h
```

obviously also the ``getMessageMap()`` method is custom.

You can read on the [official documentation](https://docs.microsoft.com/en-us/cpp/mfc/tn006-message-maps).

https://docs.microsoft.com/en-us/cpp/mfc/reference/ccmdtarget-class?view=vs-2019#syntax

## Firmware downloading and parsing

```c

int __cdecl download(CDialogUpdateClass *this)

{
  int iVar1;
  
  setState(this,DOWNLOADING_CONF);
  iVar1 = download_conf(this);
  if (iVar1 == 0) {
    setState(this,RETRY_SERVER);
    return 1;
  }
  setState(this,UPGRADE);
  return 1;
}
```

```c

/* Here get the response from the server with FW and CONF urls,
   but also downloads the conf. */

int __fastcall download_conf(CDialogUpdateClass *this)

{
  char *response;
  int iVar1;
  
  response = (char *)client_do_request(s_https://www.iezvu.com/upgrade/ot_0055e0ec,
                                       (char *)&this->json);
  if (response == NULL) {
    return 0;
  }
                    /* here seems that the function takes like three args
                       but internally doesn't use the last two */
  parse_response(response,(char *)&this->ota_conf_file,(char *)&this->ota_fw_file);
  free(response);
  iVar1 = downloading_at((char *)&this->ota_conf_file,(char *)&this->Upgrade.con_path);
  if (iVar1 != 0) {
    return 0;
  }
  getServerVersionFromConfFile(this);
  return 1;
}
```

The core of what interest us is at ``0x00408d50``:

```c

int __cdecl update(CDialogUpdateClass *this)

{
  int downloadStatus;
  
  downloadStatus = download_firmware(this);
  if (downloadStatus != 0) {
    setState(this,DOWNLOAD_FIRMWARE_FAILED);
    return 0;
  }
  firmware_open_and_parse(this);
  return 1;
}
```

00408d80 download_firmware()

```c
void __fastcall download_firmware(CDialogUpdateClass *this)

{
  setState(this,DOWNLOADING_FIRMWARE);
  downloading_at((char *)&this->ota_fw_file,(char *)&this->Upgrade.tmp_path);
  return;
}
```

After downloading the file from the remote server and saving it in ``Upgrade.tmp`` (this path is
set by the routine that starts at ``0x0040882c``) the application parses it.


The function ``firmware_open_and_parse()`` located at ``0x00408b00`` then opens the
downloaded firmware using a global ``CFile`` instance located at ``0x00593858``
that will be used from other parts of the application to act on the firmware itself
or on other kind of files.

The next step parses finally the firmware at ``0x0040e7a0``: first of all the first
16 bytes **must contain** the header of the firmware with the string ``ActionsFirmware``

A interesting part is the handling of the ``CHECKSUM`` section: if there isn't
such section there is some code to decrypt, however if there is a section
with that name then read some values and calculate the checksum

```

00000020 43 48 45 43 4b  char[16]  "CHECKSUM"              checksum
         53 55 4d 00 00 
         00 00 00 00 00
00000030 40 00 00 00     ddw       40h                     start
00000034 c0 ed 66 00     ddw       66EDC0h                 size
00000038 00 00 00 00     ddw       0h                      encriptedFlag
0000003c 5a fa ad 12     ddw       12ADFA5Ah               checksum
```

the function is at ``0x00407510``

```
int __cdecl checksum(void *buffer,uint size)

{
  int ctr;
  byte bVar1;
  uint nDword;
  dword *ptrBuffer;
  int iVar2;
  dword tmp;
  
  ctr = 0;
  nDword = size >> 2;
  ptrBuffer = (dword *)buffer;
  while (nDword != 0) {
    tmp = *ptrBuffer;
    ptrBuffer = ptrBuffer + 1;
    ctr = ctr + tmp;
    nDword = nDword - 1;
  }
  if (ptrBuffer < (dword *)(size + (int)buffer)) {
    iVar2 = 0;
    do {
      bVar1 = (byte)iVar2;
      iVar2 = iVar2 + 8;
      ctr = ctr + ((uint)*(byte *)ptrBuffer << (bVar1 & 0x1f));
      ptrBuffer = (dword *)((int)ptrBuffer + 1);
    } while (ptrBuffer < (dword *)(size + (int)buffer));
  }
  return ctr;
}
```

After that check for the sections named ``LINUX`` and ``FIRM``, with the last one **mandatory**.

```
00000120        46 49 52 4d         section_t
                00 00 00 00 
                9a 0b f0 dc 
   00000120 46 49 52 4d 00  char[16]  "FIRM"                  name
            00 00 00 9a 0b 
            f0 dc a1 74 bf
   00000130 00 de 01 00     ddw       1DE00h                  start_address
   00000134 00 00 17 00     ddw       170000h                 ???
   00000138 00 ce 16 00     ddw       16CE00h                 size
   0000013c df c6 16 00     ddw       16C6DFh                 unk1
```

```
00000140        4c 49 4e 55         section_t
                58 00 00 00 
                00 00 00 00 
   00000140 4c 49 4e 55 58  char[16]  "LINUX"                 name
            00 00 00 00 00 
            00 00 00 00 00
   00000150 01 00 00 00     ddw       1h                      start_address
   00000154 00 00 20 00     ddw       200000h                 length
   00000158 02 00 00 00     ddw       2h                      n_subsections
   0000015c 00 00 00 00     ddw       0h                      unk1
00000160        72 6f 6f 74         section_t
                66 73 00 00 
                00 00 00 00 
   00000160 72 6f 6f 74 66  char[16]  "rootfs"                name
            73 00 00 00 00 
            00 00 00 00 00
   00000170 00 a6 18 00     ddw       18A600h                 start_address
   00000174 00 50 4e 00     ddw       4E5000h                 length
   00000178 00 50 4e 00     ddw       4E5000h                 unk0
   0000017c 83 00 01 00     ddw       10083h                  unk1
00000180        76 72 61 6d         section_t
                00 00 00 00 
                00 00 00 00 
   00000180 76 72 61 6d 00  char[16]  "vram"                  name
            00 00 00 00 00 
            00 00 00 00 00
   00000190 00 a0 66 00     ddw       66A000h                 start_address
   00000194 00 4e 00 00     ddw       4E00h                   length
   00000198 00 00 08 00     ddw       80000h                  unk0
   0000019c 0b 00 00 00     ddw       Bh                      unk1
```

The ``LINUX`` parsing is done at ``0x00417ae0``

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

Since this function messup the stack, every function that uses it makes ghidra lose tracking of
the local variables after the call.

The best way to deal with it is to set stack depth change to minus the offset plus four (I don't know why...
probably there is a disalignment between the listing and decompilation windows)

## GZIP

An interesting part is where the code gunzip the firmware at ``0x00414d50``

## AWK

Function at ``0x004111d0`` does some magic with ``awk`` to parse
```
%s -v BS=\ "{if($NF==BS){$NF=NULL;line=line $0;}else{print line $0;line=NULL;}}" %s |%s -F# -v SP=" " "$1{gsub(/\t/,SP,$1);gsub(/rd_size=__FIX_ME_ON_PACK__/,\"rd_size=0x%08x\",$1);print $1}" > %s
```

## Firmware uploading

## Internal state

There is a global variable used to handle the internal state of the GUI at ``0x00594e78``
and it's processed mainly at ``0x00409a20`` by a function named by me ``setState()``;
this function is pretty interesting since allows to know what state corresponds to what
number via the messages that presents to the user and so you can create a wonderful enum :)

Also there are pieces of the interfaces that are set, like the PNGs etc...

## USB

The mechanism that the application uses to update the firmware is by a custom
``USB`` protocolo on top of the mass storage

## Flash

It's better to knwo the underlying techniology, for example at ``0x00416240``
there is a routine that checks for ``0xff``

## bare metal execution

the piece of the OTA contains piece of code

remember to set the correct address mapping before analyze them in ghidra
