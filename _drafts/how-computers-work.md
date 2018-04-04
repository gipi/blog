---
layout: post
comments: true
title: "How computers work"
tags: [electronics, computer science, transistors]
---

In this post I'll try to unravel the complex layers by which
an electronics computing device is made of.

 - [Padraic Edgington's channel](https://www.youtube.com/channel/UC4ls2cPrXHfEO_oTHZcCclA)

## Transistors

I have to start somewhere so I decided to start from the way transistors are
used as **switch**: transistors are amazing piece of technology with an enormous
range of applications and explaining how they work would be a task too long.

This is a **NPN transistor**

![]({{ site.baseurl }}/public/images/computers/npn.png)

Let's start with a transistor in a configuration such that when it's connected
to ground the collector has a voltage equal to ``VCC`` and when is connected
to ``VCC`` causes the collector to drop to ground. This is the most common
configuration to drive high voltage load for example with an arduino.

![]({{ site.baseurl }}/public/images/computers/switch.png)

You notice that if we define ``VCC`` to be logic level 1 (or true) and
``GND`` to be 0 (or false) this device implements a logic operator ``NOT``
i.e. it inverts the logic signal at its input.

![]({{ site.baseurl }}/public/images/computers/switch.gif)


Obviously there are limits to the velocity to which the signal can change
and they effect the layer above it.


## Logic operators, Boolean logic and combinational logic

Is it possible to implement other logic operators using only transistors?
the answer is positive: below you can see using only NPN transistors.

![]({{ site.baseurl }}/public/images/computers/and-or.gif)

Take in mind that this only one typology of them, modern processor can
use other incarnation but the basic principles are the same.

For logic the following properties are valid (the product is the ``AND``
operator, the sum is the ``OR`` operator)

$$
\eqalign{
ABC &= \left(AB\right)C = A\left(BC\right)\cr
AB  &= BA \cr
AA  &= A \cr
A1  &= A \cr
A0  &= A \cr
A + 1 &= 1 \cr
A\left(B + C\right) &= AB + AC \cr
A + AB &= A \cr
A + B + C &= \left(A + B\right) + C = A + \left(B + C \right) \cr
\overline{\left(AB\right)} = \overline A + \overline B \cr
}
$$

The important point here is that any boolean function than be represented
as sum of subfunctions represented as only products of its inputs.
This represents the [minterm canonical form](https://en.wikipedia.org/wiki/Canonical_normal_form).
What does it mean? It means that all the digital circuits that you can create,
operating on whatever number of inputs is buildable using boolean algebra and since
transistors are an implementation of this, then we can create all with them.

Obviously we need circuits able to have more than one output, but I think
is obvious how to extend this reasoning.

This circuits that have output effected immediately from the input are
called **combinational circuits**. In order to build useful circuits
we need something that has memory and hence the concept of **time**.

## Latch and Flip-Flop

If we come back to transistor for an experiment: look at this circuit

![]({{ site.baseurl }}/public/images/computers/latch-sr.gif)

is called **latch** and represents a metastable circuit: has two
stable configurations that maintains if the switch arent' operated.
Using the analogy with the ``NOT`` operator we can represent it in the following
way

![]({{ site.baseurl }}/public/images/computers/latch-not.gif)

Well, this could be used as a memory but is missing some input
signals, so if we re-elaborate it using logic gates we can produce
the following circuit

![]({{ site.baseurl }}/public/images/computers/latch-not.gif)

What is missing from the picture is the representation of time: we can
synchronize the operations using a periodic alternating signal that we
represents as a square wave and we call **clock**. The moment in time when
the clock passes from low to high is called **raising edge**, the opposite
is called **falling edge**.

In order to make the synchronous operations less dependent from varying signals
the flip-flops take they inputs only during the rising edge.

AoE pg 728.

## Tristate, Open collector and Bus

A last thing before leaving transistors and start to utilize logic operators
and flip-flop as building block: how we can connect digital circuits that need to talk
without connecting directly each to all the other ones? An idea is to use a **bus**,
i.e. a line of a certain number of signals to which all the circuits are connected
to read and write data.

The problem is, how we avoid that one device "talks over the other"? With a transistor
we can use the configuration called **open collector**

A better solution is the **three state logic**: it doesn't add a new logic state other
than true and false but add a new signal named **enable** that indicate if the output
is seen as open from the outside

For more information AoE pg 721.

## Sequential circuits

Thanks to flip-flops we can circuits that have memory, the first example of it is a counter:
we want to design a circuit that has two input signals: **clock** and **enable**, the first
is what keep the time and the second tells when to add one to the circuit. We start with
a single stage, i.e. one bit having two output: **the digit** and the **carry**.

To describe the circuit we can us this table

| EN | A previous | A next | C |
|----|----|---|---|
| 0  | 0  | 0 | 0 |
| 1  | 0  | 1 | 0 |
| 0  | 1  | 1 | 0 |
| 1  | 1  | 0 | 1 |

Looking for the digit entry we see that using minterms we can describe the relation
using the following formula

$$
A_{\hbox{next}} = A_{\hbox{previous}}\cdot\overline{EN} + \overline{A_{\hbox{previous}}}\cdot EN = A_{\hbox{previous}}\oplus EN
$$

where the \\(\oplus\\) operation means ``XOR`` i.e. **exclusive OR**.

![]({{ site.baseurl }}/public/images/computers/counter-single-stage.gif)

Take in mind that the value is taken exclusively at the edge of the clock so the carry
is working as expected, if you want it to maintain its value you need another flip-flop,
for this reason is very important make a circuit synchronous as much as possible (I'm
not an expert but seems reasonable to me).
