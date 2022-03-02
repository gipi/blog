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

The lowest level is the **finite automata**

The next step is the **pushdown automata**

The work of turing instead is the _highest_ level that pushes the limit of what
is computable.

## LangSec
