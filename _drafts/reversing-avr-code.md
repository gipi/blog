---
layout: post
comments: true
title: "Getting started to reverse AVR code"
tags: [reversing, AVR, WIP]
---

## Registers

 - ``x`` stands for ``r27:r26``
 - ``y`` stands for ``r29:r28`` also is the frame pointer
 - ``z`` stands for ``r31:r30`` and is used as argument for ``eicall``
 - ``r0`` is a temporary register
 - ``r1`` is usually zero

## Harvard architecture

## Arithmetic

It's important to understand how mathematics works with registers:
the first thing to learn is that (in all the architecture) the arithmetic
is module the number of bits; the other thing is that negative numbers
are implemented via **two's complement** but before explaining that
I need to explain **one's complement**.

### One's complement

It consists in flipping all the bits of a number, in this way
if you define the negative of a given number as the one's complement
of it you have the nice property that this two numbers summed are equal
to zero.

The problem is that you have two zero: all bits equal to zero and all
equal to one.

### Two's complement

## Examples

Below take a look to some examples of common routines implemented
with this language

### strlen

```
    movw r30, r24
loop:
    ld r0, z+
    tst r0
    brne loop

    com r24
    com r25
    add r24, r30
    adc r25, r31
    ret
```

Here the tricky part are the last five instructions (not ``ret`` of course):
when the ``r0`` contains a NULL byte then ``z`` point to the address of that byte
plus one (remember the post-increment addressing), so the ``com`` (the one's complement),
and ``add/adc`` instructions can be summarized as follow

$$
\eqalign{
r25:r24 &= r31:r30 + \left(r25:r24 \oplus ffff\right)\cr
        &= r31:r30 - 1 + \left(r25:r24\oplus ffff +1\right)\cr
        &= r31:r30 - 1 - r25:r24\cr
        &= \hbox{pointer to the next address fo the NULL byte} - 1 - \hbox{pointer to the start of the string}\cr
        &= \hbox{number of bytes not NULL}
}
$$

### memcpy

```
    movw r30, r22
    movw r26, r24
    rjmp start
loop:
    ld r0, z+
    st x+, r0
start:
    subi r20, 0x01
    sbci r21, 0x00
    brcc loop
    ret
```

### Sign extension

This section explains how I arrived to understand the meaning of this
piece of code:

```
lds r24, y+1
lds r25, y+2
mov r0, r25
lsl r0
sbc r26, r26
sbc r27, r27
```

initialy didn't make any sense, it loads from the stack a short and then left-shifts
the most significant byte; to end it subtracts two unrelated registers using the result
of the shifting as carry.

Pratically ``r26`` and ``r27`` are always zero if the last bit of ``r25`` is zero, if
it's not zero then ``r27:r27`` are equal to ``ffff``. Seems sign extension to me.

In order to prove my point I decided to experiment and to experiment
I need to create a test case where I cast a variable from short to 32bits
like the following:

```
$ cat extended.c
#include<stdint.h>

int32_t miao(short value) {
    return (int32_t)value;
}
$ avr-gcc -c extended.c
```

Once compiled I can look at the assembly code generated and **bingo**

```
$ r2 -A -a avr extended.o
[0x08000034]> pdf
/ (fcn) entry0 44
|   entry0 ();
|           0x08000034      cf93           push r28                    ; [01] m-r-x section size 44 named .text
|           0x08000036      df93           push r29
|           0x08000038      00d0           rcall 0x800003a
|           0x0800003a      cdb7           in r28, 0x3d                ; '=' ; IO SPL: Stack lower bits SP0-SP7
|           0x0800003c      deb7           in r29, 0x3e                ; '>' ; IO SPH: Stack higher bits SP8-SP10
|           0x0800003e      9a83           std y+2, r25
|           0x08000040      8983           std y+1, r24
|           0x08000042      8981           ldd r24, y+1
|           0x08000044      9a81           ldd r25, y+2
|           0x08000046      092e           mov r0, r25
|           0x08000048      000c           lsl r0
|           0x0800004a      aa0b           sbc r26, r26
|           0x0800004c      bb0b           sbc r27, r27
|           0x0800004e      682f           mov r22, r24
|           0x08000050      792f           mov r23, r25
|           0x08000052      8a2f           mov r24, r26
|           0x08000054      9b2f           mov r25, r27
|           0x08000056      0f90           pop r0
|           0x08000058      0f90           pop r0
|           0x0800005a      df91           pop r29
|           0x0800005c      cf91           pop r28
\           0x0800005e      0895           ret
```

