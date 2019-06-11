---
layout: post
comments: true
title: "Integer arithmetic from a computer point of view"
tags: [arithmetic, low level, WIP]
---

A thing that is overlooked is the way arithmetic operations work in a computer
and specifically in the processing unit: not having a clear idea of how
the operations are performed and their limitations can cause very important
bug to happen and also help in case you want to reverse unknown code.

## Integer encoding

We are interested of the case of a register containing a number: since
First of all, the arithmetic inside a CPU is done on register of fixed
size via the ``ALU`` and since the register are size limited, all the
arithmetic operations are intended modulo the size of the registers.

the register has a fixed number of bits (let's say is \\(N\\)) we can
only represent (directly) unsigned values between \\(0\\) and \\(2^N - 1\\).

The formula is the following

$$
b = \sum_{i = 0}^{N - 1} b_i 2^i
$$

Remember the following properties for binary numbers: **completness**

$$
\sum_{n = 0}^{N} 2^n = 2^{N + 1} - 1
$$

and **shifting - multiplication relation**

$$
\eqalign{
2\cdot2^N &= 2^N + 2^N \cr
          &= 2^N + \sum_{i = 0}^{N - 1} 2^i + 1 \cr
          &= 2^N + 2^{N - 1} + 2^{N - 2} + \dots + 2^1 + 2^0 + 1 \cr
          &= \sum_{i = 0}^N 2^i + 1 \cr
          &= 2^{N + 1} - 1 + 1 \cr
          &= 2^{N + 1} \cr
}
$$

that means that left shifting a binary number is equivalent to multiplying
the same number for a power of two (I know, I know, this is obvious).

For signed numbers there is not a unique way to represent them: the quick
and dirty way would be to use the most significant bit as **sign bit** but this has
the drawback to have two zeros.

I think that this encoding is not used by anyone in the real world (but I could be
wrong), there are more efficient ways.

### One's complement

It consists in flipping all the bits of a number, in this way
if you define the negative of a given number as the one's complement
of it you have the nice property that this two numbers summed are equal
to zero. However you have to add one to a subtraction to obtain the
correct result

$$
\hbox{one}(x) = 2^N - x
$$

$$
-x = \hbox{one}(x) + 1
$$

The problem is that you have two zeros: all bits equal to zero and all
equal to one.

### Two's complement

It's an extension of the one's complement: to obtain the negative representation
of a number you have to take the one's complement and add one: in this way you have
an asymmetry between the minimum and maximum number that can be represented, i.e.
you can represent values between \\(-2^{N - 1}\\) and \\(2^{N - 1} - 1\\). For example
with 7 bits you have the interval \\((-64, 63)\\).

$$
w = - a_{N - 1}\, 2^{N - 1} + \sum_{i = 0}^{N - 2} a_i\,2^i
$$

Normally in the code is this the way the negative numbers are represented.

Mind blowing realization is that the two's complement of the lowest integer
is itself:

$$
\hbox{two}\left(\tt 0x10000000\right) = {\tt 0x01111111} + 1 = {\tt 0x10000000}
$$

Remember that a value into a register is not signed or unsigned by itself,
it depends on how is used in the code.

## Operations

We have a representation of numbers in binary that can handle unsigned and signed, but we need
to do math with them and we have to manage the limits of having a fixed bit width but
at the end of the day is not impossible in practice.

### Addition and Subtraction

The simplest operation is the addition: we simply use the rules from the normal math but since
we have a fixed number of bits we cannot sum two number and have the result in a register
with the same number of bits, indeed if with \\(N\\) bits we can have as a maximum unsigned value \\(2^N-1\\)
if we sum itself we obtain 

$$
\eqalign{
    \hbox{max}_u(N) + \hbox{max}_u(N) &= 2^N - 1 + \left(2^N - 1\right) \cr
    &= 2\cdot2^N - 2 \cr
    &= 2^{N+1} - 2 \cr
    &= \hbox{max}_u(N + 1) - 1 \cr
}
$$

i.e. is possible, with one bit more, to represent more numbers that is possible to obtain (think for example
in a register with width 4-bit, you have 7 has a maximum unsigned number, so the maximum result of a sum
for this case is 14 that is less that 15, the maximum unsigned possible with 5 bits).


### Multiplication

Multiplication is straightforward as well, I mean, there are operations from a processor that
implement that;

$$
\eqalign{
    \hbox{max}_u(N)\cdot\hbox{max}_u(N) &= \left(2^N - 1\right)\cdot\left(2^N - 1\right) \cr
    &= 2^{2N} - 2\cdot2^N + 1 \cr
    &= 2^{2N} - 2^{N + 1} + 1 \cr
    &= 2^{2N} - 1 + 1 - 2^{N + 1} + 1 \cr
    &= \hbox{max}_u(2N) - 2^{N + 1} + 2\cr
    &= \hbox{max}_u(2N) - \left(2^{N + 1} - 2\right)\cr
    &= \hbox{max}_u(2N) - 2\cdot\left(2^{N} - 1\right)\cr
    &= \hbox{max}_u(2N) - 2\cdot\hbox{max}_u(N)\cr
}
$$

so we can contain a result for sure if we use two registers for the destination (like the ``x86`` does
with the ``mul`` operation).

If we take two 4-bit number and we multiply them together we obtain as maximum result \\(15\cdot15 = 225\\)

### Division

### Sign extension

In certain cases could be necessary to do operations between numbers having a different
number of bits; if these numbers are unsigned it's not big deal, but if instead we having
signed ones we have to **sign extend** i.e. to complete the bits of the extended number
with all ``1``s.

Let me make an example: if we have a 8-bit register with the decimal value \\(-16\\),
its representation with two's complement will be ``0xef``; now, if we want to put this
value into a 16-bit register and represent the same number, we have to set as most significant
byte ``0xff``, i.e. ``0xffef``: this because of a nice property of binary numbers, namely

in our case we have the Mth bit used for the sign and suppose we have other \\(s\\) bits

$$
\eqalign{
-2^M + \sum_{i=s}^{M-1} 2^i + \sum_{i=0}^{s - 1} 2^i &= - 1 \cr
-2^M + \sum_{i=s}^{M - 1} 2^i                        &= \sum_{i=0}^{s - 1} 2^i - 1 \cr
-2^M + \sum_{i=s}^{M - 1} 2^i                        &= 2^{s} - 1
}
$$

$$
\eqalign{
\left(-2^N + 2^{N - 1} + 2^{N - 2} + \dots + 2^s\right) - \left(-2^s\right) &= -2^N + 2^{N - 1} + 2^{N - 2} + \dots + 2^s + 2^s \cr
 &= -2^N + 2^{N - 1} + 2^{N - 2} + \dots + 2^s + \left[\left(\sum_{i = 0}^{s - 1}2^i\right) + 1\right] \cr
 &= -2^N + 2^{N - 1} + 2^{N - 2} + \dots + 2^s + 2^{s - 1} + 2^{s - 2} + \dots + 2 + 2^0 + 1 \cr
 &= -2^N + \sum_{i = 0}^{N - 1} 2^i + 1 \cr
 &= -2^N + 2^N - 1 + 1 \cr
 &= 0 \cr
}
$$

Some architectures have direct instructions to do that, like the [movxs](http://www.c-jump.com/CIS77/ASM/DataTypes/T77_0270_sext_example_movsx.htm) in x86, other instead
[use multiple operations to do the same]({% post_url 2018-03-04-reversing-avr-code %}#sign-extension)

## Flags

It's all fine and good but as already said, we have a limited number of bits
to represent numbers, so it's possible that some operations couldn't be done
correctly: for example, if you want to sum, in a 8bits-register ``0xff`` to
any other number, you can't fit the result in the register, you should have
one bit more; for this reason in a CPU you have also some flags (i.e. one-bit
values) usually contained in an unique register to indicate some particular
properties of the last arithmetic operation. Take in mind that [not all
architectures have it](https://en.wikipedia.org/wiki/Status_register#CPU_architectures_without_arithmetic_flags).

Each system has its own nomenclature and specific flags, but I think the minimal
set is composed of the following

### Carry flag (CF)

Used in unsigned numbers to indicate that the result doesn't fit in the register; for an
addition is pretty clear what that means, for a subtraction is a little tricky since
this flag can be used for this operation as **borrow flag** (see [wikipedia](https://en.wikipedia.org/wiki/Carry_flag#Carry_flag_vs._borrow_flag)).

There are two schools of thoughts: some architectures (like ``x86``) use the borrow
bit, others (like ``ARM``) use the carry and the relation \\( (a - b) = a + \hbox{not}(b) + 1\\).

### Overflow flag (OF)

Used for signed numbers to indicate that the resulting sign bit is not coherent
with the correct result; for example with 4-bit (binary) numbers we can have the
following four cases:

$$
\eqalign{
    0100 + 0100 &= 1000 \quad\hbox{overflow} \cr
    1000 + 1000 &= 0000 \quad\hbox{overflow} \cr
    0100 + 0001 &= 0101 \quad\hbox{no overflow} \cr
    1100 + 1100 &= 1000 \quad\hbox{no overflow} \cr
}
$$

It's important to stress that the ``OF`` doesn't indicate an overflow into the sign
bit, but that the sign bit is wrong: in the last example above you can see that although
there is a carry bit into the sign bit, at the end of the calculation the sign is right.

If you want a more in deep explanation, this [post](http://www.righto.com/2012/12/the-6502-overflow-flag-explained.html)
about the ``OF`` of the 6502's ``ALU`` is amazing.

### Zero flag (ZF)

The last operation resulted in a result equal to zero, like subtracting two registers containing
the same value or doing the logical ``and`` operation between two registers having both zero as value.

## Flow control

At the end of the day the flags are used primarly to do the so called **flow control** that in
high level languages is implemented via ``if``, ``while``, ``for``, etc...

Each architecture implements this with some particular couple of family of instructions: one family to
set the flag, like ``cmp`` and ``test``, and another to jump to a particular location depending on the
particular values the flags have, like ``jmp``, ``jne``, ``jnz``
and so on in ``x86`` or ``b``, ``bne``, ``ble`` etc... in ``ARM``.

Take in mind that in an instruction like ``cmp arg1, arg2`` is ``arg2`` that is subtracted from ``arg1``.

For an **unsigned** comparison is sufficient to look at the ``CF`` to understand if a number is greater
than another.

For a **signed** number it's trickier: the greater condition is achieved if the sign bit is not set
and no overflow happened (i.e. the sign bit is consistent) or if the sign bit is set (i.e. the number
is negative) and the overflow happened (making the sign bit wrong).

For the equal condition is sufficient to check the ``ZF``.

## Programmation errors

### Out of bounds

### Signedness

### Overflow

### Wrap

### Conversion

### Undefined behaviour

Having an asymmetry between the size of the greatest positive and lowest negative in two's complement arithmetics
causes some particular behaviour to happen for some functions: take for example the ``abs()`` one; this function
returns the positive version of (almost) any number, indeed what is the positive value of the lowest negative
possible in a given architecture (in two's complement arithmetics)? From the man page we can read that
``Trying to take the absolute value of the most negative integer is not defined.`` so the following
code is not doing what you would expect when is passed ``INT_MIN`` as argument

```
#define MAX_VALUE 5000

char buffer[MAX_VALUE];

int arg1 = atoi(argv[1]);

if (abs(arg1) < MAX_VALUE) {
    buffer[arg1] = arg2;
}
```

## Links

 - [The CARRY flag and OVERFLOW flag in binary arithmetic](http://teaching.idallen.com/dat2343/10f/notes/040_overflow.txt)
 - [Intel x86 JUMP quick reference](http://unixwiz.net/techtips/x86-jumps.html)
 - [SEI CERT C Coding Standard](https://wiki.sei.cmu.edu/confluence/display/c/SEI+CERT+C+Coding+Standard)
 - [Condition Codes 1: Condition Flags and Codes](https://community.arm.com/developer/ip-products/processors/b/processors-ip-blog/posts/condition-codes-1-condition-flags-and-codes) from ARM site
 - [Jumps, flags, and the CMP instruction](https://www.hellboundhackers.org/articles/read-article.php?article_id=729)
 - [The 6502 overflow flag explained mathematically](http://www.righto.com/2012/12/the-6502-overflow-flag-explained.html)
 - [Avoiding Overflow, Underflow, and Loss of Precision](https://www.codeproject.com/Articles/25294/Avoiding-Overflow-Underflow-and-Loss-of-Precision) "The cardinal rule in numerical analysis is to avoid subtracting nearly equal numbers. The more nearly equal two numbers are, the more precision is lost in the subtraction"
