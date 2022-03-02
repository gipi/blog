<!--
.. title: side channels: power analysis
.. slug: experiments-around-side-channels
.. date: 2021-10-01 00:00:00
.. tags: fault injection,hardware, WIP
.. status: draft
.. category: 
.. link: 
.. description: 
.. type: text
.. has_math: true
-->

<!-- TEASER_END -->

This is a post in a series regarding side channels, from the theoretical and
pratical point of view; the posts are

 - introduction on the model of computing devices (to be finished)
 - using the Chipwhisperer ([here](``link://slug/side-channels-using-the-chipwhisperer``))
 - power analysis (this post)
 - glitching (to be finished)

## Side channels experimentations

### Power analysis

Let's start with something interesting: leak information about the computation
observing the power consumption of a device.

As I said in the introduction about the model, the "calculations" inside a
device are done, roughly speaking, switching on and off groups of transistors to
perform the needed operations; since the transistors are physical entities, they
interact with the physical world and need **energy** to move electrons around,
so we can imagine that the power consumption would be in some way connected with
the internal state of the processor[^Nano].

[^Nano]: For an extensive explanation you can use the book "Nanometer CMOS ICs, From Basics to ASICs" pg 161

The standard configuration for measurements like these is the following: a shunt resistor between the
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

In my experiments I'm going to use the cwlite, it has the
[AD8331](https://www.analog.com/media/en/technical-documentation/data-sheets/AD8331_8332_8334.pdf)
chip (a **variable gain amplifier**, ``VGA``) and the
[AD9215](https://www.analog.com/media/en/technical-documentation/data-sheets/AD9215.pdf)
(an **ADC**).

The configuration of the ``VGA`` is such that the input impedance is 50 ohm
(see table 7 at page 30 of the datasheet) and
``AC``-coupled (so you don't have ``DC`` component); this explains why, since
the input is connected to the low side of the shunt resistor on the board, you
have negative readings: the high side is **ideally** constant (at the power
supply voltage) so, without ``AC``-coupling you would obtain something like

$$
V_{L} = V_H - I\times R_\hbox{shunt}
$$

but removing the constant voltage, what you see from the traces is

$$
AC(V_{L}) = AC(V_H) + AC(-I\times R_\hbox{shunt}) = AC(-I\times R_\hbox{shunt})
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
end the amplitude measured is really, up to a constant, the power 

#### Different instructions

First of all I need to see if different instructions have different
"energy-footprint", I try to show the power consumption of the target executing

 - 10 ``nop``s
 - 10 ``mul``s
 - 20 ``mul``s
 - 10 ``mul``s, 10 ``nop``s and 10 ``muls``

![](/images/side-channels/comparison-instructions.png)

the assembly code is the following for the last case (the other ones are simply subsection
of this)

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
that number. Moreover by sight I have the feeling that the traces generated by
different instructions are different but in the next section I try to come up
with something more useful.

### Correlation

In the last section I showed that different instructions have different
"footprints", probably the easiest possible way to use that is by timing
analysis: for example if we had a piece of code that checks
for a password and exits at the first wrong character, we could capture the power traces for
every possible (first char) input and
we should see only one having a different pattern.

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

What explanation is available for this behavious? Well, a modern processing unit
employs some trick to speed-up computation and a prevalent one is the
**pipeling**, i.e., splitting the instruction life cycle in different stages and
when the unit executed a given instruction is also doing other stuff with the
following instructions; in particular for the XMega we have this quote from the
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
Siglent using some python code that I wrote, but this is argument of the section
a little below. For now a little reasoning about statistics.

## Statistical distribution of inputs

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

| A | B | A \\(\oplus\\) B |
|---|---|-----------------|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

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

Since the **Hamming distance** is defined as [^HD]

$$
HD(S, D) = HW(S\oplus D)
$$


[^HD]: Hacker's delight pg95 and pg343

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
\langle\hbox{HW}(I\oplus k)\rangle &= \sum_{i\in I} p(i) \hbox{HW}(i\oplus k) \cr
&= \sum_{h_I = 0}^8 \sum_{i \in I_{h_I}} p(i) \hbox{HW}(i\oplus k) \cr
&= \sum_{h_I = 0}^8 \sum_{i \in I_{h_I}} p(i) \left(\hbox{HW}(k) + \Delta\hbox{HW}_k(i)\right) \cr
\end{align}
$$

$$
\begin{align}
&= \sum_{h_I = 0}^8 \sum_{i \in I_{h_I}} p(i) \hbox{HW}(k) + \sum_{h_I = 0}^8 \sum_{i \in I_{h_I}} p(i) \Delta\hbox{HW}_k(i) \cr
&= \hbox{HW}(k)\sum_{h_I = 0}^8 \sum_{i \in I_{h_I}} p(i)  + \sum_{h_I = 0}^8 \sum_{i \in I_{h_I}} p(i) \Delta\hbox{HW}_k(i) \cr
&= \hbox{HW}(k) + \sum_{h_I = 0}^8 \sum_{i \in I_{h_I}} p(i) \Delta\hbox{HW}_k(i) \cr
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

Now if we perform the experiment we obtain, studying only the power consumption
in relation to the 0th byte of input, as follow: it's possible to see "something
happening" only in the first iteration of the loop (actually there is something
going on also at the start of the second iteration, but "less").

![](/images/side-channels/constant-time-0th-hamming.png)

here the zoom

![](/images/side-channels/constant-time-0th-hamming-zoom.png)

Now I want to try something new: remember the stuff above about the ``xor``? in
this case I want to try to find for each sample the element which xor creates
the most correlated relation. And something interesting come out: obviously the
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

```
movw    r26, r14
ld      r20, X+
movw    r14, r26
ld      r25, Z+
eor     r25, r20
or      r24, r25
cp      r26, r18
cpc     r27, r19
brne    .-18
```

![](/images/side-channels/constant-time-cross-corr.png)

At this point manually crafted assembly comes to the rescue: with the following
code (and with a different password set to "armedilzo")

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


![](/images/side-channels/constant-time-unroll-manual-cross-corr.png)

In this implementation is lost the correlation with the actual password's bytes
since they are loaded separately at the start of the code


## Improve the sampling frequency

As I said at some point above, the tail present after the instruction bothered
me so I decided to try an experiment (I really like to double check stuff) and
to use my Siglent to try to capture a better sampled signal so to be able to
have a more precise signal.

Fortunately this scope exposes an API via USB using the ``pyvisa`` library, the
programming manual is not very clear but enough to obtain the same functionality
of the ``ADC`` on the chipwhisperer.

The chipwhisperer with the target running at 8MHz it's capable of 32Msamples at
for second with 10bits resolution, the other scope instead is capable of 1Gsamples for second but with 8bit
resolution. Another problem is that the chipwhisperer has each capture perfectly
aligned since the clock of target and ``ADC`` are in synch meanwhile for the
oscilloscope this is not true meaning that a process of alignment is needed
after the capture, reducing the quality of the end result.

If you are interested about the synchronization issue there is this [paper](https://eprint.iacr.org/2013/294.pdf)
named "Synchronous Sampling and Clock Recovery of Internal Oscillators for Side Channel Analysis and Fault Injection".

[A Case Study of Side-Channel Analysis using Decoupling Capacitor Power Measurement with the OpenADC](https://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.299.6185&rep=rep1&type=pdf)

[Coherent Sampling and Filtering to Improve SNR and THD](https://www.youtube.com/watch?v=LOJbztS-wFY&list=PLISmVLHAZbTTw_FuEdfRA2pl_SWzjGkUG&index=2)

If you encounter a problem like

    FAILED: XMEGA Command 20 failed: err=1, timeout=1

with the target of the CW-lite, this happened to me when I connected the
"measure" port of the chipwhisperer to the oscilloscope; in practice the board
refused to flash something. The workaround I found was to connect the "glitch"
port of the target to the "measure" port of the chipwhisperer: probably the
capacitor present in the frontend of the ``ADC`` helps to stabilize the voltage
allowing the target to start correctly.

https://stats.stackexchange.com/questions/64676/statistical-meaning-of-pearsonr-output-in-python

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

{{% wavedrom %}}
{ "signal": [
	{ "node": "...A..BC.." },
	{ "name": "D",   "wave": "x..2...x..", "data": ["data must be stable"] },
	{ "name": "CLK", "wave": "0.....1..." },
	{ "node": "...G..HI.." },
	{ "node": "...D..EF.." }
  ], "edge": [
	"A|D",
	"B|E",
	"C|F",
	"G<->H ts",
	"H<->I th"
], "config": { "hscale": 2 }}
{{% /wavedrom %}}

the maximum usable clock frequency of a processor is determined by the maximum delay among its elements,
in the sense that, if the operating frequency is so high that doesn't give enough time
to the signals to pass through all the logic gates to accomplish all its functions.

And this is one of the mechanisms that we are going to explit :) the other is the stability
of the voltage provided to the device: if there is not enough charge to switch the state of
an internal transistor, the final state is wrong.

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
 - [Pearson's correlation](https://www.statlect.com/fundamentals-of-probability/linear-correlation)
