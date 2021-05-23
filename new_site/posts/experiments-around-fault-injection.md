<!--
.. title: Experiments with side channel attacks using the Chipwhisperer
.. slug: experiments-around-side-channels
.. date: 2021-06-01 00:00:00
.. tags: fault injection,hardware
.. status: draft
.. category: 
.. link: 
.. description: 
.. type: text
.. has_math: true
-->


I own a Chipwhisperer board, the [CWLITE](https://rtfm.newae.com/Capture/ChipWhisperer-Lite/) one, it's an open source, open
hardware device that allows to quickly setup and execute side channels related
attacks. 

For the following post I'm using as target the board attached with
the firmwares already present in the repository, identified in the wiki as the
[CW303](https://rtfm.newae.com/Targets/CW303%20XMEGA/).  It has as
microcontroller an Atmel's XMEGA128
([datasheet](https://static.chipdip.ru/lib/279/DOC000279729.pdf)).

In this post I'll explore some basic concepts: how to install the library,
update the firmware of the board and practicing with it.

<!-- TEASER_END -->

But before all of those, an introduction about the inner workings of processing
units and side channels.

## Model of a processing unit

To understand what follows you need a model of how a processing unit is composed
and how the single entities with their behaviour can tell us something about
what is happening during computation that wasn't supposed to leak to you.

Obviously this won't be an exhaustive explanation, this is matter of high
profile studies, but as a physicist I can tell you that sometimes from very basic
assumptions is possible to deduce very important aspects of a system.

You should think of a processing device in the same way you think about an old clock:
a source of motion, the pendulum, is transmitted via gears to show the correct
time on the display; in the same way an electronic device has a clock that
"gives the time" to its internal components!

Let me explain a little better: let's start with the founding entities of modern
digital electronics, i.e. **transistors**; they have a lot of property and a
huge usage that would be an enourmous task to explain in detail and it's of not
importance in our understanding in this case.

In modern ICs are used a type of transistor named **MOSFET**, the first half of
the name it's an acronym for **M**etal **O**xide **S**emiconductor, the second
half it's an acronym for **F**ield **E**ffect **T**ransitor; I would like to
start from the semiconductor part: not all materials are good in conducting
current, at one side of the spectrum there are metals (like copper, silver,
gold, etc...) and to the other side there are isolants (like glass, wood,
etc...). Each element has its own chemical properties characterized by the
external shell of electrons, in particular the property of forming bonds and
conductivity.

It's well known fact that digital devices are built from silicon: it's an
element with four electrons in its outer shell, this means that can bond with
another four atoms of the same type. Silicon it's a semiconductor and its
conductivity can be improved by **doping** it using element with one more or one
less electron in the outer shell, like boron or phosporous.

FET can have the following

 - polarity: p or n
 - gate insulation: JFET or MOSFET
 - channel doping: depletion or enhancement

{{% media url=https://www.youtube.com/watch?v=Bfvyj88Hs_o %}}

N-channel MOS transistors have the sub-strate material of p-type and the drain and gate voltages
are positive with respect to the source during normal operation. The substrate is
the most negative electrode of an nMOS transistor.

P-channel MOS transistors are produced on an n-type substrate. The voltages
at the gate and drain of these pMOS transistors are negative with respect to the
source during normal operation. The substrate is the most positive electrode.

Generally NMOS are faster than PMOS [^1]

[^1]: p26-27 nanometer CMOS ICs

For now it's important to model a
transistor as a "switch", as something that allows the flow of current by a
signal.

{{% pyplots %}}
# https://schemdraw.readthedocs.io/
import matplotlib
matplotlib.use('Agg')

import schemdraw
import schemdraw.elements as elm

d = schemdraw.Drawing()
d.add(elm.NFet()
    .reverse()
    .label("gate", loc="gate")
    .label("drain", loc="drain")
    .label("source", loc="source")
)
d.draw()
{{% /pyplots %}}

Another thing to take into account is the fact that ICs are built using ``CMOS``
technology, i.e., for each NMOS there is a PMOS (the **C** means **complementary**).
This has some advantages like power consumption. For example the typical
inverter is implemented in this way in a ``CMOS`` chip

{{% pyplots %}}
# CMOS inverter
import matplotlib
matplotlib.use('Agg')

import schemdraw
import schemdraw.elements as elm
d = schemdraw.Drawing()

# use the mosfet as starting elements
d += (pmos := elm.PFet().right().reverse().at((0, d.unit/2)).label('$Q_1$', 'right'))
d += (nmos := elm.NFet().right().reverse().at((0, -d.unit/2)).label('$Q_2$', 'right'))

# connect gates and drains
d += (gate_line := elm.Line().at((pmos, 'gate')).to(nmos.gate))
d += (drain_line := elm.Line().at((pmos, 'drain')).to(nmos.drain))

# use the midpoints of these two to place Vin and Vout
d += elm.LineDot().label('$V_{in}$', 'left').at(gate_line.center).left().length(1)
d += (Vout := elm.LineDot().at(drain_line.center).length(1).right().label('$V_{out}$', 'right'))

# last but not least, Vcc and Gnd
d += elm.LineDot().length(1).at(pmos.source).up().label('$V_{cc}$', 'right')
d += elm.Ground().at((nmos, 'source'))

d.draw()
{{% /pyplots %}}

This part is actually not needed to understand what follows but I put it here
anyway as my personal notes: the final die of an IC is costituted by at least
three different layers (from the top to the bottom)

 - **metal**: conducting material, pratically the inteconnecting wires
 - **polysilicon**: used for gates
 - **active**: doped silicon for drains and sources

This could be out of scope but it's interesting to see an actual implementation
in a IC of some digital components: take a look at the
[challenge by FlyLogic](http://www.siliconzoo.org/tutorial.html#flylogic) with the
[solution by Jeri Ellsworth](https://www.flickr.com/photos/jeriellsworth/2856054068/)
as shown in this image

![](/images/side-channels/dff.png)

If you are interested in stuff like this you can take a look at the
[reversing an FM synthesizer](https://www.wdj-consulting.com/blog/nmos-sample/)
that is a little more analogic.

From left to right we have an inverter having as input the ``RESET`` signal, followed
by two transmission gates

{{% pyplots %}}
import matplotlib
matplotlib.use('Agg')

import schemdraw
import schemdraw.elements as elm
d = schemdraw.Drawing()

d += (pfet_left := elm.PFet().up())
d += (nfet_left := elm.NFet().down())

d += (nfet_right := elm.NFet().up().at(nfet_left.drain))
d += (pfet_right := elm.PFet().down())

d += (clk_not := elm.Line().at(pfet_left.gate).to(nfet_right.gate))
d += (clk := elm.Line().at(nfet_left.gate).to(pfet_right.gate))

# CLK and NOT CLK lines
d += elm.LineDot().length(2).left().at(clk_not.start).label('$\overline{CLK}$', 'left')
d += elm.LineDot().length(2).left().at(clk.start).label('$CLK$', 'left')

# input and output
d += elm.LineDot().length(2).left().at(pfet_left.source).label('$input$', 'left')
d += elm.LineDot().length(2).right().at(pfet_right.source).label('$output$', 'right')

# extra reference points
d += elm.Dot().at(nfet_left.drain).label('$A$', 'top')
d += elm.Dot().at(pfet_right.source).label('$B$', 'top')

d.draw()
{{% /pyplots %}}

That (?) elements form a ``NAND`` gate:

{{% pyplots %}}
import matplotlib
matplotlib.use('Agg')

import schemdraw
import schemdraw.elements as elm
d = schemdraw.Drawing()

# place the PMOS in parallel
d += (pmos_a := elm.PFet().reverse().at((0, 0)).label('$A$', 'gate'))
d += (pmos_b := elm.PFet().reverse().at((d.unit, 0)).label('$B$', 'gate'))
d += (vdd_line := elm.Line().at(pmos_a.source).to(pmos_b.source))
d += (out_line := elm.Line().at(pmos_a.drain).to(pmos_b.drain))

# place the two NMOS in series
# (tricky placement of the NMOS_a in the middle of the output line)
d += (nmos_a := elm.NFet().reverse().anchor('drain').at(out_line.center).label('$A$', 'gate'))
d += (nmos_b := elm.NFet().reverse().label('$B$', 'gate'))

# VDD and GND
d += elm.LineDot().length(1).at(vdd_line.center).up().label('$V_{cc}$', 'right')
d += elm.Ground().at((nmos_b, 'source'))

# output
d += elm.LineDot().length(2).at(out_line.end).right().label('$out$', 'right')

d.draw()
{{% /pyplots %}}

https://www.eeweb.com/low-power-low-voltage-d-type-flip-flop/

All the above are what is called **combinatorial logic**, from the input I
obtain an output based entirely on it, it's **stateless**; but to build
something more complex we need **memory**.

A "primitive" circuit that accomplishes that is the following:

![](/images/side-channels/latch.png)

you notice that has two **stable** state and you can trigger them with the right
inputs; it's not immediate but from here is possible to construct something, so called
**flip-flop** that set the output from the input only at the **rising edge** of the clock:

From it the simplest "object" that is possible to build is the **register**: in the
example below four flip-flops are used to create a 4bits register

![](/images/side-channels/4-bits-register.png)

There is a lot of things possible with these objects but in general a
**sequential logic** has the following structure

![](/images/side-channels/combinatorial-logic.png)

in practice how many flip-flops as the number of bits needed to represent 
the internal state and a combinatorial logic part that does the calculation
needed in order to obtain the new state from the old one and the inputs.

For now this should be enough to understand the primitive building block of a
processing device, later I will elaborate a little more where the model just
described interacts with the physical world what can tell us and what we can do
to poke it :P

## Installation steps

This part is primarly for me in order to remember what I did to getting started,
you can see a more precise procedure in the [documentation](https://chipwhisperer.readthedocs.io/en/latest/installing.html).

```
$ git clone https://github.com/newaetech/chipwhisperer.git && cd chipwhisperer
$ git submodule update --init jupyter                        # To get the jupyter notebook tutorials
$ python3 -m pip install -r jupyter/requirements.txt --user
$ jupyter nbextension enable --py widgetsnbextension         # enable jpyter interactive widgets
$ python3 -m pip install -e . --user                         # use pip to install in develop mode
```

the jupyter part is related to the tutorials, if you don't need them, only clone and install.

```
$ avr-gcc \
    -Wall \
    -mmcu=atxmega128d3 \
    -o public/code/fi/firmware \
    public/code/fi/firmware.c
$ avr-objdump -d public/code/fi/firmware | less
```

```
$ make -C hardware/victims/firmware/simpleserial-base PLATFORM=CW303
```

```
python3
Python 3.7.5 (default, Oct 27 2019, 15:43:29)
[GCC 9.2.1 20191022] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> import chipwhisperer as cw
>>> scope = cw.scope()
>>> scope
cwlite Device
gain =
    mode = low
    gain = 0
    db   = 5.5
adc =
    state      = False
    basic_mode = low
    timeout    = 2
    offset     = 0
    presamples = 0
    samples    = 24400
    decimate   = 1
    trig_count = 226703590
clock =
    adc_src       = clkgen_x1
    adc_phase     = 0
    adc_freq      = 96000000
    adc_rate      = 96000000.0
    adc_locked    = True
    freq_ctr      = 0
    freq_ctr_src  = extclk
    clkgen_src    = system
    extclk_freq   = 10000000
    clkgen_mul    = 2
    clkgen_div    = 1
    clkgen_freq   = 192000000.0
    clkgen_locked = True
trigger =
    triggers = tio4
    module   = basic
io =
    tio1       = serial_tx
    tio2       = serial_rx
    tio3       = high_z
    tio4       = high_z
    pdid       = high_z
    pdic       = high_z
    nrst       = high_z
    glitch_hp  = False
    glitch_lp  = False
    extclk_src = hs1
    hs2        = None
    target_pwr = True
glitch =
    clk_src     = target
    width       = 10.15625
    width_fine  = 0
    offset      = 10.15625
    offset_fine = 0
    trigger_src = manual
    arm_timing  = after_scope
    ext_offset  = 0
    repeat      = 1
    output      = clock_xor
>>> target = cw.target(scope)
Serial baud rate = 38400
```

However you need to call the ``default_setup()`` in order to have all configured
correctly

```python
class OpenADC(ScopeTemplate, util.DisableNewAttr):
    """OpenADC scope object.  ..."""

    def default_setup(self):
        """Sets up sane capture defaults for this scope

         *  45dB gain
         *  5000 capture samples
         *  0 sample offset
         *  rising edge trigger
         *  7.37MHz clock output on hs2
         *  4*7.37MHz ADC clock
         *  tio1 = serial rx
         *  tio2 = serial tx

        .. versionadded:: 5.1
            Added default setup for OpenADC
        """
        self.gain.db = 25
        self.adc.samples = 5000
        self.adc.offset = 0
        self.adc.basic_mode = "rising_edge"
        self.clock.clkgen_freq = 7.37e6
        self.trigger.triggers = "tio4"
        self.io.tio1 = "serial_rx"
        self.io.tio2 = "serial_tx"
        self.io.hs2 = "clkgen"

        self.clock.adc_src = "clkgen_x4"

        ...
```

## Pinout

| Left | number | number | Right |
|------|--------|--------|-------|
| 5V   | 1 | 2 | GND |
| 3V3  | 3 | 4 | HS1/I |
| nRST | 5 | 6 | HS2/O (output clock and glitch) |
| MISO | 7 | 8 | VREF |
| MOSI | 9 | 10 | IO1 (serial RX) |
| SCK  | 11 | 12 | IO2 (serial TX) |
| PC   | 13 | 14 | IO3 |
| PD   | 15 | 16 | IO4 (used as a trigger) |
| GND  | 17 | 18 | 3V3 |
| GND  | 19 | 20 | 5V |

## Updating

```python
import chipwhisperer as cw
scope = cw.scope()
programmer = cw.SAMFWLoader(scope=scope)
programmer.enter_bootloader(really_enter=True)
programmer.program('/dev/ttyACM0', hardware_type='cwlite')
```

```
[1111253.064641] usb 2-10: USB disconnect, device number 27
[1111253.449854] usb 2-10: new high-speed USB device number 28 using xhci_hcd
[1111253.602083] usb 2-10: New USB device found, idVendor=03eb, idProduct=6124, bcdDevice= 1.10
[1111253.602086] usb 2-10: New USB device strings: Mfr=0, Product=0, SerialNumber=0
[1111253.630152] cdc_acm 2-10:1.0: ttyACM0: USB ACM device
[1111253.630322] usbcore: registered new interface driver cdc_acm
[1111253.630324] cdc_acm: USB Abstract Control Model driver for USB modems and ISDN adapters
```

## Power analysis

Let's start with something interesting: leak information about the computation
observing the power consumption of a device.

As I said in the introduction about the model, the "calculations" inside a
device are done, roughly speaking, switching on and off groups of transistors to
perform the needed operations; since the transistors are physical entities, they
interact with the physical world and need **energy** to move electrons around,
so we can imagine that the power consumption would be in some way connected with
the internal state of the processor.

For an extensive explanation you can use the book "Nanometer CMOS ICs, From Basics to ASICs" pg 161

The cwlite uses the [AD8331](https://www.analog.com/media/en/technical-documentation/data-sheets/AD8331_8332_8334.pdf) chip
and the [AD9215](https://www.analog.com/media/en/technical-documentation/data-sheets/AD9215.pdf)

### Different instructions

![](/images/side-channels/comparison-instructions.png)

### Correlation

In the last section I showed that different instructions have different
"footprints", probably the only possible way to use that is by timing analysis
or differential power analysis: for example if we had a piece of code that ask
for a password we could capture the power traces for each input character and
we should see only one trace having a different trace (this of course if the
algorithm is not costant-time).

But we can do better: as I described above, during the execution the transistors
composing the device are "turn on/off" based on the values of the computation,
in particular by the actual bits set and reset by the operations done.

![](/images/side-channels/correlation-ldi.png)

With our model we can now look for correlation between traces and the SBox-es
output: I'm going to use the following function to calculate it

```python
def correlation_trace_sbox_for_byte_at(key_guess, traces, texts, bnum, trace_avg, trace_stddev):
    """Correlation between trace values and hamming value
    for the bnum-th byte and key "key_guess"."""
    hws = np.array([[HW[aes_internal(textin[bnum], key_guess)] for textin in texts]]).transpose()
    hws_avg = mean(hws)
    
    return cov(traces, trace_avg, hws, hws_avg)/trace_stddev/std_dev(hws, hws_avg)
```

Plotting the correlation associated with the greatest value I obtain a very good
looking image of the internal of the algorithm:

![](/images/side-channels/correlation-sbox.png)

It's easy to distinguish between the various blocks of the first round of the key.

To check that what we are seeing makes sense, look at the code in ``simpleserial-aes`` that we flashed:
here there is the code that triggers the capture from the chipwhisperer


```c
/* This is the function that takes our input */
uint8_t get_pt(uint8_t* pt)
{
    aes_indep_enc_pretrigger(pt);
    
	trigger_high();

	aes_indep_enc(pt); /* encrypting the data block */
	trigger_low();
    
    aes_indep_enc_posttrigger(pt);
    
	simpleserial_put('r', 16, pt);
	return 0x00;
}
```

and here the outer most routines

```c
void aes_indep_enc(uint8_t * pt)
{
	AES128_ECB_indp_crypto(pt);
}

void AES128_ECB_indp_crypto(uint8_t* input)
{
  state = (state_t*)input;
  BlockCopy(input_save, input);
  Cipher();
}
```

``Cipher`` is what triggers the encryption, and its first operation is to
initialize the first round key

```c
// Cipher is the main function that encrypts the PlainText.
static void Cipher(void)
{
    uint8_t round = 0;

    // Add the First round key to the state before starting the rounds.
    AddRoundKey(0); 

  // There will be Nr rounds.
  // The first Nr-1 rounds are identical.
  // These Nr-1 rounds are executed in the loop below.
  for(round = 1; round < Nr; ++round)
  {
    SubBytes();
    ...
}
// This function adds the round key to state.
// The round key is added to the state by an XOR function.
static void AddRoundKey(uint8_t round)
{
  uint8_t i,j;
  for(i=0;i<4;++i)
  {
    for(j = 0; j < 4; ++j)
    {
      (*state)[i][j] ^= RoundKey[round * Nb * 4 + i * Nb + j];
    }
  }
}

// The SubBytes Function Substitutes the values in the
// state matrix with values in an S-box.
static void SubBytes(void)
{
  uint8_t i, j;
  for(i = 0; i < 4; ++i)
  {
    for(j = 0; j < 4; ++j)
    {
      (*state)[j][i] = getSBoxValue((*state)[j][i]);
    }
  }
}
```

To have an idea of the actual clock cycles we need to look at the assembly code
produced from the compiler

```text
[0x0000082a]> pdf @ sym.SubBytes 
            ; CALL XREFS from sym.Cipher @ 0x94e, 0x9c6
┌ 46: sym.SubBytes ();
│           0x00000848      20912223       lds r18, 0x2322
│           0x0000084c      30912323       lds r19, 0x2323
│           0x00000850      94e0           ldi r25, 0x04
│           ; CODE XREF from sym.SubBytes @ 0x872
│       ┌─> 0x00000852      d901           movw r26, r18  (1)
│       ╎   0x00000854      80e0           ldi r24, 0x00  (1)
│       ╎   ; CODE XREF from sym.SubBytes @ 0x868
│      ┌──> 0x00000856      ec91           ld r30, x      (2)
│      ╎╎   0x00000858      f0e0           ldi r31, 0x00  (1)
│      ╎╎   0x0000085a      e55f           subi r30, 0xf5 (1)
│      ╎╎   0x0000085c      fe4d           sbci r31, 0xde (1)
│      ╎╎   0x0000085e      4081           ld r20, z      (2)
│      ╎╎   0x00000860      4c93           st x, r20      (2)
│      ╎╎   0x00000862      8f5f           subi r24, 0xff (1)
│      ╎╎   0x00000864      1496           adiw r26, 0x04 (1)
│      ╎╎   0x00000866      8430           cpi r24, 0x04  (1)
│      └──< 0x00000868      b1f7           brne 0x856     (1/2)
│       ╎   0x0000086a      9150           subi r25, 0x01 (1)
│       ╎   0x0000086c      2f5f           subi r18, 0xff (1)
│       ╎   0x0000086e      3f4f           sbci r19, 0xff (1)
│      ┌──< 0x00000870      9111           cpse r25, r1   (1/2/3)
│      │└─< 0x00000872      efcf           rjmp 0x852     (2)
│      │    ; CODE XREF from sym.SubBytes @ 0x870
└      └──> 0x00000874      0895           ret
```

**Note:** look for the [Atmel AVR Instruction Set Manual](http://ww1.microchip.com/downloads/en/devicedoc/atmel-0856-avr-instruction-set-manual.pdf) to have a detailed
explanation of instructions and clock cycles.

If I plot all the traces above together and manually zoom for the actual time intervals

![](/images/side-channels/correlation-input-zoom.png)

I obtain the following values (the first row contains the time value of the most
correlated peak, the second row the difference between the adjacent ones)

```
1938  1994  2050  2106  2190  2246  2302  2358  2442  2498  2554  2610  2694  2750  2806  2862
    56    56    56    84    56    56    56    84    56    56    56    84    56    56    56
```

(I took the highest peaks as "markers"); since the ``ADC`` is capturing 4 times
the actual device's clock, we have the 14 and 21 clock cycles between the
operations. **This is what we have found looking at the assembly!**

But wait a moment: for sure there is also some instructions that interact with
the input bytes and we can do the same reasoning about correlation: using the
following function

```python
def correlation_trace_input_for_byte_at(traces, texts, bnum, trace_avg, trace_stddev):
    """Correlation between trace values and hamming value for the bnum-th byte of input."""
    hws = np.array([[HW[textin[bnum]] for textin in texts]]).transpose()
    hws_avg = mean(hws)
    
    return cov(traces, trace_avg, hws, hws_avg)/trace_stddev/std_dev(hws, hws_avg)
```

the following is obtained

![](/images/side-channels/correlation-input.png)

```c
static void BlockCopy(uint8_t* output, const uint8_t* input)
{
  uint8_t i;
  for (i=0;i<KEYLEN;++i)
  {
    output[i] = input[i];
  }
}
```

what in reality we want is the assembly code

```text
000009ea <BlockCopy>:
 9ea:   9b 01           movw    r18, r22  (1)
 9ec:   20 5f           subi    r18, 0xF0 (1)
 9ee:   3f 4f           sbci    r19, 0xFF (1)
 9f0:   fb 01           movw    r30, r22  (1)
 9f2:   41 91           ld      r20, Z+   (1)
 9f4:   bf 01           movw    r22, r30  (1)
 9f6:   fc 01           movw    r30, r24  (1)
 9f8:   41 93           st      Z+, r20   (1)
 9fa:   cf 01           movw    r24, r30  (1)
 9fc:   62 17           cp      r22, r18  (1)
 9fe:   73 07           cpc     r23, r19  (1)
 a00:   b9 f7           brne    .-18      (1/2)
 a02:   08 95           ret               (4/5)
```


## Glitching

Until now I observed the specimen under the microscope provided by the ADC of
the chipwhisperer, but what if I would poke and perturbe its behaviour?

The model of the processor is fine and good but obviously is a model, its
**correct** behaviour is dependent of the voltage and clock "quality" that I'm
providing to it: a latch needs some margins both for clock and voltage
parameters to work in the way is intended.

It's not used specifically in the attacks that follow but doesn't hurt to know a
little more in detail: a flip-flop-like device has some specific parameters

 - **setup time** \\(t_s\\): input **must** be present and stable for at least
   this time before the clock transition
 - **hold time** \\(t_h\\): input **must** be present and stable for at least this time
   after the clock transition
 - **propagation time** \\(t_p\\): the time after which the output is expected
   to be stable after the clock transition

![](/images/side-channels/data-clock-timing.png)

the maximum usable clock frequency of a processor is determined by the maximum delay among its elements

## Code

[Application note AVR1307](http://ww1.microchip.com/downloads/en/AppNotes/doc8049.pdf)

First of all, create all the one-bit-away instructions from the original one

```
$ public/code/fi/flip.py > public/code/fi/code.bin
$ avr-objdump -b binary -m avr:5 -D public/code/fi/code.bin

public/code/fi/code.bin:     formato del file binary


Disassemblamento della sezione .data:

00000000 <.data>:
   0:   00 2c           mov     r0, r0
   2:   01 2c           mov     r0, r1
   4:   02 2c           mov     r0, r2
   6:   04 2c           mov     r0, r4
   8:   08 2c           mov     r0, r8
   a:   10 2c           mov     r1, r0
   c:   20 2c           mov     r2, r0
   e:   40 2c           mov     r4, r0
  10:   80 2c           mov     r8, r0
  12:   00 2d           mov     r16, r0
  14:   00 2e           mov     r0, r16
  16:   00 28           or      r0, r0
  18:   00 24           eor     r0, r0
  1a:   00 3c           cpi     r16, 0xC0       ; 192
  1c:   00 0c           add     r0, r0
  1e:   00 6c           ori     r16, 0xC0       ; 192
  20:   00 ac           ldd     r0, Z+56        ; 0x38
```

the first line is the original instruction, I choosen this as a alias
for ``nop``, and then follow the 16 one-bit-distant instructions; lucky
us they aren't flow related. The original instruction executes in 1 cycle.

Now I need some instruction to actual printing out of the UART some data from
which I can deduce the effects of glitching: from the actual code of the
firmware

```c
#define USART USARTC0

	while(!USART_IsTXDataRegisterEmpty(&USART));
	USART_PutChar(&USART, 'A');
```

results in this code

```text
.-> 74a:   80 91 a1 08     lds     r24, 0x08A1 (2)
|   74e:   85 ff           sbrs    r24, 5      (1/2/3)
'-- 750:   fc cf           rjmp    .-8         (2)
    752:   81 e4           ldi     r24, 0x41   (1)
    754:   80 93 a0 08     sts     0x08A0, r24 (2)
    758:   80 e0           ldi     r24, 0x00   (1)
    75a:   90 e0           ldi     r25, 0x00   (1)
    75c:   08 95           ret                 (4/5)
```

note that this is the "slower" part of the code since the target uses a baud
rate of 38400 baud, this means the in one second can send 38400 bits or 4800
bytes.

If the target run at speed of 8MHz (as indicated by the value in
``scope.clock.clkgen_freq``) we have each cycle takes 1667 cycle for each bytes
so, since we are printing the string "hello" we have a total of around 8.3k cycles

Thsi is the macro to set a register with a predefined value:

```c
/* nice: ldi can be used only with registers r16-r31 */
#define set_r(r,value) __asm__( \
    "ldi r31, " #value "\n\  (1)
     mov r" #r ", r31 "   \  (1)
    )
```

it executes in two clock cycles, since there are 32 of them, we have 64 clock
cycles

To summarise: we have three part in our firmware:

 1. the setup part where we initialize the hardware and print out "hello"
 2. the setup of the registers with predefined value ~ 64 clock cycles
 3. a nop sled with 1 clock cycle for entry
 4. print out the content of the registers

```
$ ./chipw.py hardware/victims/firmware/simpleserial-experiments/simpleserial-experiments-CW303.hex 
Serial baud rate = 38400
XMEGA Programming flash...
XMEGA Reading flash...
Verified flash OK, 2459 bytes
'\x00hello\x80\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f'
```

## Glitching

[Chipwisperer documentation about glitch module](https://chipwhisperer.readthedocs.io/en/latest/api.html#chipwhisperer.scopes.OpenADC.glitch)


## Links

 - [AVR instruction set manual](http://ww1.microchip.com/downloads/en/devicedoc/atmel-0856-avr-instruction-set-manual.pdf)
 - https://pbpython.com/interactive-dashboards.html
 - https://jakevdp.github.io/PythonDataScienceHandbook/04.08-multiple-subplots.html
 - https://towardsdatascience.com/subplots-in-matplotlib-a-guide-and-tool-for-planning-your-plots-7d63fa632857
 - [Optimal statistical power analysis](https://eprint.iacr.org/2003/152.pdf)
 - [Statistics and Secret Leakage](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.59.3849&rep=rep1&type=pdf)
 - [Power Analysis, What Is Now Possible...](https://link.springer.com/content/pdf/10.1007/3-540-44448-3_38.pdf), paper from ``ASIACRYPT2000``
 - [Investigations of Power Analysis Attacks on Smartcards](https://www.usenix.org/legacy/events/smartcard99/full_papers/messerges/messerges.pdf)
 - [Differential Power Analysis](https://www.paulkocher.com/doc/DifferentialPowerAnalysis.pdf), paper by Paul Kocher
 - [Correlation Power Analysis with a Leakage Model](https://www.researchgate.net/publication/221291676_Correlation_Power_Analysis_with_a_Leakage_Model) paper introducing the CPA in 2004
 - [Tamper Resistance - a Cautionary Note](https://www.cl.cam.ac.uk/~rja14/tamper.html)
 - [Understanding Power Trace](https://forum.newae.com/t/understanding-power-trace/1905), post from NewAE forum explaining the meaning of the power traces
 - [CHIP.FAIL – GLITCHING THE SILICON OF THE CONNECTED WORLD](https://sector.ca/sessions/chip-fail-glitching-the-silicon-of-the-connected-world/)
 - [Fault diagnosis and tolerance in cryptography (FDTC) 2014](https://fdtc.deib.polimi.it/FDTC14/slides.html) with some slides:
   - https://fdtc.deib.polimi.it/FDTC11/shared/FDTC-2011-session-4-3.pdf
   - https://fdtc.deib.polimi.it/FDTC11/shared/FDTC-2011-session-2-1.pdf
   - https://fdtc.deib.polimi.it/FDTC14/shared/FDTC-2014-session_1_1.pdf
 - [POWER ANALYSIS BASED SOFTWARE REVERSE ENGINEERING ASSISTED BY FUZZING II](https://www.schutzwerk.com/en/43/posts/poweranalysis_2/)
 - [Power Analysis For Cheapskates](https://media.blackhat.com/us-13/US-13-OFlynn-Power-Analysis-Attacks-for-Cheapskates-WP.pdf)
 - [Side-channel Attacks Using the Chipwhisperer](https://www.robopenguins.com/chip-whisperer/)
 - [Evaluation of the Masked Logic Style MDPL on a Prototype Chip](https://www.iacr.org/archive/ches2007/47270081/47270081.pdf)
 - [CMOS fabrication processs](https://bjpcjp.github.io/pdfs/cmos_layout_sim/ch07-fabrication.pdf)
 - [Reverse-Engineering Custom Logic (Part 1)](https://web.archive.org/web/20130331010506/http://www.flylogic.net/blog/?p=32)
 - [An Introduction to the MAGIC VLSI Design Layout System](http://terpconnect.umd.edu/~newcomb/vlsi/magic_tut/Magic_x3.pdf)
 - [EE-612: CMOS Circuit Essentials](https://web.archive.org/web/20150509004607/http://nanohub.org/resources/5929/download/2008.11.20-ece612-l22.pdf)
 - [Latches inside: Reverse-engineering the Intel 8086's instruction register](http://www.righto.com/2020/08/latches-inside-reverse-engineering.html)
 - [Reverse-engineering the 8085's ALU and its hidden registers](http://www.righto.com/2013/07/reverse-engineering-8085s-alu-and-its.html)
 - [Silicon reverse engineering: The 8085's undocumented flags](http://www.righto.com/2013/02/looking-at-silicon-to-understanding.html)
 - [8085 die shots](http://visual6502.org/images/pages/8085_die_shots.html)
