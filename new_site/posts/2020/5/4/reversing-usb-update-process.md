<!--
.. title: Reversing the USB update process of a device
.. slug: reversing-usb-update-process
.. date: 2020-05-04 00:00:00
.. tags: WIP,reversing,MFC,C++,windows,ghidra
.. category: 
.. link: 
.. description: 
.. type: text
-->


I'm again at it: I have a device that I want to know how it works and I started
to reverse it, this time without any particular reason if not curiosity.

What I couldn't know was that I was entering a rabbit hole of biblic proportion
and this post is only the tip of the iceberg.

In this post I want to describe without any particular order, how to reverse
a C++ application and the USB protocol that it uses to update the firmware
on the device. I don't think this will be useful to anyone, let me know in
case it has changed your life :)

<!-- TEASER_END -->

I will use Ghidra and I will try to show how to do some specific steps and how
I approach reversing in general.

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

Analyzing the firmware opened a can of worms, since now I wanted to know how the upgrade process works.

## MFC C++

First of all, the application is using ``VC6`` (the magic in the ``FuncInfo`` struct is ``0x19930520``).

I opened ``ghidra`` and imported the binary: obviously I had no idea of what I
was doing so the initial phase was to start jumping around the calls tree: my
first thing that I do when reversing something is to rename functions,
variables etc... with labels that indicate something about them, if not just
to remember that is something I have already seen. It can seem something boring
and useless but I assure you that the brain is very good at spotting patterns
(maybe too much) and this helps a lot during the reversing process.

However, at some point, walking up to the call tree you arrive to a function that is not
called from no one and you are like "uhm, how is this possible?"; for example
the function at ``0x0040a050`` (that by the way is the function at the end calls
the one the uses the url described above).

Maybe the address is indicated somewhere, or the code is not disassembled yet;
using Ghidra you can look for direct reference using the menu ``Search > For Direct References``

![]({{ site.baseurl }}/public/images/reversing-usb-update-process/menu-search-direct-references.png)

and found that at ``0x004e02a4`` there is 4 bytes value corresponding at that address.

Right clicking on the address in the listing window and choosing ``Data > pointer`` from the menu
you can inform Ghidra that the address stores
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

that corresponds perfectly with what we are looking for. This struct is used to
describe "callback" from element of the GUi of the program represented by the MFC class.

At the end the layout in memory of a MFC class is the following

```
+ CRuntimeClass      <------------------------------.
+ Message Map data   <----------------------------------------.
 + ptr to MFC42.DLL::<super class>::messageMap()     |        |
 + ptr to AFX_MSGMAP_ENTRY array -.                  |        |
 + AFX_MSGMAP_ENTRY array  <------'                  |        |
  + 0th element                                      |        |
  + 1th element                                      |        |
   ...                                               |        |
  + last element (all elements are NULL)             |        |
+ MFC class' vtable                                  |        |
 + GetRuntimeClass() (returns a pointer to) ---------'        |
 + Destructor()                                               |
 + null()                                                     |
 + null()                                                     |
 + null()                                                     |
 + OnCmdMsg()                                                 |
  ...                                                         |
 + GetTypeLib()                                               |
 + GetMessageMap() (returns a pointer to) --------------------'
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
char *  m_lpszClassName 
dword   m_nObjectSize   
dword * m_pBaseClass    
dword * m_pfnCreateObject   
dword * m_pfnGetBaseClass   
dword   m_wSchema   
```

**Remember:** you can follow the ``GetRuntimeClass()`` into the original library
and find out the size of the class so to have an idea of how much space a class
is going to occupy in memory (and in particular it's very useful for local variables
in the stack).

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

You can read on the official documentation

 - [message maps](https://docs.microsoft.com/en-us/cpp/mfc/tn006-message-maps).
 - [CCmdTarget](https://docs.microsoft.com/en-us/cpp/mfc/reference/ccmdtarget-class)
 - [CWinApp](https://docs.microsoft.com/it-it/cpp/mfc/reference/cwinapp-class)

or an article about ``CString`` internals in VC6

 - [CString In A Nutshell](https://www.codeguru.com/cpp/cpp/string/article.php/c2789/CString-In-A-Nutshell.htm)

bad enough this application uses ``mfc42.dll`` that is a library with API not completly
"forward" compatible with the one existing today.

You can organize smartly the functon into class moving the function in the classes with the mouse
once that you put the function into the right hierarchy, ``__thiscall`` set the ``ecx`` register
to the right type (be aware that the struct connected to the class must have the same name, it's obvious
you know, until you name one ``Whatever`` and the other ``WhateverClass``).

### Subclasses

The classes that are used in the application are

| Name | Description |
|------|-------------|
| ``CPageUpdateClass``   | |
| ``CDialogUpdateClass`` | |


```
explicit CDialog(
    UINT nIDTemplate,
    CWnd* pParentWnd = NULL);

UINT GetDlgItemTextA(
  HWND  hDlg,
  int   nIDDlgItem,
  LPSTR lpString,
  int   cchMax
);

BOOL SetDlgItemTextA(
  HWND   hDlg,
  int    nIDDlgItem,
  LPCSTR lpString
);
```

after ``doModal()`` there is ``initDialog()``

The general organization of the vtable is the following

```
GetRuntimeClass
???
nullsub
nullsub
nullsub
OnCmdMsg
OnFinalRelease
IsInvokeAllowed
GetDispatchIID
GetTypeInfoCount
GetTypeLibCache
GetTypeLib
GetMessageMap
GetCommandMap
GetDispatchMap
GetConnectionMap
GetInterfaceMap
GetEventSinkMap
OnCreateAggregates
GetInterfaceHook
GetExtraConnectionPoints
GetConnectionHook
PreSubclassWindow
Create
DestroyWindow
PreCreateWindow
CalcWindowRect
OnToolHitTest
GetScrollBarCtrl
WinHelpA
ContinueModal
EndModalLoop
OnCommand
OnNotify
GetSuperWndProcAddr
???
_function_shared
CPage_ECDkey::FUN_00401fa0
PreTranslateMessage
OnAmbientProperty
WindowProc
OnWndMsg
DefWindowProcA
PostNcDestroy
OnChildNotify
CheckAutoCenter
IsFrameWnd
SetOccDialogInfo
DoModal
OnInitDialog
OnSetFont
OnOK
OnCancel
PreInitDialog
```


## Windows quirks

For someone like me, coming from linux, some aspects of the runtime of Windows
are very puzzling

### Libraries resolution

This is the most WTF of all: the external call to a function placed in a library is identified by an ``id``
so you cannot know the name of the function called if you don't have the library and in my case
I have some API that are mismatched from the one recognnized by ghidra (it's obvious since in every
place where those functions are used the stack goes banana).

Maybe I'm missing something here but how in the world someone could think that using an id was a good idea?

### Calling conventions

Internally this application uses all the possible families of calling convention
that I list here

| Name | Arguments | Stack cleaning | Return value |
|------|-------------|
| ``cdecl``   | passed on the stack in reverse order | by the caller | ``eax`` |
| ``stdcall`` | passed on the stack in reverse order | callee | ``eax`` |
| ``fastcall`` | passed via registers | by the caller | ``eax`` |
| ``thiscall`` | used with class's methods, ``ecx`` contains the ``this`` pointer and the arguments are on the stack on the reverse order | | ``eax`` |

If ghidra mis-recognize the calling convention of a function you will see something strange happening
to the local variables.

### Resources

Inside a Windows executable is possible to use a particular section (named ``.rsrc``)
for storing **resources**, like icon, images etc... and load it during the execution
with appropriate calls, like ``FindResourceA(hModule,(LPCSTR)((uint)rsrc_id & 0xffff),type)``.

This can be useful to "connect the dots" to particular functionality: in the application
exists the function ``loadRsrc()`` that takes a parameter identifying the resource
and set a particular field of the class to the resource: you can see that is possible
to directly see what icon corresponds to what resource from ghidra

![]({{ site.baseurl }}/public/images/reversing-usb-update-process/resources.png)

Strange that from the symbol tree pane I see the PNGs and them have the xref to the
function but the call to ``loadRsrc()`` doesn't have the xref back (if not a ``= <PNG-Image>`` comment
in the listing window that doesn't jump to the resource).

It's possible also to reconstruct some custom dialog using the resource
id passed as argument to the constructor of ``CDialog()``

![]({{ site.baseurl }}/public/images/reversing-usb-update-process/dialog.png)

## Internal state

There is a global variable used to handle the internal state of the GUI at ``0x00594e78``
and it's processed mainly at ``0x00409a20`` by a function named by me ``setState()``;
this function is pretty interesting since allows to know what state corresponds to what
number via the messages that presents to the user and so you can create a wonderful enum :)

Also there are pieces of the interfaces that are set, like the PNGs etc...

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

If we take a look at the first 200 bytes of the firmware we have some hints that
is structured into different sections:

```
00000000: 4163 7469 6f6e 7346 6972 6d77 6172 6500  ActionsFirmware.
00000010: 5570 6461 7465 5665 723a 7631 2e33 3100  UpdateVer:v1.31.
00000020: 4348 4543 4b53 554d 0000 0000 0000 0000  CHECKSUM........
00000030: 4000 0000 c0fd b801 0000 0000 b59b c093  @...............
00000040: 434f 4d50 5245 5353 0000 0000 0000 0000  COMPRESS........
00000050: 0000 0000 0000 0000 00b2 4100 00de 9d00  ..........A.....
00000060: 4144 4543 6164 6675 7300 0000 0000 0000  ADECadfus.......
00000070: 0004 0000 0020 0000 0000 04b4 0000 0000  ..... ..........
00000080: 4144 4655 6164 6675 7300 0000 0000 0000  ADFUadfus.......
00000090: 0024 0000 1826 0000 0000 00a0 0000 0000  .$...&..........
000000a0: 4857 5343 6877 7363 0000 0000 0000 0000  HWSChwsc........
000000b0: 004c 0000 102a 0000 0000 01a0 0000 0000  .L...*..........
000000c0: 4636 3438 6677 7363 0000 0000 0000 0000  F648fwsc........
000000d0: 0078 0000 2091 0100 0080 01a0 0000 0000  .x.. ...........
000000e0: 4636 3438 6d62 7265 6300 0000 0000 0000  F648mbrec.......
000000f0: 000a 0200 001a 0000 0000 01a0 0040 04b4  .............@..
00000100: 4636 3438 6272 6563 0000 0000 0000 0000  F648brec........
00000110: 0024 0200 0000 0200 0000 0000 1000 0000  .$..............
00000120: 4649 524d 0000 0000 9879 f68a e33c 4541  FIRM.....y...<EA
00000130: 0024 0400 0000 9e00 00de 9d00 c304 2400  .$............$.
00000140: 4c49 4e55 5800 0000 0000 0000 0000 0000  LINUX...........
00000150: 0100 0000 0000 e000 0300 0000 0000 0000  ................
00000160: 726f 6f74 6673 0000 0000 0000 0000 0000  rootfs..........
00000170: 002a 2800 0000 0004 0000 0004 8300 0100  .*(.............
00000180: 7573 6572 3100 0000 0000 0000 0000 0000  user1...........
00000190: 00f0 8b01 0000 8000 0000 8000 8300 0100  ................
000001a0: 7672 616d 0000 0000 0000 0000 0000 0000  vram............
000001b0: 00a4 b801 005a 0000 0000 1000 0b00 0000  .....Z..........
000001c0: 7265 7365 7276 6500 0000 0000 0000 0000  reserve.........
000001d0: 0000 0000 0000 0000 0000 0002 0000 0000  ................
000001e0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
000001f0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
```

it seems that the header is composed of header sections of 32 bytes each,
let's see if we are able to understand the structure of them.

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

The ``LINUX`` parsing is done at ``0x00417ae0`` and it's the more puzzling piece
because some values don't make sense: this is an example

```
00000140        4c 49 4e 55         section_t
                58 00 00 00 
                00 00 00 00 
   00000140 4c 49 4e 55 58  char[16]  "LINUX"                 name
            00 00 00 00 00 
            00 00 00 00 00
   00000150 01 00 00 00     ddw       1h                      ?????
   00000154 00 00 20 00     ddw       200000h                 ?????
   00000158 02 00 00 00     ddw       2h                      n_subsections
   0000015c 00 00 00 00     ddw       0h                      ????
```

at ``0x14`` and ``0x1c`` there is something used elsewhere. The interesting fact
is that is possible to have a ``reserve`` section that doesn't seem to indicate
actual data in the OTA but some metadata.

The dword at offset ``0x18`` indicates the number of subsections to read: the name
of the subsections doesn't imply anything.

The ``FIRM`` instead at ``0x0040ef10``; at ``0x00406e80`` is manipulating
the first ``0x80`` bytes copied in memory

At this point the smart reader could ask about the other sections, like ``ADECadfus``,
``ADFUadfus`` etc... that part will be investigated in the next post where I'll take
 a look more in detail in the internal working(?) of this family of chips.

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


seems that ghidra can handle this with ``alloca_probe``

## GZIP

An interesting part is where the code gunzip the ``FIRM`` section at ``0x00414d50``:
it doesn't seem to be depending from parameters as I thought initially (I have firmwares
from other Actions' devices that don't compress that part).

It's the first time I recognize the format following the [specification](https://tools.ietf.org/html/rfc1952).

## AWK

Function at ``0x004111d0`` does some magic with ``awk`` to parse
```
%s -v BS=\ "{if($NF==BS){$NF=NULL;line=line $0;}else{print line $0;line=NULL;}}" %s |%s -F# -v SP=" " "$1{gsub(/\t/,SP,$1);gsub(/rd_size=__FIX_ME_ON_PACK__/,\"rd_size=0x%08x\",$1);print $1}" > %s
```

## Partitions

At ``0x00416660`` the application builds what seems to be the **Native MBR** using
the information extracted during the parsing of the ``LINUX`` portion of the firmware

## USB communication protocol

The mechanism that the application uses to update the firmware is by a custom
``USB`` protocol on top of the [mass storage](https://www.usb.org/sites/default/files/usbmassbulk_10.pdf);
the core of it is the **Command Block Wrapper** (``CBW``) a packet of 31 bytes (yeah, 31) having the
following organization:

```
  .----.----.----.----.
  | U    S    B    C  |
  |----|----|----|----|
  |        tag        |
  |----|----|----|----|
  |   transferLength  |
  |----'----'----'----'
  | Fl | LU | CL |    |
  |----|----|----|....|
  |                   |
  |....|....|....|....|
  |                   |
  |....|....|....|....|
  |         |         |
  |....|....|....|....'
  |              |
  '....|....|....'
```

the "custom" part is inside ``CBWCB``.

```c
struct cmd_block_t {
    byte cmd;
    dword arg0;
    dword arg1;
    short subCmd;
    short subCmd2;
};

struct CBW_t {
    byte[4] signature;
    dword tag;
    dword transferLength;
    byte flags;
    byte LUN;
    byte cmdLength;
    struct cmd_block_t cmdBlock;
    byte padding[3];
};
```

The typical code is the following

```
  CBW_t localCBW;

  /* first it copies the 31 bytes of the pre-filled packet */
  int counter = 7;
  dword* cbw = (dword *)&GLOBAL_CBW_PACKET;
  dword* ref2localCBW = (dword *)&localCBW;
  while (counter != 0) {
    counter = counter + -1;
    *ref2localCBW = *cbw;
    cbw = cbw + 1;
    ref2localCBW = ref2localCBW + 1;
  }
  /* this strange assignment exists because there are the three remaining bytes*/
  *(undefined2 *)ref2localCBW = *(undefined2 *)cbw;
  *(undefined *)((int)ref2localCBW + 2) = *(undefined *)((int)cbw + 2);

  /* then it fills the values needed for the wanted function */
  localCBW.transferLength = transferLength;
  localCBW.cmdBlock.arg0 = arg0;
  localCBW.cmdBlock.arg1 = arg1;

  /* it then sends the packet to the device */
  retValue = USB_Write(&localCBW,0x1f,usbIndex);

  /*
   * here can happen some data upload/download from the device
   * depending on the command
   */

  /* the device sends the response of the command */
  retValueResponse = USB_ReadFile(responseBuffer,0xd,index);

```
