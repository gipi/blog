<!--
.. title: Control a SIGLENT oscilloscope with Python
.. slug: control-siglent-oscilloscope
.. date: 2018-02-20 00:00:00
.. tags: electronics,python,programming,oscilloscope,VISA
.. category: 
.. link: 
.. description: 
.. type: text
-->


I'm an happy owner of a SIGLENT SDS1102CML, a entry level digital oscilloscope
with which I experiment when I do electronics.

I discovered that is possible to access its functionality using its ``USB`` port,
indeed if you connect this oscilloscope to a Linux system you can see that it recognizes
it

```
$ lsusb
 ...
Bus 003 Device 030: ID f4ec:ee3a Atten Electronics / Siglent Technologies
 ...
```


Reading the [Programming guide](https://www.siglentamerica.com/wp-content/uploads/dlm_uploads/2017/10/ProgrammingGuide_forSDS-1-1.pdf)
(or [this one](https://siglentna.com/wp-content/uploads/dlm_uploads/2017/10/ProgrammingGuide_forSDS-1-1.pdf))
the interested hacker can found that using [VISA](https://en.wikipedia.org/wiki/Virtual_instrument_software_architecture) i.e.
**Virtual instrument software architecture** it's possible to command this device.

``VISA`` it's a high-level API used to communicate with instrumentation buses and it's possible
to use with the python language by [pyvisa](https://pyvisa.readthedocs.io).

## VISA Installation

To install it you can simply use pip

```
$ pip install pyusb pyvisa pyvisa-py
```

and you can check the installation using

```
$ python -m visa info
Machine Details:
   Platform ID:    Linux-4.9.0-3-amd64-x86_64-with-debian-kebab
   Processor:

Python:
   Implementation: CPython
   Executable:     .virtualenv/bin/python
   Version:        2.7.14+
   Compiler:       GCC 7.2.0
   Bits:           64bit
   Build:          Dec  5 2017 15:17:02 (#default)
   Unicode:        UCS4

PyVISA Version: 1.8

Backends:
   ni:
      Version: 1.8 (bundled with PyVISA)
      Binary library: Not found
   py:
      Version: 0.2
      ASRL INSTR:
         Please install PySerial to use this resource type.
         No module named serial
      TCPIP INSTR: Available
      USB RAW: Available via PyUSB (1.0.2). Backend: libusb1
      USB INSTR: Available via PyUSB (1.0.2). Backend: libusb1
      GPIB INSTR:
         Please install linux-gpib to use this resource type.
         No module named gpib
      TCPIP SOCKET: Available
```

The important thing to check is that you have at least a backend available,
in this case the one named ``py`` was installed with the package ``pyvisa-py``.


## UDEV rules

First of all you need to configure your system to recognize the ``USB`` device and make it
accessible for a normal user; for a system with ``udev`` you can use the following rule

```
# SIGLENT SDS1102CML
SUBSYSTEMS=="usb", ACTION=="add", ATTRS{idVendor}=="f4ec", ATTRS{idProduct}=="ee3a", GROUP="plugdev", MODE="0660"
```

saved into ``/etc/udev/rules.d/`` with a file named like ``70-siglent.rules``.

You need to tell ``udev`` to reload its rules via ``sudo udevadm control --reload``.
Obviously your user must be in the right group (in this case ``plugdev``).

## Programming

At this point we can show the first lines necessary to connect to the oscilloscope:

```python
import visa
resources = visa.ResourceManager('@py')
probe = resources.open_resource("USB0::62700::60986::SDS10PA1164640::0::INSTR")
print probe.query("*IDN?")
```

The ``ResourceManager`` takes as parameter the backend name, if not indicated
the default one is used (i.e. ``ni``); in our case we have the python backend and
so we need to indicate explicitely.

Once opened the resource using the right identifier you can query the device with
commands described into the programming guided linked at the start of the post.

The thing to note when try to write a script is that the ``query()`` call is simply
a wrapper around ``write()`` and ``read()`` calls, and in case of binary data
exception related to encoding can happens. In these cases the ``read_raw()`` method
should be called.

The tricky part is that the responses are half ASCII and half binary data and parsing
them could be not foolproof.

## Source code

Below you can read an utility [script](https://github.com/gipi/electronics-notes/blob/master/test_visa.py) with a few commands implemented

```python
# encoding: utf-8
# See document "Programming Guide" at <https://www.siglentamerica.com/wp-content/uploads/dlm_uploads/2017/10/ProgrammingGuide_forSDS-1-1.pdf>
import sys
import logging
import argparse
import wave # https://docs.python.org/2/library/wave.html

import visa # https://pyvisa.readthedocs.io


logging.basicConfig()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def usage(progname):
    print 'usage: %s [list|dump]' % progname
    sys.exit(1)

def list(r):
    results = r.list_resources()

    for idx, result in enumerate(results):
        print '[%03d] %s' % (idx, result)


def waveform(device, outfile, channel):

    sample_rate = device.query('SANU C%d?' % channel)

    sample_rate = int(sample_rate[len('SANU '):-2])
    logger.info('detected sample rate of %d' % sample_rate)

    #desc = device.write('C%d: WF? DESC' % channel)
    #logger.info(repr(device.read_raw()))

    # the response to this is binary data so we need to write() and then read_raw()
    # to avoid encode() call and relative UnicodeError
    logger.info(device.write('C%d: WF? DAT2' % (channel,))) 

    response = device.read_raw()

    if not response.startswith('C%d:WF ALL' % channel):
        raise ValueError('error: bad waveform detected -> \'%s\'' % repr(response[:80]))

    index = response.index('#9')
    index_start_data = index + 2 + 9
    data_size = int(response[index + 2:index_start_data])
    # the reponse terminates with the sequence '\n\n\x00' so
    # is a bit longer that the header + data
    data = response[index_start_data:index_start_data + data_size]
    logger.info('data size: %d' % data_size)

    fd = wave.open(outfile, "w")
    fd.setparams((
        1,               # nchannels
        1,               # sampwidth
        sample_rate,     # framerate
        data_size,       # nframes
        "NONE",          # comptype
        "not compresse", # compname
    ))
    fd.writeframes(data)
    fd.close()

    logger.info('saved wave file')

def dumpscreen(device, fileout):
    logger.info('DUMPING SCREEN')

    device.write('SCDP')
    response = device.read_raw()

    fileout.write(response)
    fileout.close()

    logger.info('END')

def template(device):
    response = device.query('TEMPLATE ?')

    print response

def configure_opts():
    parser = argparse.ArgumentParser(description='Use oscilloscope via VISA')

    subparsers = parser.add_subparsers(dest='cmd', help='sub-command help')

    parser_a = subparsers.add_parser('list', help='list help')
    parser_wave = subparsers.add_parser('wave')
    parser_c = subparsers.add_parser('shell', help='VISA shell')
    parser_c = subparsers.add_parser('dumpscreen', help='dump screen')
    parser_template = subparsers.add_parser('template', help='dump the template for the waveform descriptor')

    parser_wave.add_argument('--device', required=True)
    parser_wave.add_argument('--out', type=argparse.FileType('w'), required=True)
    parser_wave.add_argument('--channel', type=int, required=True)

    parser_c.add_argument('--device', required=True)
    parser_c.add_argument('--out', type=argparse.FileType('w'), required=True)

    parser_template.add_argument('--device', required=True)

    return parser


if __name__ == '__main__':
    parser = configure_opts()
    args = parser.parse_args()

    resources = visa.ResourceManager('@py')

    if args.cmd == 'list':
        list(resources)
        sys.exit(0)
    elif args.cmd == 'shell':
        from pyvisa import shell
        shell.main(library_path='@py')
        sys.exit(0)

    device = resources.open_resource(args.device, write_termination='\n', query_delay=0.25)
    idn = device.query('*IDN?')

    logger.info('Connected to device \'%s\'' % idn)

    if args.cmd == 'wave':
        waveform(device, args.out, args.channel)
    elif args.cmd == 'dumpscreen':
        dumpscreen(device, args.out)
    elif args.cmd == 'template':
        template(device)

    device.close()
```

The commands are the following

### list

Simply shows the device recognized

```
$ python test_visa.py list
[000] USB0::62700::60986::SDS10PA1164640::0::INSTR
```

### shell

This is the shell available with ``pyvisa`` and by which is
possible to quickly test commands

```
$ python test_visa.py shell
Welcome to the VISA shell. Type help or ? to list commands.

(visa) list
( 0) USB0::62700::60986::SDS10PA1164640::0::INSTR
(visa) open USB0::62700::60986::SDS10PA1164640::0::INSTR
USB0::62700::60986::SDS10PA1164640::0::INSTR has been opened.
You can talk to the device using "write", "read" or "query.
The default end of message is added to each message
(open) query *IDN?
Response: *IDN SIGLENT,SDS1102CML,SDS10PA1164640,5.01.02.32
```

### wave

This is the more useful: dumps the trace stored into the oscilloscope
as a ``wav`` file.

```
$ python test_visa.py wave --device USB0::62700::60986::SDS10PA1164640::0::INSTR --out /tmp/wave.wav --channel 1
INFO:__main__:Connected to device '*IDN SIGLENT,SDS1102CML,SDS10PA1164640,5.01.02.32
'
INFO:__main__:detected sample rate of 11250
INFO:__main__:(28, <StatusCode.success: 0>)
INFO:__main__:data size: 20480
INFO:__main__:saved wave file
```

then you can import the file into ``audacity``

![trace imported into audacity as wave file](/images/audacity-import.png)

### dumpscreen

Sometime is useful to dump the LCD screen of the oscilloscope

```
$ python test_visa.py dumpscreen --device USB0::62700::60986::SDS10PA1164640::0::INSTR --out screen.bmp
```

![SIGLENT dumped screen](/images/siglent-screen.bmp)

## Conclusion

I think in the future I will return to this argument, in particular I want to
try to continously read data from the oscilloscope but probably that is not possible
for this kind of device, by the way there are a lot of commands that are missing
that can be useful to interact with.
