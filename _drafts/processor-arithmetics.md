---
layout: post
comments: true
title: "Integer arithmetic from a computer point of view"
tags: [arithmetic, low level]
---

First of all, the arithmetic inside a CPU is done on register of fixed
size via the ``ALU``.

Since the register are size limited, all the arithmetic operations are intended
modulo the size of the registers.

## Integer encoding

### One's complement

It consists in flipping all the bits of a number, in this way
if you define the negative of a given number as the one's complement
of it you have the nice property that this two numbers summed are equal
to zero.

The problem is that you have two zero: all bits equal to zero and all
equal to one.

### Two's complement

It's an extension of the one's complement: to obtain the negative representation
of a number you have to take the one's complement and add one: in this way you have
an asymmetry between the minimum and maximum number that can be represented.

Normally in the code is this the way the negative numbers are represented.

Remember that a value into a register is not signed or unsigned by itself,
it depends on how is used in the code.

## Operations

### Extension

In certain cases could be necessary to do operations between numbers having a different
number of bits; if these numbers are unsigned it's not big deal, but if instead we having
signed ones we have to **sign extend** i.e. to complete the bits of the extended number
with all ``1``s.

## Flags

It's all fine and good but as already said, we have a limited number of bits
to represent numbers, so it's possible that some operations couldn't be done
correctly: for example, if you want to sum, in a 8bits-register ``0xff`` to
any other number, you can't fit the result in the register, you should have
a bit more; for this reason in a CPU you have also some flags (i.e. one-bit
values) usually contained in an unique register to indicate some particular
properties of the last arithmetic operation.

Each system has its own nomenclature and specific flags, but I think the minimal
set is composed of the following

### Carry flag

### Overflow flag

### Zero flag

## Programmation errors

### Out of bounds

### Signedness

### Overflow

### Wrap

## Links

 - [The CARRY flag and OVERFLOW flag in binary arithmetic](http://teaching.idallen.com/dat2343/10f/notes/040_overflow.txt)
 - [Intel x86 JUMP quick reference](http://unixwiz.net/techtips/x86-jumps.html)
 - [SEI CERT C Coding Standard](https://wiki.sei.cmu.edu/confluence/display/c/SEI+CERT+C+Coding+Standard)
