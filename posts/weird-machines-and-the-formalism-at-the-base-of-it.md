<!--
.. title: weird machines and the formalism at the base of it
.. slug: weird-machines-and-the-formalism-at-the-base-of-it
.. date: 2022-03-01 15:43:59 UTC
.. tags: vulnerability, exploit, mathematics, security, LangSec, computational models
.. status: draft
.. category: 
.. link: 
.. description: 
.. type: text
.. has_math: true
-->

In this post I'll try to explain the basis of the mathematical formalism used
to explain **exploitation**: the **weird machines**.


<!-- TEASER_END -->

This is the opposite of the post about [pratical approach of exploitation](``link://slug/pratical-approach-exploitation``) where is
explained the practical implementation of a computational model in a modern
computer. However take in mind that this formalism applies not only to
vulnerabilities derived from binary running on operating system but in all
computer related environment like ``XSS``, ``SQLi``; this will be more clear at
the end of the post.

To explain the theory we need to take a journey on the world of the computational models.

## Computational models

I think is pretty well known what's a **Turing machine** is (at least the name)
but not a lot of people are aware of its inner meaning.

The Turing machine is not the only computational model available, probably there
are infinite ones that have different **computational power**.

The lowest level is the **finite automata** defined as a 5-tuple \\(\left(Q,
\Sigma, \delta, q_0, F\right)\\) where

 - \\(Q\\) is a finite set called **states**
 - \\(\Sigma\\) is a finite set called **alphabet**
 - \\(\delta\colon Q\times\Sigma\rightarrow Q\\) is the **transition function**
 - \\(q_0\in Q\\) is the **start state**
 - \\(F\subseteq Q\\) is the set of **accept states**

A **language** is a set of strings over a finite set \\(\Sigma\\), with \\(\|\Sigma\|\geq2\\),
called and alphabet.

**Chomsky hierarchy**

| Language type | Machine type |
|---------------|--------------|
| phase-structure | Turing machine |
| context-sensitive | linear bounded automata |
| context-free | nondeterministic pushdown automata |
| regular | finite-state machine |

For the regular and deterministic context-free grammars, the _equivalence
problem_ (do two grammars produce exactly the same language?) is
**decidable**[^Halt].

[^Halt]: The halting problem of network stack security.

The regular languages are equivalent as descriptive power to the finite automata
(see [this site](https://ivanzuzak.info/noam/webapps/fsm_simulator/) to
visualize the FSM corresponding to a given regular expression).

The next step is the **pushdown automata** (PA): to understand why we need something
more powerful take a look for example at the language

$$
B = \left\\{0^n 1^n \,\|\, n \geq 0\right\\}
$$

this is impossible to recognize via a finite automata because the parameter
\\(n\\) is not fixed so we should have an **infinite** automata to do the job
(if \\(n\\) was fixed, or at least bounded a finite description would be
possible). With the PA is possible to recognize such language because in this
computational model we have access a some sort of **memory**, a stack.

A PA is a 6-tuple \\(\left(Q, \Sigma, \Gamma, \delta, q_0, F\right)\\) where

 - \\(Q\\) is a finite set called **states**
 - \\(\Sigma\\) is a finite set called **input alphabet**
 - \\(\Gamma\\) is a finite set called **stack alphabet**
 - \\(\delta\colon Q\times\Sigma_\epsilon\times\Gamma_\epsilon\rightarrow 2^{Q\times\Gamma_epsilon}\\) is the **transition function**
 - \\(q_0\in Q\\) is the **start state**
 - \\(F\subseteq Q\\) is the set of **accept states**

The work of turing instead is the _highest_ level that pushes the limit of what
is computable.

## LangSec

## Linkography

 - [What are Weird Machines?](https://www.cs.dartmouth.edu/~sergey/wm/)
 - [Exploitation and state machines](https://downloads.immunityinc.com/infiltrate-archives/Fundamentals_of_exploitation_revisited.pdf)
