<!--
.. title: Sending command to an Anet A8 3d printer by the serial port with python
.. slug: sending-commands-to-anet
.. date: 2018-02-25 00:00:00
.. tags: serial,programming,python,Anet,DIY
.. category: 
.. link: 
.. description: 
.. type: text
-->


Since last year I have an Anet A8, a 3d printer received from China as a kit
and that I use as you can expect to print 3d models and experiment with this
technology.

In this post I want to describe a thing that is very simple but that is not
(probably) well known: the board that manages the functionality of this device
is (in the majority of the cases) an arduino-like system that receives commands
via a serial port and acts accordingly enabling the various systems that compose
the printer, like stepper motors, bed heater etc...

The commands understood by this sistem of boards is called ``Gcode``, is a text based
language used primarly for movements in a 3d spaces; you can find a list of these commands
in the [page](http://reprap.org/wiki/G-code) of the RepRap site. Not all the commands
are implemented in all the firmwares (some of them don't make sense in a 3d printer).

A little problem that someone using a Linux system is that the baudrate used with these systems
is a not standard one: 250000 and in some cases it's tricky to make the OS accepts this value.
Check the ``set_special_baudate()`` function in the [module](https://github.com/gipi/anet-scanner/blob/cdab1597b5c753efa4afe278b54f1ae806002d57/anet/serial.py) below:

```python
'''
For more information about GCODE take a look at <http://reprap.org/wiki/G-code>.
'''
from __future__ import absolute_import
import array
import ctypes
import fcntl
import logging
import time
import os
import serial
from cmd import Cmd


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SerialCmd(Cmd):
    def __init__(self, printer):
        Cmd.__init__(self)
        self.printer = printer

    def _query(self, msg):
        self.printer.write('%s\r\n' % msg)

        # we need to wait a little bit in order
        # to receive the output
        while self.printer.in_waiting == 0:
            time.sleep(0.5)

        response = ''
        while self.printer.in_waiting > 0:
            response += self.printer.readline()
            #time.sleep(0.5)

        return response

    def do_query(self, args):
        print self._query(args)

    def do_firmware(self, args):
        '''Get firmware version and capabilities'''
        print self._query('M115')

    def do_origin(self, args):
        '''Move to origin the printer head'''
        self.printer.write('G28\n')
        response = self.printer.readline()

        print response

    def do_sdcard(self, args):
        print self._query('M20')

    def do_quit(self, args):
        '''quit the shell'''
        raise SystemExit


# from /usr/lib/python2.7/site-packages/serial/serialposix.py
# /usr/include/asm-generic/termbits.h for struct termios2
#  [2]c_cflag [9]c_ispeed [10]c_ospeed
def set_special_baudrate(fd, baudrate):
    TCGETS2 = 0x802C542A
    TCSETS2 = 0x402C542B
    BOTHER = 0o010000
    CBAUD = 0o010017
    buf = array.array('i', [0] * 64) # is 44 really
    fcntl.ioctl(fd, TCGETS2, buf)
    buf[2] &= ~CBAUD
    buf[2] |= BOTHER
    buf[9] = buf[10] = baudrate
    assert(fcntl.ioctl(fd, TCSETS2, buf)==0)
    fcntl.ioctl(fd, TCGETS2, buf)
    if buf[9] != baudrate or buf[10] != baudrate:
        print("failed. speed is %d %d" % (buf[9],buf[10]))
        sys.exit(1)


def open_serial(device_path='/dev/ttyACM0', baudrate=250000):
    logger.info('opening serial device \'%s\' with baudrate set to %d' % (device_path, baudrate))
    fd = os.open(device_path, os.O_RDWR)
    set_special_baudrate(fd, baudrate)

    device = serial.Serial(device_path, baudrate)

    logger.info('please wait, the device will reset in a few seconds')
    # we need to wait a little bit to allow the port to be opened
    # and the device to be reset
    import time;time.sleep(5)

    banner = "\n"
    while device.in_waiting > 0:
        banner += device.readline()

    logger.info('BANNER: %s' % banner)

    return device

if __name__ == '__main__':
    device = open_serial()

    shell = SerialCmd(device)
    shell.prompt = 'anet> '
    shell.cmdloop('starting...')

    device.close()
```

With this script is possible to interact with the serial with some commands
preconfigured; below an example: first of all launch the script and wait for
the prompt.

```
$ python -m anet.serial
INFO:__main__:opening serial device '/dev/ttyACM0' with baudrate set to 250000
INFO:__main__:please wait, the device will reset in a few seconds
INFO:__main__:BANNER: 
start test1
echo:Marlin 0721
echo: Last Updated: Apr 12 2017 12:22:44 | Author: (none, default config)
Compiled: Apr 12 2017
echo: Free Memory: 4534  PlannerBufferBytes: 1232
echo:SD card ok

starting...
anet>
```

You can find the commands available with the ``help`` command

```
anet> help

Documented commands (type help <topic>):
========================================
firmware  help  origin  quit

Undocumented commands:
======================
query  sdcard
```

At this point in time there are few commands:

```
anet> firmware
FIRMWARE_NAME:Marlin V1; Sprinter/grbl mashup for gen6 FIRMWARE_URL:http://www.mendel-parts.com PROTOCOL_VERSION:1.0 MACHINE_TYPE:Mendel EXTRUDER_COUNT:1
ok

anet> sdcard
Begin file list
/TESTFILE/TESTMODE/2016~1.GCO
/TESTFILE/TESTMODE/FZ-~1.GCO
/TESTFILE/TESTMODE/MAN~1.GCO
/TESTFILE/TESTMODE/PIGALL~1.GCO
/TESTFILE/TESTMODE/TEST-P~1.GCO
/TESTFILE/TESTMODE/TEST~1.GCO
/TESTFILE/TESTMODE/YZ87B3~1.GCO
/TESTFILE/TESTMODE/Z-LEFT~1.GCO
/TESTFILE/TESTMODE/Z-RIGH~1.GCO
echo:Cannot open subdir

PI_LVD~1.GCO
PI_GAP~1.GCO
PI_LVD~2.GCO
PIM_PO~1.GCO
A_CAT~1.GCO
End file list
ok
```

A fundamental command is ``query`` that allows to send directly raw text
to the printer: if you want to move of a vector-offset of ``(100, 100, 100)``
the head of the printer you have to type

```
anet> query X100 Y100 Z100
ok
```

(keep in mind that if you don't have endstop in one or more of those directions and
the offset move the head off the limits of you printer damage can happen!).


Now it's possible to abuse the 3d printer and use it as a [scanner](https://github.com/gipi/anet-scanner) or
maybe a PCB milling machine or whatever you want ;)
