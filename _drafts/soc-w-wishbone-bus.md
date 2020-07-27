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

## Wishbone

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

Defining such grouping of signals is not a simple task, moreover there is not a
unique solution to it so you can imagine that are available a lot of such
interfaces and you need to have **all** the peripherals "talk" the same
protocol.

What I'm going to use is the bus specification named **wishbone**, it's an open
[specification](https://zipcpu.com/doc/wbspec_b4.pdf) and largely used, also professionally.

The main point of this bus specification is that exists a peripherals with the
role of **main** and exists 

The principal signals are the following (see sections ``2.2.3`` and ``2.2.4`` from the specification)

| Signal nick | Name | Description master | Description slave |
|-------------|------|------|
| ``CYC_x``   | cycle | A valid bus cycle is in progress, the signal is asserted for the duration of all bus cycles |
| ``STB_x``   | strobe | Indicates a valid data transfer cycle, it is used to qualify various other signals on the interface | The strobe input, when asserted, indicates that the SLAVE is selected A SLAVE shall respond to other WISHBONE signals only when this signal is asserted (except for the reset signal) |
| ``ACK_x``   | acknowledge | Input that indicates the termination of a normal bus cycle | 
| ``STL_x`` | stall | the slave is not currently able to accept the transfer |
| ``RST_x`` | reset | ``STB_O`` and ``CYC_O`` must be negated |


Take in mind from ``RULE 3.40`` that

    As a minimum, the MASTER interface MUST include the following signals:
    [ACK_I],[CLK_I], [CYC_O], [RST_I], and [STB_O]. As a minimum, the SLAVE
    interface MUST include the following signals: [ACK_O], [CLK_I], [CYC_I],
    [STB_I], and [RST_I]. All other signals are optional.

### Handshaking protocol

There are two way of doing a bus cycle with this kind of bus: **standard** and
**pipelined**.

RULE 3.35
In standard mode the cycle termination signals [ACK_O], [ERR_O], and [RTY_O] must be
generated in response to the logical AND of [CYC_I] and [STB_I].

RULE 3.50
SLAVE interfaces MUST be designed so that the [ACK_O], [ERR_O], and [RTY_O] signals
are asserted and negated in response to the assertion and negation of [STB_I].

## Memory slave


{% github_sample_ref gipi/electronics-notes/blob/c572bb618eb9d7acc8beba15a417572ed2741e3f/fpga/mojo/SOC/modules/blockrams/wb_memory.v %}
{% highlight verilog%}
{% github_sample gipi/electronics-notes/blob/c572bb618eb9d7acc8beba15a417572ed2741e3f/fpga/mojo/SOC/modules/blockrams/wb_memory.v %}
{% endhighlight %}

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
