<!--
.. title: side channels: power analysis
.. slug: experiments-around-side-channels
.. date: 2022-03-19 00:00:00
.. tags: fault injection,hardware
.. category: 
.. link: 
.. description: 
.. type: text
.. has_math: true
-->

<!-- TEASER_END -->

This is a post in a serie regarding side channels, from the theoretical and
pratical point of view; the posts are

 - introduction on the model of computing devices (to be finished)
 - using the Chipwhisperer ([here](``link://slug/side-channels-using-the-chipwhisperer``))
 - power analysis (this post)
 - glitching (to be finished)

All the graphs in this post are generated using my own libray named [power_analys](https://github.com/gipi/power-analysis/),
this is alpha-quality software without documentation (for now); also a notebook
with all the code that generated the graphs will be available as soon as I take
the time to clean up it.

## Physical interface

As I said in the (to-be-completed) post about the model of a processing unit, the "calculations" inside a
device are done, roughly speaking, switching on and off groups of transistors to
perform the needed operations; since the transistors are physical entities, they
interact with the physical world and need **energy** to move electrons around,
so we can imagine that the power consumption would be in some way connected with
the internal state of the processor[^Nano].

[^Nano]: For an extensive explanation you can use the book "Nanometer CMOS ICs, From Basics to ASICs" pg 161

To measure the power consumption, tipically you have a shunt resistor between the
power line and the ``VCC`` pin of the target with an ``ADC`` measuring the voltage as indicated in the
drawing below

{{% pyplots %}}
import matplotlib
matplotlib.use('Agg')

import schemdraw
import schemdraw.elements as elm
from schemdraw.dsp.dsp import Adc

d = schemdraw.Drawing()

# define as the first thing the IC so we can reference it later
d += (target := elm.Ic(pins=[elm.IcPin('VCC', side='left')]).label('Target', loc='top'))

# move the "drawing point" at the left of it
d.move_from(target.VCC, dx=-5, dy=0)

# add elements
d += (power := elm.Vdd().label('Power', loc='top'))
d += elm.Line().right().at(power.end)
d += (shunt := elm.Resistor().right().label('shunt').to(target.VCC))

# now stuff connected to the ADC
d += elm.Line().at(shunt.end).down()
d += Adc().label('ADC').down()

d.draw()

{{% /pyplots %}}

this works because thanks to Ohm's law, the voltage difference at the sides of
the resistor is proportional to the current drawn from the device.

In general it's possible that multiple pins are responsible for providing power
to the digital device and maybe each pin serves different subsystems
(peripherals, core, etc...), so in real settings the configuration can be more
complex.

In my experiments I'm going to use the ChipWhisperer-lite, it has the
[AD8331](https://www.analog.com/media/en/technical-documentation/data-sheets/AD8331_8332_8334.pdf)
chip (a **variable gain amplifier**, ``VGA``) and the
[AD9215](https://www.analog.com/media/en/technical-documentation/data-sheets/AD9215.pdf)
(an **ADC**). The target's clock and ``ADC`` are synchronized, only the latter
has a sample rate four times of the former (this ratio can be configured).

The configuration of the ``VGA`` is such that the input impedance is 50 ohm
(see table 7 at page 30 of the datasheet) and
``AC``-coupled (so you don't have ``DC`` component, at least theoretically); this explains why, since
the input is connected to the low side of the shunt resistor on the board, you
have negative readings: the high side is **ideally** constant (at the power
supply voltage) so, without ``AC``-coupling you would obtain something like

$$
V_{L} = V_H - I\times R_\hbox{shunt}
$$

but removing the constant voltage, what you see from the traces is

$$
\eqalign{
AC(V_{L}) &= AC(V_H) + AC(-I\times R_\hbox{shunt}) \cr
&= AC(-I\times R_\hbox{shunt})\cr
}
$$

The actual value that you'll find in the traces are also affected by the
**gain** set for the ``VGA``.

**Note:** the power consumption is not technically the values that you are
capturing but has a direct relation with them: the textbook definition is

$$
P = V\cdot I
$$

If the assumption is that the voltage is constant with **a low-amplitube varying
component** (let's call it \\(V_{AC}\\)) we can obtain the following approximation

$$
\eqalign{
P &= V\cdot I \cr
&= (V_{DC} + V_{AC})\cdot I \cr
&= V_{DC}\left(1 + {V_{AC}\over V_{DC}}\right)\cdot I\cr
&\sim V_{DC}\cdot I\cr
}
$$

that works fine as long as \\({V_{AC}\over V_{DC}}\\) is negligible. So at the
end the amplitude measured is really, up to a constant, the power consumption.

Since we are not going to do real physics, for now this is enough to continue.

## Maths&Statistics

To understand a little better what we are going to see in the following
we need to have an overview of what we mean by **correlation**: what follows is an introduction
of the statistical formalism needed to explain **correlation power
analysis**[^Optimal].

[^Optimal]: Optimal statistical power analysis; E. Brier, C. Clavier, F. Olivier ([link to the paper](https://eprint.iacr.org/2003/152.pdf))

First of all, we need a model to describe the relationship between power
consumption and the _digital world_: the simplest one with usefulness is the
model using the **Hamming weight** or **Hamming distance**.

The **Hamming weight** is a quantity defined over a number using its base 2 representation: if \\(d\\) is
a number such that

$$
d = \sum_{i=0}^{N - 1} d_i 2^i\hbox{ with }d_i\in \\{0,1\\}
$$

we define the hamming weight as

$$
HW(d) = \sum_{i=0}^{N - 1} d_i
$$

Although the Hamming weight  is not linear with  respect to its argument, if we
see \\(d\\) as a uniformly independent random variable we can safely assume for
the mean and variance for the Hamming weight

$$
\mu_H = {N\over 2}\qquad\sigma^2_H = {N\over4}
$$

What does it mean? simply that when we are going to capture traces, we are going
to feed as input random bytes (in statistical terms are random variables), since
the HW _inherits_ randomness from them, it's also treated as a random
variable, allowing to use statistical tools to analyze the results.

Another important quantity related to the Hamming weight is the **Hamming
distance** that measure the number of bit flip between two numbers (represented
in base 2); this quantity as a very simple definition [^HD]

$$
HD(S, D) = HW(S\oplus D)
$$

[^HD]: Hacker's delight pg95 and pg343

where \\(\oplus\\) is the ``xor`` (exclusive or) operation defined via this
truth table

| A | B | A \\(\oplus\\) B |
|---|---|-----------------|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

An interesting property is its simmetry

$$
A\oplus B = B \oplus A
$$

and interestingly, if we fix one operand and make the other a uniformly random
independent variable, the Hamming distance has the same mean and variance as the
Hamming weight. We will see later how this can be useful.

What we want to achieve is the "measure" of the correlation between our model's
parameters and the power consumption and to do that we need to use the
**Pearson's correlation factor**: its definition is given by

$$
\rho(A,B) = {Cov(A, B)\over\sigma_A\sigma_B}
$$

where \\(A\\) and \\(B\\) are random variables; the value of \\(\rho(A, B)\\) is
comprised between \\(-1\\) and \\(1\\), when two variables are independent
\\(\rho\\) has a value of zero.

In the following experiments I'm going to use (implicitely) a model where the power consumption
\\(W\\) is related to the Hamming weight of some input \\(D\\) (as a random
variable) by the following relation

$$
W = aH(D) + b
$$

where \\(b\\) is a **noise term**, all the contributions for the power
consumption of the device not involved with the computation directly.

From this model is possible to obtain the following statistical relations:

$$
\eqalign{
    \sigma^2_W &= a^2\sigma^2_H + \sigma^2_b\cr
    \rho(W, H) &= {Cov(W, H)\over\sigma_W\sigma_H}\cr
               &= {Cov(aH+b, H)\over\sqrt{a^2\sigma^2_H + \sigma^2_b}\sigma_H}\cr
               &= {aCov(H, H)\over\sqrt{a^2\sigma^2_H + \sigma^2_b}\sigma_H}\cr
               &= {a\sigma_H^2\over\sqrt{a^2\sigma^2_H + \sigma^2_b}\sigma_H}\cr
               &= {a\sigma_H\over\sqrt{a^2\sigma^2_H + \sigma^2_b}}\cr
               &= {a\sqrt{N/4}\over\sqrt{a^2{N/4} + \sigma^2_b}}\cr
               &= \hbox{sign}(a){\sqrt{N}\over\sqrt{N + 4\sigma^2_b}}\cr
}
$$

so the absolute value of the correlation tends to the limit of 1 when the noise
term is negligible, where the sign is given only by the sign of the coefficient \\(a\\).

Another useful fact for later, related to the Hamming distance, is that if you
want to maximise the correlation of this with respect to a fixed "background",
this maximum is unique[^Optimal].

<!--
### Statistical distribution of inputs

I want to add a little reasoning about the statistical distribution of the
inputs used in my experiments: from the start the point was to study the
relation between Hamming weight and the resulting power traces but you have to
take in mind that not all the weights are "equal" in terms of distribution: this
is a table indicating how many elements with a given weight are possible disposing
of 8bits

| Hamming Weight | # elements |
|----------------|------------|
| 0 | 1 |
| 1 | 8 |
| 2 | 28 |
| 3 | 56 |
| 4 | 70 |
| 5 | 56 |
| 6 | 28 |
| 7 | 8 |
| 8 | 1 |

All this table can be summarized by the formula

$$
\\#\hbox{elements with Hamming weight } w = {8\choose w}
$$

(it's a pretty standard exercise of statistics: you "extract" 8 "balls"
without replacement where \\(w\\) are "white").

The problem is that the elements of weight 8 and 0 are under-represented if we
chose to extract randomly an element from the set of 8bits input, so at first I
was tempted to use as input-generating-algorithm one that selects at random
first the hamming weight and then shuffles the bits position. This generates a
**uniform distribution with respect to the Hamming weights**.

This is ok if you are looking only at the hamming weight but take into account
that a very common operation to perform in order to understand bit transition is
the **xor** operation: this is a table


it's pretty simple to observe that we can use the ``xor`` operation as a
flipping-bits device: if we have an input \\(i\in I\\) and a key \\(k\in K\\)
where \\(h_i\\) is the Hamming weight of the input and \\(h_k\\) the Hamming weight of
the key, we have that the key is flipping \\(h_k\\) bits of the input, possibly
modifying the Hamming weight between a range of 

$$
A\oplus B = B \oplus A
$$

$$
\eqalign{
S \oplus F &= D \cr
S \oplus F \oplus F &= D \oplus F \cr
S &= D \oplus F \cr
}
$$

suppose \\(h_i \leq h_k\\) we can rearrange the order of the bits so that the input
has all the set bits on one "side" so we can flip all the one bits and \\(h_k - h_1\\)
zero bits as a least HW obtainaible and we can 

**no, key is not continuous**

Let be \\(C(h_i, h_k, a, b)\\) the number of combinations that cause the input to
flip \\(a\\) 1bits and \\(b\\) 0bits



However this is also problematic because this operation doesn't
preserve the _uniformity_ of the statistical distribution of the Hamming weight as I build it.
Let me explain.

When you apply the ``xor`` operation to an input you have some bit flips, if
they happen where the input had a bit set the Hamming weight decrements by one,
otherwise the opposite happens.

Let \\(i\in I\\) be the input byte, \\(h_{I}\\) the Hamming weight associated to it,
i.e., \\(h_I\\) bits are set. Let be \\(k\in K\\) the element we are xoring the input with,
having \\(h_k\\) as Hamming weight. The average of the Hamming weight is given
by (we are averaging over the input space)

$$
\begin{align}
\langle\hbox{HW}(I\oplus k)\rangle &= \sum_{i\in I} p(i) \hbox{HW}(i\oplus k)\cr
&= \sum_{h_I = 0}^8 \sum_{i \in I_{h_I}} p(i) \hbox{HW}(i\oplus k) \cr
&= \sum_{h_I = 0}^8 \sum_{i \in I_{h_I}} p(i) \left(\hbox{HW}(k) + \Delta\hbox{HW}\_{k}(i)\right) \cr
&= \sum\_{h_I = 0}^8 \sum_{i \in I_{h_I} } p(i) \hbox{HW}(k) + \sum_{h_I = 0}^8 \sum_{i \in I_{h_I} } p(i) \Delta\hbox{HW}\_{k}(i) \cr
&= \sum\_{h_I = 0}^8 \sum_{i \in I_{h_I} } p(i) \hbox{HW}(k) + \sum_{h_I = 0}^8 \sum_{i \in I_{h_I} } p(i) \Delta\hbox{HW}\_{k}(i) \cr
&= \hbox{HW}(k)\sum\_{h_I = 0}^8 \sum\_{i \in I_{h_I} } p(i)  + \sum\_{h_I = 0}^8 \sum\_{i \in I_{h_I} } p(i) \Delta\hbox{HW}\_k(i) \cr
&= \hbox{HW}(k) + \sum_{h_I = 0}^8 \sum_{i \in I_{h_I} } p(i) \Delta\hbox{HW}\_k(i) \cr
\end{align}
$$

Note how is important in the equation the probability distribution \\(p(i)\\) of
the input bytes; in the case of the uniform distribution with respect to the
bytes we have \\(p(i) = 1/256\\), meanwhile in the case of uniform Hamming
weight distribution we have \\({1\over p(i)} = 9{8\choose h_i}\\).

Note how a permutation of the bits order doesn't change the Hamming weight, so the
iteration over the space of the inputs with given Hamming weight is the same as
the iteration over the space of the key with the same Hamming weight of the
starting key maintaining fixed the input.

This means that for a constant \\(p(i)\\) we have

$$
\langle\hbox{HW}\[I\oplus k]\rangle =\langle\hbox{HW}\[i\oplus K]\rangle
$$

If we have an key with HW equal to \\(h_k\\) and we want to calculate the sum
over all the inputs with a given HW \\(h_i\\) fixed we have

\\(\overline{h}_i = 8-h_i\\)

This is the number of xoring with \\(u\\) transitions \\(0\rightarrow 1\\)
and \\(d\\) transitions \\(1\rightarrow0\\) of \\(i\\)

$$
C(h_i, h_k, u, d) = {h_i\choose u}{8 - h_i\choose d}\;\hbox{where}\;
\cases{
    u + d = h_k &\cr
    u\in\\{h_i - \overline h_k, \dots,h_i\\}&if $h_i\geq\overline h_k$ \cr
    u\in\\{0, \dots,h_i\\} & if $h_i\leq\overline h_k$ and $h_i\leq h_k$ \cr
    u\in\\{0, \dots,h_k\\} & if $h_i\leq\overline h_k$ and $h_i\geq h_k$ \cr
}
$$

-->

## Measuring different instructions

Before starting crunching numbers, a very simple overview of how different
instructions have different
"energy-footprint": let's try to show the power consumption of the target executing

 - 10 ``nop``s
 - 10 ``mul``s
 - 20 ``mul``s
 - 10 ``mul``s, 10 ``nop``s and 10 ``muls``

![](/images/side-channels/comparison-instructions.png)

the assembly code is the following (each column is a different capture)

```text
nop             mul	r0, r1     mul	r0, r1     mul	r0, r1
nop             mul	r0, r1     mul	r0, r1     mul	r0, r1
nop             mul	r0, r1     mul	r0, r1     mul	r0, r1
nop             mul	r0, r1     mul	r0, r1     mul	r0, r1
nop             mul	r0, r1     mul	r0, r1     mul	r0, r1
nop             mul	r0, r1     mul	r0, r1     mul	r0, r1
nop             mul	r0, r1     mul	r0, r1     mul	r0, r1
nop             mul	r0, r1     mul	r0, r1     mul	r0, r1
nop             mul	r0, r1     mul	r0, r1     mul	r0, r1
nop             mul	r0, r1     mul	r0, r1     mul	r0, r1
rjmp	.-2     rjmp	.-2    mul	r0, r1     nop
                               mul	r0, r1     nop
                               mul	r0, r1     nop
                               mul	r0, r1     nop
                               mul	r0, r1     nop
                               mul	r0, r1     nop
                               mul	r0, r1     nop
                               mul	r0, r1     nop
                               mul	r0, r1     nop
                               mul	r0, r1     nop
                               rjmp	.-2        mul	r0, r1
                                               mul	r0, r1
                                               mul	r0, r1
                                               mul	r0, r1
                                               mul	r0, r1
                                               mul	r0, r1
                                               mul	r0, r1
                                               mul	r0, r1
                                               mul	r0, r1
                                               mul	r0, r1
                                               rjmp	.-2
```

the tail of the capture is the ``rjmp`` instruction that loops indefinitely.
The big spike at the start of the capture is probably the current generated by
the ``GPIO`` used to trigger the capture.

The first thing that you can notice is that ten ``nop``s are taking 40 cycles to
complete (i.e. 10 target's clock cycles) meanwhile ten ``mul``s needs double
that number. This matches with the actual number of cycles needed by these
instructions: ``nop`` executes in one cycle, meanwhile ``mul`` takes two cycles
and each cycle the ``ADC`` samples four times.

## Correlation

In the last section I showed that different instructions have different
"footprints", probably the easiest possible way to use that is by timing
analysis: for example if we had a piece of code that checks
for a password and exits at the first wrong character, we could capture the power traces for
every possible (first char) input and
we should see only one having a different pattern.

What follows is an example with the firmware provided by the Chipwhisperer
(``basic-passwdcheck``) where the ``h`` character is the first of the secret
password (I grouped the traces in sets of 16 to make clearer the "outcast")

![](/images/side-channels/basic-passwdcheck-timing.png)
![](/images/side-channels/basic-passwdcheck-timing1.png)
![](/images/side-channels/basic-passwdcheck-timing2.png)
![](/images/side-channels/basic-passwdcheck-timing3.png)

For now I'm not interested in performing specific attacks but to study the
relationship between instructions and power consumption and to do this I will
perform an "experiment" where I use as input the firmware code with the simplest
possible assembly instructions.

The first experiment is to check what we can infer from the relation between the
argument of the instruction ``ldi r16, <value>`` and the power consumption: these
are the (interesting portion of) instructions (``sts`` is the instruction
triggering the capture of the trace)

```
 6de:	c0 93 05 06 	sts	0x0605, r28
 6e2:	00 00       	nop
 6e4:	00 00       	nop
 6e6:	00 00       	nop
 6e8:	00 00       	nop
 6ea:	00 00       	nop
 6ec:	00 00       	nop
 6ee:	00 00       	nop
 6f0:	00 00       	nop
 6f2:	00 00       	nop
 6f4:	00 00       	nop
 6f6:	00 e0       	ldi	r16, <value>
 6f8:	00 00       	nop
 6fa:	00 00       	nop
 6fc:	00 00       	nop
 6fe:	00 00       	nop
 700:	00 00       	nop
 702:	00 00       	nop
 704:	00 00       	nop
 706:	00 00       	nop
 708:	00 00       	nop
 70a:	00 00       	nop
 70c:	ff cf       	rjmp	.-2
```

As you can see there is the instruction of interested sourrounded by
input-independent code, this should make the relation standing out.

After capturing 100 traces for each hamming weight it's possible to plot the
average for each one together as in the following plot where I tried to align
the instructions with the actual clock cycle where they **should** happen
(I'm not sure of the alignment of the trace with the actual instructions, so the
instruction in picture are the first guess)

![](/images/side-channels/pa-hamming.png)

It's possible to note "something going on" around the ``ldi`` instruction; if
we zoom in we can see a little better

![](/images/side-channels/pa-hamming-zoom.png)

At first seems disaligned by half-instruction, take note of this for the
following.

Meanwhile it's possible to have a better view plotting a scatterplot of
mean value of a given sample for a specific Hamming weight versus the
corresponding hamming weight (the
vertical bars are the standard deviations of each respective set of traces):

![](/images/side-channels/pa-hamming-scatterplot.png)

The first interesting samples have a **negative** correlation but after a couple
of cycles this change to positive improving considerebly (note for example at
sample 50 the standard deviations are way far from each other, this means that
also taking noise into consideration the respective sets of traces are
"separated").

The final graph is the correlation I talked so much about

![](/images/side-channels/ldi-corr.png)

Just with one kind of instruction is not possible to deduce anything valuable
(althought it's interesting seeing that _something is there_), now I want to try
a different instruction: ``adc rx, <value>``.

This is the code under scrutiny

```
 6de:	c0 93 05 06 	sts	0x0605, r28
 6e2:	10 e0       	ldi	r17, <value>
 6e4:	00 e0       	ldi	r16, 0x00
 6e6:	00 00       	nop
 6e8:	00 00       	nop
 6ea:	00 00       	nop
 6ec:	00 00       	nop
 6ee:	00 00       	nop
 6f0:	00 00       	nop
 6f2:	00 00       	nop
 6f4:	00 00       	nop
 6f6:	00 00       	nop
 6f8:	00 00       	nop
 6fa:	01 1f       	adc	r16, r17
 6fc:	00 00       	nop
 6fe:	00 00       	nop
 700:	00 00       	nop
 702:	00 00       	nop
 704:	00 00       	nop
 706:	00 00       	nop
 708:	00 00       	nop
 70a:	00 00       	nop
 70c:	00 00       	nop
 70e:	00 00       	nop
 710:	ff cf       	rjmp	.-2
```

Plotting each averaged class we obtain something similar to before

![](/images/side-channels/adc-hamming.png)

but notice how the instructions seem aligned perfectly!

![](/images/side-channels/adc-hamming-zoom.png)

in particular is interesting to note that there is not in this case a negative
correlation around the _start_ of the instruction

![](/images/side-channels/adc-hamming-scatterplot.png)
![](/images/side-channels/adc-corr.png)

What explanation is available for this behaviour? Well, a modern processing unit
employs some tricks to speed-up computation and a prevalent one is the
**pipeling**, i.e., splitting the instruction life cycle in different stages and
when the unit is executing a given instruction is also doing other stuff with the
instruction that should be executed next; in particular for the XMega we have this quote from the
manual:

    The AVR uses a Harvard architecture - with separate memories and buses for program and
    data. Instructions in the program memory are executed with a single level pipeline. While one
    instruction is being executed, the next instruction is pre-fetched from the
    program memory. This concept enables instructions to be executed in every clock cycle

To clarify a little better here a diagram

![](/images/side-channels/avr-pipeline-timing.png)

Now if you take a look at the [AVR instruction set manual](http://ww1.microchip.com/downloads/en/devicedoc/atmel-0856-avr-instruction-set-manual.pdf)
you can see how the opcode for the ``ldi`` instruction is encoded:

![](/images/side-channels/avr-ldi.png)

i.e. the value to put in the register is encoded directly in the instruction
that is read in the fetching stage during the previous instruction!

With this in mind for now on I assume that the alignment is correct (another
implicit assumption is that the ``sts`` instruction, that is two-cycles long,
executes at the last cycle); while
I'm at it I want to double-proof the _fetching stage_ assumption for ``ldi``
putting an infinite loop just before it :)

Observe what happens if we flash this code

```
 6de:	c0 93 05 06 	sts	0x0605, r28	; 0x800605 <__TEXT_REGION_LENGTH__+0x7de605>
 6e2:	00 00       	nop
 6e4:	00 00       	nop
 6e6:	00 00       	nop
 6e8:	00 00       	nop
 6ea:	00 00       	nop
 6ec:	00 00       	nop
 6ee:	00 00       	nop
 6f0:	00 00       	nop
 6f2:	00 00       	nop
 6f4:	00 00       	nop
 6f6:	ff cf       	rjmp	.-2      	; 0x6f6 <main+0x56>
 6f8:	00 e0       	ldi	r16, <value>
```

![](/images/side-channels/ldi-hamming.png)

it's clearly visible a repeated pattern, look at this zoom

![](/images/side-channels/ldi-hamming-zoom.png)

and the repeation in the correlation

![](/images/side-channels/ldi-hamming-scatterplot.png)
![](/images/side-channels/ldi-loop-over-corr.png)

Compare what you have seen with the same concept applied to the ``adc``

![](/images/side-channels/adc-loop-over-hamming.png)

No correlation at all! I mean, this would have been obvious from the start but
it's always better to double check unexpected results :)

Now to improve on my experiment I decided to change strategy: until now I
flashed a different code every time I wanted to read a particular value for
``ldi`` but this involves overwriting the flash so I decided to write some code
to build a **jump table**; with this code a character is read from the serial,
converted to an integer and used as an index to jump to a specific block where
the ``ldi r16, <value>`` is waiting to execute (I have a specific [post](link://slug/reversing-avr-code) about
reversing ``AVR`` assembly if you want to understand what is happening).

![](/images/side-channels/ldi-jump-table-hamming.png)

and also in this case it's pretty amazing how the instructions align perfectly
(by the way, an [old AVR instruction set manual indicated contradicting values for
the number of cycles for the ``ldd`` instruction](https://www.reddit.com/r/avr/comments/s3p2yl/contradictory_information_about_cycles_for_the/) so I used this captures as a
evidence for the correct number).

There is only one thing that bothers me, there is apparently a "tail" after the
instruction that shouldn't be there, my educated guess is that the ``ADC``
frontend, being ``AC`` coupled causes this anomaly since the capacitor in front
of the measuring device has a change oscillating with the flow of current.

On order to test this I tried to capture the power consumption using my trusty
Siglent using some python code that I wrote, but this is argument of a future
post.

## A more realistic case

Now I want to try to apply to the simplest difficult problem, i.e., trying
to break a constant time password comparison; the code is the following

```c
#define PASSWORD "kebab"
#define SIZE_INPUT 32

int main(void)
{

    char password[] = PASSWORD;

    platform_init();
    init_uart();
    trigger_setup();

    /* banner requesting the password */
    putch('p');
    putch('a');
    putch('s');
    putch('s');
    putch('w');
    putch('o');
    putch('r');
    putch('d');
    putch(':');
    putch(' ');

    /* taking the password, waiting for a newline or for SIZE_INPUT characters */
    char c;
    char input[SIZE_INPUT];
    unsigned int input_index = 0;

    do {
        c = getch();
        input[input_index++] = c;
    } while(c != '\n' && input_index < SIZE_INPUT);

    trigger_high();

    unsigned char result = 0;

    for (uint8_t index = 0 ; index < strlen(PASSWORD) ; index++) {
        result |= input[index] ^ password[index];
    }

    if (result)
        while(1);

    putch('W');
    putch('I');
    putch('N');

    while(1);
}
```

and this is the generated assembly (I advice always to check generated code
because the compiler sometimes does magic)

```
000006c6 <main>:
 6c6:   cf 93           push    r28
 6c8:   df 93           push    r29
 6ca:   cd b7           in      r28, 0x3d       ; 61
 6cc:   de b7           in      r29, 0x3e       ; 62
 6ce:   a6 97           sbiw    r28, 0x26       ; 38 <--- allocate 38 byte on the stack (32 for the input, 6 for the hardcoded password (that includes the null byte))
 6d0:   cd bf           out     0x3d, r28       ; 61
 6d2:   de bf           out     0x3e, r29       ; 62
 6d4:   86 e0           ldi     r24, 0x06       ; 6  <--- set the counter to six
 6d6:   e0 e1           ldi     r30, 0x10       ; 16
 6d8:   f0 e2           ldi     r31, 0x20       ; 32 <--- set the source Z to the password
 6da:   de 01           movw    r26, r28             <--- set dest to X (on the stack)
 6dc:   91 96           adiw    r26, 0x21       ; 33 <--- with a starting offset of 33
 6de:   01 90           ld      r0, Z+               <---- loop starts here with r0 = *Z++
 6e0:   0d 92           st      X+, r0               <---- *(X++) = r0
 6e2:   8a 95           dec     r24                  <---- decrement counter
 6e4:   e1 f7           brne    .-8                  <---- jump if not zero -------
 6e6:   0e 94 4d 03     call    0x69a   ; 0x69a <platform_init>
 6ea:   0e 94 7c 02     call    0x4f8   ; 0x4f8 <init_uart0>
 6ee:   81 e0           ldi     r24, 0x01       ; 1
 6f0:   80 93 01 06     sts     0x0601, r24     ; 0x800601 <__TEXT_REGION_LENGTH__+0x7de601>
 6f4:   80 e7           ldi     r24, 0x70       ; 112
 6f6:   0e 94 b9 02     call    0x572   ; 0x572 <output_ch_0>
 6fa:   81 e6           ldi     r24, 0x61       ; 97
 6fc:   0e 94 b9 02     call    0x572   ; 0x572 <output_ch_0>
 700:   83 e7           ldi     r24, 0x73       ; 115
 702:   0e 94 b9 02     call    0x572   ; 0x572 <output_ch_0>
 706:   83 e7           ldi     r24, 0x73       ; 115
 708:   0e 94 b9 02     call    0x572   ; 0x572 <output_ch_0>
 70c:   87 e7           ldi     r24, 0x77       ; 119
 70e:   0e 94 b9 02     call    0x572   ; 0x572 <output_ch_0>
 712:   8f e6           ldi     r24, 0x6F       ; 111
 714:   0e 94 b9 02     call    0x572   ; 0x572 <output_ch_0>
 718:   82 e7           ldi     r24, 0x72       ; 114
 71a:   0e 94 b9 02     call    0x572   ; 0x572 <output_ch_0>
 71e:   84 e6           ldi     r24, 0x64       ; 100
 720:   0e 94 b9 02     call    0x572   ; 0x572 <output_ch_0>
 724:   8a e3           ldi     r24, 0x3A       ; 58
 726:   0e 94 b9 02     call    0x572   ; 0x572 <output_ch_0>
 72a:   80 e2           ldi     r24, 0x20       ; 32
 72c:   0e 94 b9 02     call    0x572   ; 0x572 <output_ch_0>
 730:   ce 01           movw    r24, r28
 732:   01 96           adiw    r24, 0x01       ; 1
 734:   7c 01           movw    r14, r24
 736:   8e 01           movw    r16, r28
 738:   0f 5d           subi    r16, 0xDF       ; 223 <--- r16 = fp - 32
 73a:   1f 4f           sbci    r17, 0xFF       ; 255
 73c:   6c 01           movw    r12, r24
 73e:   0e 94 b2 02     call    0x564   ; 0x564 <input_ch_0>
 742:   d6 01           movw    r26, r12
 744:   8d 93           st      X+, r24
 746:   6d 01           movw    r12, r26
 748:   8a 30           cpi     r24, 0x0A       ; 10
 74a:   19 f0           breq    .+6             ; 0x752 <main+0x8c>
 74c:   a0 17           cp      r26, r16
 74e:   b1 07           cpc     r27, r17
 750:   b1 f7           brne    .-20
 752:   81 e0           ldi     r24, 0x01       ; 1
 754:   80 93 05 06     sts     0x0605, r24
 758:   f8 01           movw    r30, r16        <--- Z points to password
 75a:   9e 01           movw    r18, r28
 75c:   2a 5f           subi    r18, 0xFA       ; 250
 75e:   3f 4f           sbci    r19, 0xFF       ; 255
 760:   80 e0           ldi     r24, 0x00       ; 0
 762:   d7 01           movw    r26, r14        <--- loop starts here
 764:   4d 91           ld      r20, X+
 766:   7d 01           movw    r14, r26
 768:   91 91           ld      r25, Z+
 76a:   94 27           eor     r25, r20
 76c:   89 2b           or      r24, r25
 76e:   a2 17           cp      r26, r18
 770:   b3 07           cpc     r27, r19
 772:   b9 f7           brne    .-18            ; 0x762 <main+0x9c>
 774:   81 11           cpse    r24, r1
 776:   ff cf           rjmp    .-2             ; 0x776 <main+0xb0>
 778:   87 e5           ldi     r24, 0x57       ; 87
 77a:   0e 94 b9 02     call    0x572   ; 0x572 <output_ch_0>
 77e:   89 e4           ldi     r24, 0x49       ; 73
 780:   0e 94 b9 02     call    0x572   ; 0x572 <output_ch_0>
 784:   8e e4           ldi     r24, 0x4E       ; 78
 786:   0e 94 b9 02     call    0x572   ; 0x572 <output_ch_0>
 78a:   ff cf           rjmp    .-2             ; 0x78a <main+0xc4>
```

Let see a single capture

![](/images/side-channels/constant-time-trace.png)

it's possible to deduce that there are five iterations happening before the
infinite loop (five is the number of characters in the password).

**Note:** this could seem boring but for me it's very important: thanks to power
analysis you have some sort of **oracle** that gives you information otherwise
unavailable! Imagine you have a device that presents some sort of password
prompt and you, via tinkering from the terminal can asses that accepts up to 32
characters; this means you have \\(\left(2^8\right)^{32} = 2^{256}\\) possible passwords,
a key space huge, without hope to be bruteforced.

**But** from power analysis you have now reduced the key space to \\(\left(2^8\right)^{5} = 2^{40}\\)
more feasible (an encryption algorithm with such "strength" would be considered broken).
Obviously a 32 characters password doesn't have this problem :)

Now if we study only the power consumption
in relation to the 0th byte of input it's possible to see "something
happening" only in the first iteration of the loop (actually there is something
going on also at the start of the second iteration, but "less").

![](/images/side-channels/constant-time-0th-hamming.png)

here the zoom

![](/images/side-channels/constant-time-0th-hamming-zoom.png)

This is interesting: we have a way to see **when** our input is used in the
computation; in the graph above I overlayed the instructions but obviously in
general this is not possible, however this temporal information instead is available
via power analysis. This is akin to **taint analysis** done in security research
were the software is analyzed to find how the user input can "propagate" and
impact execution, take a look at [libdft](https://www.cs.columbia.edu/~vpk/research/libdft/)
for example. But this out of scope (for now :P).

Now I want to try something new: remember the stuff above about the Hamming distance
and the ``xor`` operation? in
this case I want to try to find for each sample the element which xor creates
the most correlated relation with respect to the input. And something interesting come out: obviously the
majority of samples have no correlation with nothing, in a couple of points
there is correlation with the input bytes but specific samples (corresponding
to the instruction ``ld r25, Z+``, i.e. the instruction loading the hardcoded
password into a register) correlate to the password!

Here the results where each entry is the best correlation between the i-th input
byte (row) and the j-th iteration of the instruction (column):

<style type="text/css">
#T_7eb3e_row0_col0 {
  background-color: #289049;
  color: #f1f1f1;
}
#T_7eb3e_row0_col1, #T_7eb3e_row0_col2, #T_7eb3e_row0_col3, #T_7eb3e_row0_col4, #T_7eb3e_row0_col5, #T_7eb3e_row1_col0, #T_7eb3e_row1_col2, #T_7eb3e_row1_col3, #T_7eb3e_row1_col4, #T_7eb3e_row1_col5, #T_7eb3e_row2_col0, #T_7eb3e_row2_col1, #T_7eb3e_row2_col3, #T_7eb3e_row2_col4, #T_7eb3e_row2_col5, #T_7eb3e_row3_col0, #T_7eb3e_row3_col1, #T_7eb3e_row3_col2, #T_7eb3e_row3_col4, #T_7eb3e_row3_col5, #T_7eb3e_row4_col0, #T_7eb3e_row4_col1, #T_7eb3e_row4_col2, #T_7eb3e_row4_col3, #T_7eb3e_row4_col5 {
  background-color: #f7fcf5;
  color: #000000;
}
#T_7eb3e_row1_col1 {
  background-color: #0a7633;
  color: #f1f1f1;
}
#T_7eb3e_row2_col2 {
  background-color: #006529;
  color: #f1f1f1;
}
#T_7eb3e_row3_col3 {
  background-color: #004e1f;
  color: #f1f1f1;
}
#T_7eb3e_row4_col4 {
  background-color: #00441b;
  color: #f1f1f1;
}
</style>
<table id="T_7eb3e_">
  <thead>
    <tr>
      <th class="blank level0" >&nbsp;</th>
      <th class="col_heading level0 col0" >0</th>
      <th class="col_heading level0 col1" >1</th>
      <th class="col_heading level0 col2" >2</th>
      <th class="col_heading level0 col3" >3</th>
      <th class="col_heading level0 col4" >4</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th id="T_7eb3e_level0_row0" class="row_heading level0 row0" >0</th>
      <td id="T_7eb3e_row0_col0" class="data row0 col0" >b'k':0.73</td>
      <td id="T_7eb3e_row0_col1" class="data row0 col1" >b'\xeb':0.26</td>
      <td id="T_7eb3e_row0_col2" class="data row0 col2" >b'\xd4':0.06</td>
      <td id="T_7eb3e_row0_col3" class="data row0 col3" >b'\xfe':0.05</td>
      <td id="T_7eb3e_row0_col4" class="data row0 col4" >b'\xd6':0.04</td>
    </tr>
    <tr>
      <th id="T_7eb3e_level0_row1" class="row_heading level0 row1" >1</th>
      <td id="T_7eb3e_row1_col0" class="data row1 col0" >b'F':0.02</td>
      <td id="T_7eb3e_row1_col1" class="data row1 col1" >b'e':0.76</td>
      <td id="T_7eb3e_row1_col2" class="data row1 col2" >b'\xe5':0.25</td>
      <td id="T_7eb3e_row1_col3" class="data row1 col3" >b'\xde':0.07</td>
      <td id="T_7eb3e_row1_col4" class="data row1 col4" >b'\xda':0.06</td>
    </tr>
    <tr>
      <th id="T_7eb3e_level0_row2" class="row_heading level0 row2" >2</th>
      <td id="T_7eb3e_row2_col0" class="data row2 col0" >b'\xbb':0.02</td>
      <td id="T_7eb3e_row2_col1" class="data row2 col1" >b'z':0.01</td>
      <td id="T_7eb3e_row2_col2" class="data row2 col2" >b'b':0.78</td>
      <td id="T_7eb3e_row2_col3" class="data row2 col3" >b'\xe2':0.25</td>
      <td id="T_7eb3e_row2_col4" class="data row2 col4" >b'\xbd':0.06</td>
    </tr>
    <tr>
      <th id="T_7eb3e_level0_row3" class="row_heading level0 row3" >3</th>
      <td id="T_7eb3e_row3_col0" class="data row3 col0" >b'\xbf':0.11</td>
      <td id="T_7eb3e_row3_col1" class="data row3 col1" >b'\x9f':0.10</td>
      <td id="T_7eb3e_row3_col2" class="data row3 col2" >b'\xbf':0.06</td>
      <td id="T_7eb3e_row3_col3" class="data row3 col3" >b'a':0.80</td>
      <td id="T_7eb3e_row3_col4" class="data row3 col4" >b'\xe1':0.20</td>
    </tr>
    <tr>
      <th id="T_7eb3e_level0_row4" class="row_heading level0 row4" >4</th>
      <td id="T_7eb3e_row4_col0" class="data row4 col0" >b']':0.02</td>
      <td id="T_7eb3e_row4_col1" class="data row4 col1" >b'\xf7':0.01</td>
      <td id="T_7eb3e_row4_col2" class="data row4 col2" >b'v':0.01</td>
      <td id="T_7eb3e_row4_col3" class="data row4 col3" >b'\xdf':0.02</td>
      <td id="T_7eb3e_row4_col4" class="data row4 col4" >b'b':0.81</td>
    </tr>
  </tbody>
</table>


and the diagonal contains the password (the floating point number is the value
of the correlation). For completness here the table with the iterations along the
rows and the (eight) samples related to the instruction along the columns


| sample index | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|--------------|---|---|---|---|---|---|---|---|
| 44           |b'\x00'	0.56 |b'+'	0.68 |b'+'	0.73 |b'k'	0.72 |b'k'	0.71 |b'+'	0.60 | b'+'	0.61 |b'+'	0.58 |
| 92           |b'\x80'	0.20 |b'e'	0.67 |b'e'	0.76 |b'e'	0.76 |b'e'	0.74 |b'e'	0.42 |b'e'	0.40 |b'e'	0.39 | 
| 140          |b'A'	0.18 |b'b'	0.72 |b'b'	0.78 |b'b'	0.78 |b'b'	0.76 |b'b'	0.43 |b'b'	0.41 |b'b'	0.39 |
| 188          |b'\x88'	0.13 |b'a'	0.73 |b'a'	0.80 |b'a'	0.80 |b'a'	0.78 |b'a'	0.45 |b'a'	0.44 |b'a'	0.42 |
| 236          |b'@'	0.21 |b'b'	0.76 |b'b'	0.82 |b'b'	0.81 |b'b'	0.80 |b'b'	0.45 |b'b'	0.43 |b'b'	0.41 |

Now with this discovery I would expect to see a symmetric relation with the
``ldd r20, X+`` instruction: if we have correlation between the input byte
(``ldd r20, X+``) and the password byte (``ldd r25, Z+``) in a given iteration I would expect to see a
similar correlation between the password byte and the following iteration input byte but this doesn't happen;
if you look at the table with the most correlated bytes you see that there are
interesting correlation with **two** previous iteration (sample 129, 177, 225)

| sample index | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|--------------|---|---|---|---|---|---|---|---|
| 32           |b'\xb1' 0.01 |b'\x03'	0.82 |b'\x03'	0.87 |b'\x03'	0.86 |b'\x03'	0.83 |b'\x00'	0.90 |b'\x00'	0.91 |b'\x00'	0.90 |
| 80           |b'm'	0.01 |b'\xa1'	0.82 |b'\xa1'	0.88 |b'\xa1'	0.87 |b'\xa1'	0.85 |b'\x80'	0.64 |b'\x80'	0.67 |b'\x80'	0.66 |
| 128          |b'\x15'	0.01 |b'k'	0.78 |b'k'	0.85 |b'k'	0.83 |b'k'	0.81 |b'\x00'	0.44 |b'\x80'	0.49 |b'\x80'	0.49 |
| 176          |b'\x9f'	0.09 |b'e'	0.82 |b'e'	0.88 |b'e'	0.87 |b'e'	0.85 |b'\x00'	0.50 |b'\x00'	0.55 |b'\x80'	0.54 |
| 224          |b'\xf7'	0.01 |b'b'	0.79 |b'b'	0.86 |b'b'	0.84 |b'b'	0.82 |b'\x00'	0.52 |b'\x80'	0.55 |b'\x80'	0.55 |

To summarize the relationship between power consumption and input bytes I'm
using the following diagram where in the entry \\(\left(i, j\right)\\) of the
"matrix" you have the correlation with \\(I[i]\otimes I[j]\\), with \\(I[\alpha]\\)
indicating the \\(\alpha\\)-th input byte. In the diagonal \\(\left(a, a\right)\\)
instead I placed the direct correlation with the input byte \\(I[a]\\)

![](/images/side-channels/constant-time-cross-corr.png)

It's possible to see a correlation between two adjacent ``ld``s from memory.

Improving the experiment a  little, it's possible to manually craft some assembly
to unroll the loop in a way that the loadings of the password and the input bytes
are not more one after the other, but instead the password is loaded into some
registers at the start of the routine
(this time I used a different password: "armedilzo", so I don't have repeated
characters and is longer)

```
 75a:	80 93 05 06 	sts	0x0605, r24	; 0x800605 <__TEXT_REGION_LENGTH__+0x7de605>
 75e:	00 e0       	ldi	r16, 0x00	; 0
 760:	d9 a0       	ldd	r13, Y+33	; 0x21
 762:	fa a0       	ldd	r15, Y+34	; 0x22
 764:	1b a1       	ldd	r17, Y+35	; 0x23
 766:	ac a1       	ldd	r26, Y+36	; 0x24
 768:	ed a1       	ldd	r30, Y+37	; 0x25
 76a:	6e a1       	ldd	r22, Y+38	; 0x26
 76c:	4f a1       	ldd	r20, Y+39	; 0x27
 76e:	28 a5       	ldd	r18, Y+40	; 0x28
 770:	89 a5       	ldd	r24, Y+41	; 0x29
 772:	e9 80       	ldd	r14, Y+1	; 0x01
 774:	de 24       	eor	r13, r14
 776:	0d 29       	or	r16, r13
 778:	ea 80       	ldd	r14, Y+2	; 0x02
 77a:	fe 24       	eor	r15, r14
 77c:	0f 29       	or	r16, r15
 77e:	eb 80       	ldd	r14, Y+3	; 0x03
 780:	1e 25       	eor	r17, r14
 782:	01 2b       	or	r16, r17
 784:	ec 80       	ldd	r14, Y+4	; 0x04
 786:	ae 25       	eor	r26, r14
 788:	0a 2b       	or	r16, r26
 78a:	ed 80       	ldd	r14, Y+5	; 0x05
 78c:	ee 25       	eor	r30, r14
 78e:	0e 2b       	or	r16, r30
 790:	ee 80       	ldd	r14, Y+6	; 0x06
 792:	6e 25       	eor	r22, r14
 794:	06 2b       	or	r16, r22
 796:	ef 80       	ldd	r14, Y+7	; 0x07
 798:	4e 25       	eor	r20, r14
 79a:	04 2b       	or	r16, r20
 79c:	e8 84       	ldd	r14, Y+8	; 0x08
 79e:	2e 25       	eor	r18, r14
 7a0:	02 2b       	or	r16, r18
 7a2:	e9 84       	ldd	r14, Y+9	; 0x09
 7a4:	8e 25       	eor	r24, r14
 7a6:	08 2b       	or	r16, r24
 7a8:	01 11       	cpse	r16, r1
 7aa:	ff cf       	rjmp	.-2      	; 0x7aa <main+0xe4>
```

this time the correlation between two-``ld``s-apart is more apparent.

![](/images/side-channels/constant-time-unroll-manual-cross-corr.png)

probably the branch instruction interferes with the ``ld``s in some obscure way.

This breaks my method of recovering the password but maybe something can be done
for this and if something interesting come up I will tell you in future.

## Conclusion

In this post I gave you an overview of what is possible to "see" via power analysis and
some of the tools available for it. Maybe I uncovered a new "primitive" to steal
secret in chips of the AVR family. Probably there will be a future post about
some "advanced" experiments, like capturing traces via an oscilloscope, align
them via fourier transform and more.

## Linkography

 - [AVR instruction set manual](http://ww1.microchip.com/downloads/en/devicedoc/atmel-0856-avr-instruction-set-manual.pdf)
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
 - [Pearson's correlation](https://www.statlect.com/fundamentals-of-probability/linear-correlation)
