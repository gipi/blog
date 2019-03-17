---
layout: post
comments: true
title: "Getting started to reverse AVR code"
tags: [reversing, AVR, WIP]
---

First of all, the instructions used on ATMel's chips are **RISC**-like, aligned
to 2-byte addresses but with instructions that can be 16 or 32-bit long.

## Registers

The registers have all 8-bit size.

 - ``pc`` is the **program counter**, cannot be modified directly. Since the instructions
are all two bytes longs (a word), the value inside this register is an index of words.
 - ``x`` stands for ``r27:r26``
 - ``y`` stands for ``r29:r28`` also is the frame pointer
 - ``z`` stands for ``r31:r30`` and is used as argument for ``eicall``
 - ``r0`` is a temporary register
 - ``r1`` is usually zero
 - ``r2`` to ``r25`` are general purpose registers, used also for calling subroutines (see
below the section about calling conventions).

What is missing from this list is the **stack pointer**: it's not a directly accessible
register, it's implemented using the memory address couple ``0x3e:0x3d``, see the section about
the prologue of a function to see what this means.

## Harvard architecture

Unlike well known systems, this architecture has the memory space separated
from the code space: the first is called **SRAM**, the second **Program**.

For this reason there are separated instructions to load and to store
data in these spaces, ``lds/sts`` and ``lpm/spm`` respectively.

Another particularity is that by the memory space can be accessed some
peripherics

## Arithmetic

It's important to understand how mathematics works with registers:
the first thing to learn is that (in all the architecture) the arithmetic
is module the number of bits; the other thing is that negative numbers
are implemented via **two's complement**. I have a [post]({% post_url 2018-10-28-processor-arithmetics %})
dedicated to that.

### Flags

As the registers have a fixed size, arithmetic operations can overflow, for example
think of the result of the sum of two register containing each the value ``0xff``,
the result, ``0x1fe``, cannot fit into the destination register. For this reason
exists a special register named **sreg** containing a bit (called **flag**)
indicating when a overflow happened.

It's not the only flag dedicated in this register, the list is

| C | there is an overflow |
| Z | Zero flag |
| N | Negative flag |
| V | two's complement overflow |
| S | \\(N\oplus V\\) |
| H | half carry |
| T | transfer bit |
| I | global interrupt flag |

## Calling convention

The processor doesn't have a notion of argument of its own, when you call
a routine in your program the caller have to define a convention with the callee
in order to communicate. Usually is set by the compiler (I'm not completely sure).

Using ``avr-gcc`` we have the following indications ([source](https://gcc.gnu.org/wiki/avr-gcc#Calling_Convention)):

 - An argument is passed either completely in registers or completely in memory.
 - To find the register where a function argument is passed, initialize the register number Rn with R26 and follow this procedure:

    1. If the argument size is an odd number of bytes, round up the size to the next even number.
    2. Subtract the rounded size from the register number Rn.

    3. If the new Rn is at least R8 and the size of the object is non-zero, then the low-byte of the argument is passed in Rn. Subsequent bytes of the argument are passed in the subsequent registers, i.e. in increasing register numbers.

    4. If the new register number Rn is smaller than R8 or the size of the argument is zero, the argument will be passed in memory.

    5. If the current argument is passed in memory, stop the procedure: All subsequent arguments will also be passed in memory.
    6. If there are arguments left, goto 1. and proceed with the next argument.
 - Return values with a size of 1 byte up to and including a size of 8 bytes will be returned in registers. Return values whose size is outside that range will be returned in memory.
 - If a return value cannot be returned in registers, the caller will allocate stack space and pass the address as implicit first pointer argument to the callee. The callee will put the return value into the space provided by the caller.
 - If the return value of a function is returned in registers, the same registers are used as if the value was the first parameter of a non-varargs function. For example, an 8-bit value is returned in R24 and an 32-bit value is returned R22...R25.
 - Arguments of varargs functions are passed on the stack. This applies even to the named arguments.

## Instruction sets

Here a summary of the instrutions available on this architecture,
with a little description of the operations that they implement.
To have more informations read the [summary](http://www.avr-tutorials.com/sites/default/files/Instruction%20Set%20Summary.pdf)
or the [complete reference](http://ww1.microchip.com/downloads/en/devicedoc/atmel-0856-avr-instruction-set-manual.pdf).

### Arithmetic

| add ra, rb | adds two register and stores the result in the first one |
| adc ra, rb | adds two register using also the carry flag and stores the result in the first one |
| adiw ra, K | adds immediate to word |
| inc ra | increments a register of one |
| sub ra, rb | subtracts two registers and stores the result in the first one |
| sbc ra, rb | subtracts two registers using also the carry flag and stores the result in the first one |
| sbiw ra, K | subtracts immediate from word |
| dec ra | decrements a register |
| com ra | takes the one's complement of a register |
| neg ra | takes the two's complement |
| eor ra, rb | calculates the exclusive or of two register and stores the result in the first one |


### Load and store

| ldi ra, K | loads immediate in register |
| lds ra, K | loads register with value stored in address |
| ld ra, x | loads register with value stored in address contained in x |
| ld ra, x+ | |
| ld ra, -x | |
| ldd ra, x+q | loads register with value stored in address pointed by x + q |

### Branch

In AVR exists only two opcodes for branching, ``brbs <bit flag> <relative jump>`` and ``brbc <bit flag> relative jump>``
that for easy of use have a few aliases

| Test  | Boolean  | Mnemonic  | Complementary  | Boolean  | Mnemonic  | Comment  |
| :---  | :------  | :-------  | :------------  | :------  | :-------  | :------  |
| Rd > Rr  | Z & (N ^ V) = 0  | BRLT  | Rd <= Rr  | Z+(N ^ V) = 1  | BRGE  | Signed  |
| Rd >= Rr  | (N ^ V) = 0  | BRGE  | Rd < Rr  | (N ^ V) = 1  | BRLT  | Signed  |
| Rd = Rr  | Z=1  | BREQ  | Rd != Rr  | Z=0  | BRNE  | Signed  |
| Rd <= Rr  | Z+(N ^ V) = 1  | BRGE  | Rd > Rr  | Z & (N ^ V) = 0  | BRLT  | Signed  |
| Rd < Rr  | (N ^ V) = 1  | BRLT  | Rd >= Rr  | (N ^ V) = 0  | BRGE  | Signed  |
| Rd > Rr  | C+Z=0  | BRLO  | Rd <= Rr  | C+Z=1  | BRSH  | Unsigned  |
| Rd >= Rr  | C=0  | BRSH/BRCC  | Rd < Rr  | C=1  | BRLO/BRCS  | Unsigned  |
| Rd = Rr  | Z=1  | BREQ  | Rd != Rr  | Z=0  | BRNE  | Unsigned  |
| Rd <= Rr  | C+Z=1  | BRSH  | Rd > Rr  | C+Z=0  | BRLO  | Unsigned  |
| Rd < Rr  | C=1  | BRLO/BRCS  | Rd >= Rr  | C=0  | BRSH/BRCC  | Unsigned  |
| Carry  | C=1  | BRCS  | No carry  | C=0  | BRCC  | Simple  |
| Negative  | N=1  | BRMI  | Positive  | N=0  | BRPL  | Simple  |
| Overflow  | V=1  | BRVS  | No overflow  | V=0  | BRVC  | Simple  |
| Zero  | Z=1  | BREQ  | Not zero  | Z=0  | BRNE  | Simple  |

| sbrs Rr | Skip if Bit in Register is Set |
| sbrc Rr | Skip if Bit in Register is Cleared |

## Examples

Below take a look to some examples of common routines implemented
with this language


### Prologue

This is the start of a function, where it sets its frame pointer and allocate
the space into the stack for local variables; generally looks like the following

```
push r28
push r29
in r28, 0x3d
in r29, 0x3e
subi r28, 0x10
sbci r29, r1
```

In this case the code saves the frame pointer of the caller and sets the frame pointer
to the actual position of the stack pointer. The moves downs the frame pointer of 16 bytes
to create space for the local variables. I think is backward with respect to the normal
use of stack and frame pointers in the x86 code.

To access local variables you simply can use the load/store with displacement instruction with the
``y`` register (that is the frame pointer)

```
ldd r24, y+1
ldd r25: y+2
eor r24, r25
ld r25, r1
std y+1, r24
std y+2, r25
```

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
r25:r24 &= r31:r30 + \left(r25:r24 \oplus {\tt 0xffff}\right)\cr
        &= r31:r30 - 1 + \left(r25:r24\oplus {\tt 0xffff} +1\right)\cr
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
it's not zero then ``r27:r26`` are equal to ``0xffff``. Seems sign extension to me.

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

