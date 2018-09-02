---
layout: post
comments: true
title: "Digital Signal Processing"
tags: [notes, DSP, WIP]
---

I just completed the course [Digital Signal Processing](https://www.coursera.org/learn/dsp) on Coursera
and these are my re-elaborated notes; it will follow a different path with respect to the
course.

## Introduction

We want to formalize the theoretical and practical discipline of communication: we'll start defining
our characters as **message**, **channel**.

## Bits

First we want to define a way to _measure_ how much information a piece of something contains

## Capacity

The **capacity** is the maximum data rate at which a given channel is capable of. It's in relation
with the bandwidth: a channel with bandwidth \\(B\\) can change at a maximum rate of \\(2B\\).

If we suppose that the signal can change without limitation we have the data rate equal to

$$
R = 2B\log_2\left(n\right)\,\hbox{bits/seconds}
$$

But in reality it's not possible to have how many levels as we like since, at fixed bandwidth, we need
to decrease the interval width approaching the magnitude of the noise present in the channel.

If we know the **signal to noise ratio** (indicated with ``SNR``) we have a measure of the intervals.
Usually is expressed in decibel with the formula

$$
SNR = 10\log_{10}\left(S\over N\right)\,\hbox{dB}
$$

## Links

 - [Foundations of Signal Processing](http://www.fourierandwavelets.org/FSP_v1.1_2014.pdf) free e-book
 - [D/A and A/D | Digital Show and Tell](https://www.youtube.com/watch?v=cIQ9IXSUzuM)
