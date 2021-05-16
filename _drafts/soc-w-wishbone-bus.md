---
layout: post
comments: true
title: "Designing a SOC using a wishbone bus"
tags: [electronics,verilog, wishbone]
---

Here we go again, last time I've done some experimenting with simulation, now I'll try to improve over my VGA controller,
adding some processing capabilities. Yes I'm going to implement a **very** simple CPU in verilog.

But wait! First I'll try to implement an internal bus using the ``wishbone`` specification in order to have
the (future) components of the SoC talking together.

## Introduction to Wishbone

In a similar way applications or functions talk together via an interface defined
by their API, hardware components, like memory, video controller etc... need a
"contract" about the way they will communicate what is needed to accomplish
their role. Since we are talking about electronics and digital circuits the
obvious material manifestation of this interface are the signals the different
peripherals are connected to.

The first idea could be to connect each device to each other in order to
communicate but it's pretty obvious that that will escalate quickly! the more
reasonable idea is to use a common given grouping of signals that is used only
when needed by the peripherals active in a given moment.

For example in my simple **system on chip** (SoC) I would like to have a
**bootrom** containing the boot up code that initialize the device itself and
its peripherals, a **static ram** to use primarly for the startup stack, a **VGA
controller** and a **UART controller**; my idea is to use a common memory
interface and having different memory ranges allocated for each peripherals.

![]({{ site.baseurl }}/public/images/soc/soc.png)

Defining such grouping of signals is not a simple task, moreover there is not a
unique solution to it so you can imagine that are available a lot of such
interfaces and you need to have **all** the peripherals "talk" the same
protocol.

What I'm going to use is the bus specification named **wishbone**, it's an open
[specification](https://zipcpu.com/doc/wbspec_b4.pdf) and largely used, also professionally.

The main point of this bus specification is that exists a peripherals with the
role of **main** and **secondary** (the specification uses the older
terminology, but [I decided to drop it](https://cdm.link/2020/06/lets-dump-master-slave-terms/)).

The principal signals are the following (see sections ``2.2.3`` and ``2.2.4`` from the specification)

| Signal nick | Name | Description main | Description secondary |
|-------------|------|------|
| ``CYC_x``   | cycle | **Output** A valid bus cycle is in progress, the signal is asserted for the duration of all bus cycles. When this signal is negated, all other signals are invalid. | **Input**. It respondes only when this signal is asserted. |
| ``STB_x``   | strobe | **Output** Indicates a valid data transfer cycle, it is used to qualify various other signals on the interface | **Input**, when asserted indicates that it is selected and shall respond to other WISHBONE signals only when this signal is asserted (except for the reset signal) |
| ``ACK_x``   | acknowledge | **Input** that indicates the termination of a normal bus cycle | 
| ``STL_x`` | stall | **Input**, the secondary is not currently able to accept the transfer |
| ``WE_x``  | write enable | **Output** that indicates if is a read or write operation | |
| ``SEL_x`` | select signal | **Output** indicating the "width" of the data interaction | |
| ``RST_I`` | reset | ``STB_O`` and ``CYC_O`` must be negated | |

They exist other two signals that must be used, named **SYSCON** that are the
``RST_x`` and ``CLK_I`` that are common in all the digital circuit (see section
``2.2.1`` from specification). In particular all the outputs are registered at
the raising edge of ``CLK_I``. Instead ``RST_I`` forces all the wishbone
interfaces to restart (probably in a well known initial state).

Take in mind from ``RULE 3.40`` that

    As a minimum, the MASTER interface MUST include the following signals:
    [ACK_I],[CLK_I], [CYC_O], [RST_I], and [STB_O]. As a minimum, the SLAVE
    interface MUST include the following signals: [ACK_O], [CLK_I], [CYC_I],
    [STB_I], and [RST_I]. All other signals are optional.

## Handshaking protocol

There are two way of doing a bus cycle with this kind of bus: **standard** and
**pipelined**.

Long story short: they are practically identical but the pipelined allows to
stream continuously data: it will be clearer in a moment.

Just a note: in the following I'll explain what I'm implementing in my case; I'm
not sure what the specification really says, see the section
[Contradictions](#contradictions) below about my doubts.

In practice raising ``STB`` for a clock cycle defines a request from the master;
the secondary must respond with to this request raising ``ACK`` for a clock cycle but this can happen
at any time. A set of requests forms a **cycle** during which the ``CYC`` signal must be raised.
Note that when ``STL`` is asserted the master waits until is negated before
issuing a new request (mainting ``STB`` asserted).

With "defining" a request I mean that the value intended to be communicated to
the other side are valid when such signal is asserted at the rasing edge of the
clock.

### Standard


### Pipelined

The main difference is that now the main is not waiting for the terminating
signals to issue a new request

    PERMISSION 3.40
    If a MASTER doesn’t generate wait states, then [STB_O] and [CYC_O] MAY be assigned
    the same signal.

    OBSERVATION 3.55
    [CYC_O] needs to be asserted during the entire transfer cycle. A MASTER that doesn’t
    generate wait states doesn’t negate [STB_O] during a transfer cycle, i.e. it is asserted the
    entire transfer cycle. Therefore it is allowed to use the same signal for [CYC_O] and
    [STB_O]. Both signals must be present on the interface though.

``STALL_O`` indicates if is possible to issue a new request **but should be
raised at the time of the previous ``ACK``**.

## Memory secondary


{% github_sample_ref gipi/electronics-notes/blob/master/fpga/mojo/SOC/modules/blockrams/wb_memory.v %}
{% highlight verilog%}
{% github_sample gipi/electronics-notes/blob/master/fpga/mojo/SOC/modules/blockrams/wb_memory.v %}
{% endhighlight %}

## UART

Another peripheral I have developed is a ``UART``: this explore a little more
the concept of internal addresses, having tree one byte registers, respectively
for control, reading and writing.

**Note:** for this peripheral I could have used the stall signal to indicate
that a communication is ongoing but this would block all the memory accesses
(and more importantly the cpu itself); take into account that the communication
speed is much slower than the actual clock the cpu runs on, adding problems.

The solution adotted is to use a particular (bit at an) address to indicate if the previous
transmission completed.

{% github_sample_ref gipi/electronics-notes/blob/master/fpga/mojo/SOC/modules/UART/wb_uart.v %}
{% highlight verilog%}
{% github_sample gipi/electronics-notes/blob/master/fpga/mojo/SOC/modules/UART/wb_uart.v %}
{% endhighlight %}

## Bus decoding

What about having more secondary to contact, we could want to access a secondary UART
peripheral or a SDRAM controller, how can we select the right one to talk with?

In the specification is indicated to use a **partial address decoding**, i.e.
from my understanding, using part of the address to select the secondary to which
send the ``STB`` signal; the remaining (usually the "lower part") of the
addressing it used to indicate the secondary what we want.

For example, suppose we have four secondary devices with one main, each one is
mapped to a different range of memory

| Device | Range |
|--------|-------|
| ``UART`` | 0xaffff-0xa0000 |
| ``GPIO`` | 0xbffff-0xb0000 |
| ``SRAM`` | 0xcffff-0xc0000 |

the idea is of using the most significative byte as a "selector" of the device and
passing unaltered the remaining bits to interact directly with the peripheral.

From the diagram below you see that the address line goes from the master to the
address decoder that internally selects (via a multiplexer probably) where to
direct the ``STB`` line

![]({{ site.baseurl }}/public/images/soc/wishbone-bus-decoding.png)

Obviously ``CYC``and the other signals are shared among all the
secondary but only the one having the "live" ``STB`` is going to interact with the
main.

The only remaining aspect to take into account is something very important:
being a bus where all the peripherals share the signal lines means that the same
signal can have conflicting driving device: only one secondary is going to react
to the ``STB`` signal via its ``ACK``, raising it, but the other will maintain
not asserted its own.

There are two way to resolve this: one is to use a multiplexer that connect the
needed line back to the main, the other is to have the secondary not interacting
setting up the ``ACK`` line in **high impedence** mode.

{% github_sample_ref gipi/electronics-notes/blob/master/fpga/mojo/SOC/soc.v %}
{% highlight verilog %}
{% github_sample gipi/electronics-notes/blob/master/fpga/mojo/SOC/soc.v %}
{% endhighlight %}

## Contradictions

Here will collect some pieces of the specifications that don't make sense (to me).

The specification starts describing it with these words: from the main point of
view we have

    the MASTER asserts [STB_O] when it is ready to transfer data.
    [STB_O] remains asserted until the SLAVE asserts one of the cycle terminating signals
    [ACK_I], [ERR_I] or [RTY_I]. At every rising edge of [CLK_I] the terminating signal is
    sampled. If it is asserted, then [STB_O] is negated

instead the other side

    RULE 3.35
    In standard mode the cycle termination signals [ACK_O], [ERR_O], and [RTY_O] must be
    generated in response to the logical AND of [CYC_I] and [STB_I].

    RULE 3.50
    SLAVE interfaces MUST be designed so that the [ACK_O], [ERR_O], and [RTY_O] signals
    are asserted and negated in response to the assertion and negation of [STB_I].

It's all fine and good until you take a look at the timing diagram in which you
see that ``ACK_I`` and ``STB_O`` are negated at the same time that is impossible
by the rules above.

Also the timing diagram doesn't make much sense since ``ACK`` couldn't react to
``STB`` at the same raising edge of the clock in which ``STB`` reacts to it (I'm
talking of the fourth raising edge where both are negated).

![]({{ site.baseurl }}/public/images/soc/wb-time-diagram-wrong.png)

If in pipeline mode, it's not specified that the ``STALL`` should indicates that
the **next** request is not possible. 

## Linkography

 - [WISHBONE specification](https://zipcpu.com/doc/wbspec_b4.pdf)
 - [Building a prefetch module for the ZipCPU](https://zipcpu.com/zipcpu/2017/11/18/wb-prefetch.html)
 - [Building a Simple Wishbone Master](https://zipcpu.com/blog/2017/06/08/simple-wb-master.html)
 - [WISHBONE Frequently Asked Questions (FAQ)](http://www.pldworld.com/_hdl/2/_ip/-silicore.net/wishfaq.htm)
 - [Beginning Logic Design – Part 6](https://suchprogramming.com/beginning-logic-design-part-6/)
 - [Classic RISC pipeline](https://en.wikipedia.org/wiki/Classic_RISC_pipeline)
 - [The ZipCPU's pipeline logic](https://zipcpu.com/zipcpu/2017/08/23/cpu-pipeline.html)
 - http://www-5.unipv.it/mferretti/cdol/aca/Charts/02-pipeline-MF.pdf
 - https://cs.stanford.edu/people/eroberts/courses/soco/projects/risc/pipelining/index.html
 - http://www.iet.unipi.it/m.cimino/tweb/tia/risc.pdf
 - [krevanth/ZAP](https://github.com/krevanth/ZAP) a pipelined ARMv4T architecture compatible processor with cache and MMU
