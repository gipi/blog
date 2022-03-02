<!--
.. title: side channels: model of a processing unit
.. slug: side-channels-model-of-a-processing-unit
.. date: 2022-03-02 08:42:44 UTC
.. status: draft
.. tags: 
.. category: 
.. link: 
.. description: 
.. type: text
-->


To understand what follows you need a model of how a processing unit is composed
and how the single entities with their behaviour can tell us something about
what is happening during computation (that wasn't supposed to leak to you).

Obviously this won't be an exhaustive explanation, this is matter of high
profile studies, but as a physicist I can tell you that sometimes from very basic
assumptions is possible to deduce very important aspects of a system.

You should think of a processing device in the same way you think about a mechanical clock:
a source of motion, the pendulum, is transmitted via gears to show the correct
time on the display; in the same way an electronic device has a clock that
"gives the time" to its internal components!

To continue with this analogy, the parts that transmit "motion" are the wires where
the current "flows" and
In order to have current you need a power supply that provides an appropriate
voltage potential that causes the charges to move inside the wires.

However not all materials allow the passage of charge, the ones
with this property are named **conductors**, the materials without it are named
**isolants**. Without enter too deep in the physics involved, usually the
conductors have **electrons** available to move around. Take in mind that
conductivity is a relative term: with enough electric potential any material
can conduct electricity.

With something that approaces magic is possible to create a particular type of
semiconductor that behaves in a strange way **impurity semiconductors**: to a
intrinsic semiconductor crystal are added some _impurities_, i.e. elements that
provide a free electron to the 

When you put a p-type and n-type semiconductor in contact the area is called
**junction**; around this region, via thermal noise, the excess of electrons
from the n-type migrate to the p-type causing a polarization.

![](/images/side-channels/junction.png)

At this point this behaves like a **diode**: providing an adeguate difference of
potential is possible to generate a current but only in one direction: applying
a reverse voltage cause the polarization in the junction to increase blocking
further flow of current.

![](/images/side-channels/junction-forward-reverse.png)

The next step is to have a semiconductor with three regions (two junctions) of
alternating semiconductor types: this creates a **transistor**.  they have a lot
of property and a huge usage that would be an enourmous task to explain in
detail and it's of not importance in our understanding in this case [^AoE].
The core idea here is that the central region between the two junctions acts as
a "switch" to enable the flow of current on command (this is a **huge
oversimplification** but stick with me here).

![](/images/side-channels/triode.png)

[^AoE]: Art of Electronics has a couple of chapter dedicated to these concepts.

Now, exist a complete taxonomy of transistors but here
I'm limiting myself to a type of transistor named **MOSFET**, the first half of
the name it's an acronym for **M**etal **O**xide **S**emiconductor, the second
half it's an acronym for **F**ield **E**ffect **T**ransitor; 

{{% youtube id=Bfvyj88Hs_o %}}

N-channel MOS transistors have the sub-strate material of p-type and the drain and gate voltages
are positive with respect to the source during normal operation. The substrate is
the most negative electrode of an nMOS transistor.

Instead the P-channel MOS transistors are produced on an n-type substrate. The voltages
at the gate and drain of these pMOS transistors are negative with respect to the
source during normal operation. The substrate is the most positive electrode.

Generally NMOS are faster than PMOS [^1]

[^1]: p26-27 nanometer CMOS ICs

For now it's important to model a
transistor as a "switch", as something that allows the flow of current by a
signal. The convention for a FET transistor in schematics is the following [^3]

[^3]: a more precise representation has a fourth terminal that is the named the **body** that
represents the substrate the transistor is built on. Usually is connected to the
source.

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

If you work out the logic table for this device you see that it outputs the
inverted logic level of the input (the little circle to the gate of the
transistor \\(Q_1\\)) indicates that is a PMOS.

An actual die of an IC is costituted by at least
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

Let me introduce you a electronic device that usually is not well known, the
**transmission gate** [^2]: is a particular configuration of
transistors that acts as a switch that allows the transmission of signal only
when the select signal is enabled (in most of the cases is the clock signal).

[^2]: Section **3.4 FET switches** (pg171) Art of Electronics

On the left the implementation with complementary transistors and on the right
its schematic representation.

{{% pyplots %}}
import matplotlib
matplotlib.use('Agg')

import schemdraw
import schemdraw.elements as elm
from schemdraw import logic
d = schemdraw.Drawing()

d += (pfet_left := elm.PFet().up())
d += (nfet_left := elm.NFet().down())

d += logic.Tgate().at((10, 0)).right()

d.draw()
{{% /pyplots %}}

Now we can start with the reversing: from left to right we have an inverter
having as input the ``RESET`` signal, followed by two transmission gates.

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
# d += elm.LineDot().length(2).right().at(pfet_right.source).label('$output$', 'right')

# extra reference points
d += elm.Dot().at(nfet_left.drain).label('$A$', 'top')
d += elm.Dot().at(pfet_right.source).label('$B$', 'top')

d.draw()
{{% /pyplots %}}

That (?) elements form a ``NAND`` gate (note that the input named \\(C\\) is the signal \\(A\\)
negated):

{{% pyplots %}}
import matplotlib
matplotlib.use('Agg')

import schemdraw
import schemdraw.elements as elm
from schemdraw import logic
d = schemdraw.Drawing()

# place the PMOS in parallel
d += (pmos_a := elm.PFet().reverse().at((0, 0)).label('$C$', 'gate'))
d += (pmos_b := elm.PFet().reverse().at((d.unit, 0)).label('$D$', 'gate'))
d += (vdd_line := elm.Line().at(pmos_a.source).to(pmos_b.source))
d += (out_line := elm.Line().at(pmos_a.drain).to(pmos_b.drain))

# place the two NMOS in series
# (tricky placement of the NMOS_a in the middle of the output line)
d += (nmos_a := elm.NFet().reverse().anchor('drain').at(out_line.center).label('$C$', 'gate'))
d += (nmos_b := elm.NFet().reverse().label('$D$', 'gate'))

# VDD and GND
d += elm.LineDot().length(1).at(vdd_line.center).up().label('$V_{cc}$', 'right')
d += elm.Ground().at((nmos_b, 'source'))

# output
d += elm.LineDot().length(2).at(out_line.end).right().label('$B$', 'right')

d.draw()
{{% /pyplots %}}

The central element generates the inverted clock needed by the trasmission gates

The circuit now assumes the following shape (**to be completed**)

{{% pyplots %}}
import matplotlib
matplotlib.use('Agg')

import schemdraw
import schemdraw.elements as elm
from schemdraw import logic
d = schemdraw.Drawing()

d += elm.LineDot().label('$RESET$', 'left').right().reverse().length(0.5)
d += logic.Not()
d += (tgate_primary := logic.Tgate())
# d += elm.Line().right()

d.push()
d += elm.Line().right().length(1)
d += logic.Not().right()
d += elm.Line().right().length(1)
d += elm.Line().down()
d += (nand := logic.Nand().anchor('in2').left())
d += (tgate_secondary := logic.Tgate())
d.pop()

# a little hack to join the two transmission gates
# with straight perpendicular lines
# since the length of the lines doesn't match
d += elm.Line().to((tgate_primary.end.x, tgate_secondary.end.y))
d += elm.Line().to(tgate_secondary.end)

# the D line now
d += elm.Line().at(nand.in1).right().length(.5)
d += elm.LineDot().down().length(2).label('$D$', 'end')

d.draw()
{{% /pyplots %}}

that is a textbook latch (see Nanometer CMOS ICs, pg194) that usually is
represented via the following simbol

{{% pyplots %}}
import matplotlib
matplotlib.use('Agg')

import schemdraw
import schemdraw.elements as elm
from schemdraw import logic
d = schemdraw.Drawing()

d += elm.intcircuits.DFlipFlop(preclr=True)

d.draw()
{{% /pyplots %}}

https://www.eeweb.com/low-power-low-voltage-d-type-flip-flop/

If you are interested in stuff like this you can take a look at the
[reversing an FM synthesizer](https://www.wdj-consulting.com/blog/nmos-sample/)
that is a little more analogic.


From it the simplest "object" that is possible to build is the **register**: in the
example below four flip-flops are used to create a 4bits register

![](/images/side-channels/4-bits-register.png)

The existence of this component allows to build devices maintaining an internal
state, i.e. to build **sequential logic**, where the output doesn't depend only
on the present values of its input signals but also from its history;
generally this kind of logic can be built decomposing its internal state machine
in a register-like component and some combinatorial logic to obtain the next
configuration for its state

![](/images/side-channels/combinatorial-logic.png)

The clock signal is used to indicate **when** the transistion between states
happen. Using again the analogy with a mechanical clock, the sequential logic
blocks can be associated with the gears that "modulate" the motion of the
pendulum to create the visualization via the "hands".

For now this should be enough to understand the primitive building block of a
processing device, later I will elaborate a little more where the model just
described interacts with the physical world what can tell us and what we can do
to poke it :P
