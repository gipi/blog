---
layout: post
comments: true
title: "Notes about theoretical foundation of vulnerabilities"
---

> Insecurity is about computation

> exploitation is unexpected computation

> inputs are a language (as in formal language)

[slide](http://langsec.org/insecurity-theory-28c3.pdf) from the talk **The science of security**,
you can found a lot more from http://langsec.org/.

[Page](http://www.cs.dartmouth.edu/~sergey/wm/) about weird machines by halvar flake, in particular
 this [paper](http://www.cs.dartmouth.edu/~sergey/wm/woot13-shapiro.pdf) where uses the ``RTLD`` as a weird machine,
implementing ``add``, ``mov`` and ``jnz`` using relocation entries.

## Computation model

Bear with me, a little excursus about the formal models of computation.
They define a language hierarchy

### Finite state machine

The simplest computationa model is named **Finite State Machine** (aka ``FSM``); it's usually
represented as a flowgraph having as nodes the different states of a system

A language recognized by this kind of machine is called **regular**; it can be proof
that recognized the same kind of languages of a regular expression (this where the name
come from).

### Pushdown automata

### Turing machine

## Security and vulnerability model

If you are arrived to read up to here, maybe are you asking, what the fuck all
this formalism is connected with a ``rip = 0x4141414141414141``?

The reason to bring up all this formalism is the necessity to summarize
all we know about vulnerabilities  in order to create an unificating theoretical
framework, like in the same way in which modern cryptography works (if you are
a mathematical person I advice you to read *Modern cryptography* by Kahn).
The reality is that this framework exists already, and is that written
above.

But let me explain this in detail.

First of all you have to keep in mind that when you are writing a program,
you are writing an emulator for something like a ``FSM``, not a ``TM``:
you have in mind a diagram with the different states of the program and
the transitions between them; take for example this simple program

```
int main() {

    char* name = ask_name();
    print_name(name);

    return 0;
}
```

that can be represent with the following diagram

![]()

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
