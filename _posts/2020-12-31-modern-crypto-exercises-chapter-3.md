---
layout: post
comments: true
title: "Modern cryptography: exercises chapter 3 'Private-key encryption'"
tags: [cryptography, exercises, WIP]
---

These are some solved exercises of chapter 3 of the book ["Introduction to
modern cryptography"](http://www.cs.umd.edu/~jkatz/imc.html) (second edition) by Jonathan Katz and Yehuda Lindell.
For chapter 2 go [here]({% post_url 2018-02-06-modern-crypto-exercise-chapter2 %}).

I'm not sure are correct but if anyone find any error let me know. It's a work in progress
and more exercises will follow in future, when I finally find time to solve more.

\\(\def\negl#1{\hbox{negl}_{#1}}\\)

\\(\def\PrivK#1#2{\hbox{PrivK}^\hbox{#1}_{#2}}\\)

\\(\def\Pr#1{\hbox{Pr}\left[#1\right]}\\)

Let's start with some notes about this chapter: here the book starts the serious business and introduces
the idea of **realistic expectation of security**; in the previous chapter talked about
**perfect secrecy**, here instead it's introducing a **security parameter** \\(n\\) linked to
the length of the key of the encryption scheme.

This is important since the minimal requirement is that the key space is big enough to be not
brute-forced in polynomial time.

Since we can relax the security for practical cases the book is going to talk about **asymptotic security**
i.e. encryption schemes that "behave" well for \\(n\\) "large enough". Linking a scheme with the security
parameter allows to modulate its security also for situation in which technological improvements
helps the attackers.

**Efficient algorithms:** an algorithm \\(A\\) is efficient if runs in **polynomial time** i.e. there exists
a polynomial \\(p\\) such that for every input \\(x\in \\{0, 1\\}^\star\\), the computation of \\(A(x)\\) terminates
in \\(p(\|x\|)\\) steps.

**Negligible function:** is \\(f:N\to N^+\\) if for every positive polynomial \\(p\\)
there is a natural number \\(N\\) such that for every \\(n \gt N\\), \\(f(n) \lt{1\over p(n)}\\)

The idea here is that the function is negligible if is going to zero for large enough \\(n\\) faster
than any negative power of \\(n\\) (to me this seems a simpler way to define something approaching zero than the neglibile functions).

**A scheme is secure** if for every PPT adversary \\(A\\) carrying out an attack
of some formally specified type, and for every positive polynomial \\(p\\),
there exists an integer \\(N\\) such that when \\(n \gt N\\) the probability
of \\(A\\) succeeding in the attack is less than \\({1\over p(n)}\\).

**Pseudorandom generator:** \\(G\\) is a deterministic polynomial-time algorithm such that for any \\(n\\)
and any input \\(s\in\\{0, 1\\}^n\\), the result \\(G(s)\\) is a string of length \\(l(n)\\), where \\(l\\)
is a polynomial. Also the following conditions hold true

 - \\(\forall n,\,l(n) > n\\).
 - For any PPT algorithm \\(D\\), there is a negligible function \\(\negl{}\\) such that

$$
\bigl\|\Pr{D(G(s)) = 1} - \Pr{D(r)= 1}\bigr\| \leq\negl{}(n)
$$

where the first probability is taken over  uniform choice of \\(s\in\\{0,1\\}^n\\) and the randomness of \\(D\\),
and the second probability is taken over uniform choice of \\(r\in\\{0, 1\\}^{l(n)}\\) and the randomness of \\(D\\).

\\(s\\) is called **seed**, \\(l\\) is called **expansion factor** of \\(G\\).

## **3.1**

Prove proposition \\(3.6\\)

### Solution

From the definitions:

$$
\eqalign{
    \negl{3}(n) &= \negl{1}(n) + \negl{2}(n)\cr
&\lt{1\over p_1(n)} + {1\over p_2(n)} \cr
&\lt{2\over p_i(n)} \cr
}
$$

$$
\eqalign{
    \negl{b}(n) &= r(n)\cdot\negl{a}(n) \cr
    &\lt r(n)\cdot{1\over p(n)} \cr
}
$$

TODO: improve the details

## 3.2

Prove that definition 3.8 cannot be satisfied if \\(\Pi\\) can encrypt arbitrary-length messages
and the adversary is not restricted to output equal length messages in experiment \\(\PrivK{eav}{A, \Pi}\\).

**Hint:** Let \\(q(n)\\) be a polynomial upper-bound on the length of the ciphertext
when \\(\Pi\\) is used to encrypt a single bit. Then consider and adversary who outputs \\(m_0=\\{0, 1\\}\\)
and a uniform \\(m_1\in\\{0, 1\\}^{q(n) + 2}\\).

### Solution

Using the setting of the hint, when the adversary outputs the message \\(m_0\\) it expects for it a ciphertext
with length less or equal than \\(q(n)\\). Since the decryption function (for fixed key) must map plaintext to corresponding
ciphertext and viceversa, if we take all the possible messages up to length \\(q(n)\\) we have the following
as the total possible number of messages

$$
\#\hbox{binary strings up to length}q(n) = \sum_{l = 1}^{q(n)}2^l = 2^{q(n) + 1} - 2
$$

So the idea is that all the messages up to length \\(q(n) + 2?\\) cannot be **all** contained into ciphertext with
at most \\(q(n)\\) digits; if we take a message with length \\(q(n) + 2 + \Delta\\) we have the following result:

$$
\eqalign{
    \Pr{\PrivK{eav}{A, \Pi} = 1} &= \Pr{ A\, \hbox{outputs}\, 0 \,|\, b = 0 }\Pr{b = 0} + \Pr{A\,\hbox{outputs}\,1\,|\, b = 1}\Pr{b = 1} \cr
    &= {1\over2}\left({1\over2} + 1 - {2^{q(n) + 1} - 2\over 2^{q(n) + 2 + \Delta}}\right) \cr
    &= {1\over2}\left({1\over2} + 1 - {2^{q(n) + 1}\over 2^{q(n) + 2 + \Delta}} + {2\over 2^{q(n) + 2 + \Delta}}\right) \cr
    &= {1\over2}\left({1\over2} + 1 - {1\over 2^{\Delta + 1}} + {2\over 2^{q(n) + 2 + \Delta}}\right) \cr
}
$$

TODO: double check the calculation.

## 3.3

Say \\(\Pi= \left(\hbox{Gen}, \hbox{Enc}, \hbox{Dec}\right)\\) is such that for \\(k\in\\{0, 1\\}^n\\), algorithm \\(Enc_k\\)
is only defined for messages of length at most \\(l(n)\\) (for some polynomial \\(l\\)).
Construct a scheme satisfying definition \\(3.8\\) even when the adversary is not restricted to outputting  equal-length messages
in \\(\PrivK{eav}{A, \Pi}\\).

### Solution

This seems against the previous exercise, but the devil is the details: probably the previous result is true, we need just to
avoid  giving away information about the original message's length, in this case we could fix the length of the ciphertext to be \\(l(n) + 2\\)
in order to contain all the possible ciphertexts.

## 3.4

Prove the equivalence of definition \\(3.8\\) and definition \\(3.9\\).

### Solution

\\(\def\outA#1#2{\hbox{out}_A\left(\PrivK{eav}{A, \Pi}(n, #1)\right) = #2}\\)

It's sufficient to explicitly write \\(\PrivK{eav}{A, \Pi}(n)\\) as \\(\hbox{out}_A\\)

$$
\eqalign{
    \Pr{\PrivK{eav}{A, \Pi}(n) = 1} &= {1\over2}\left\{\Pr{\outA{0}{0}} + \Pr{\outA{1}{1}}\right\} \cr
    &= {1\over2}\left\{1 - \Pr{\outA{0}{1}} + \Pr{\outA{1}{1}}\right\} \cr
    &= {1\over2} - {1\over2}\left\{\Pr{\outA{0}{1}} - \Pr{\outA{1}{1}}\right\} \cr
\Pr{\PrivK{eav}{A, \Pi}(n) = 1} - {1\over2} &=  {1\over2}\left\{\Pr{\outA{0}{1}} - \Pr{\outA{1}{1}}\right\} \cr
\left\|\Pr{\PrivK{eav}{A, \Pi}(n) = 1} - {1\over2}\right\| &=  {1\over2}\left\|\Pr{\outA{0}{1}} - \Pr{\outA{1}{1}}\right\| \cr
}
$$

## 3.5

Let \\(\|G(s)\| = l(\|s\|)\\) for some \\(l\\). Consider the following experiment:

\\(\def\PRG#1{\hbox{PRG}_{#1}}\\)

**The PRG indistinguishability experiment** \\(\PRG{A, G}(n)\\):

 - (a) A uniform bit \\(b\in\\{0,1\\}\\) is chosen. If \\(b = 0\\) then choose a uniform \\(r\in\\{0,1\\}^{l(n)}\\); if \\(b=1\\)
       then choose a uniform \\(s\in\\{0,1\\}^n\\) and set \\(r:=G(s)\\).
 - (b) The adversary \\(A\\) is given \\(r\\), and outputs a bit \\(b^\prime\\).
 - (c) The output of the experiment is defined to be \\(1\\) if \\(b = b^\prime\\), and \\(0\\) otherwise.

Provide a definition of a pseudorandom generator based on this experiment, and prove that your definition is equivalent
to definition \\(3.14\\). (That is, show that \\(G\\) satisfies your definition if and only if it satisfies definition \\(3.14\\).)

### Solution

We can define a pseudorandom generator to be a deterministic polynomial-time algorithm such that the following condition holds

$$
\|\Pr{\PRG{A, G}(n) = 1}\bigr\| \leq {1\over2} + \negl{}(n)
$$

and following the same procedure of the previous exercise we can find that is equivalent to definition \\(3.14\\). TODO

## 3.6

Let \\(G\\) be a pseudorandom generator with expansion factor \\(l(n) > 2n\\). In each of the following cases, say whether \\(G^\prime\\)
is necessarily a pseudorandom generator. If yes, give a proof; if not, show a counterexample.

 - (a) Define \\(G^\prime (s){\buildrel\rm def\over=} G(s_1\dots s_{\lfloor n/2\rfloor})\\)
 - (b) Define \\(G^\prime (s){\buildrel\rm def\over=} G(0^{\|s\|}\Vert s)\\)
 - (c) Define \\(G^\prime (s){\buildrel\rm def\over=} G(s)\Vert G(s + 1)\\)

### Solution

Let's first of all calculate the expansion factor:

 - (a) \\(l^\prime(n) = l^\prime(\|s\|) = l(\lfloor\|s\|/2\rfloor) > 2\lfloor\|s\|/2\rfloor = \|s\| = n\\)
 - (b) \\(l^\prime(n) = l^\prime(\|s\|) = l(2\|s\|) > 4\|s\| = 4n\\)
 - (c) \\(l^\prime(n) = l^\prime(\|s\|) = l(\|s\|) + l(\|s\|) = 2 l(\|s\|) > 4\|s\| = 4n\\)

and seems fine in all cases.

In general these cases seem PRGs since the dependency on the length of \\(s\\) remains exponential but we must be careful!

In case (a) we have a seed of length let me say \\(m\\), of which we discard half (ending) bits to obtain a seed that
"fits" into the original PRG: since the original seed is extracted from a random sample, its bits are random distributed
and so are the first half that are used as seed; there is the possibility the two seed starting with the same pattern
can generate the same pseudo random string via \\(G\\) but the probability is negligible (like \\(2^{-m/2}\\)).

For case (b) seems the same but there is also the intuition that something is off: if we had a PRG that takes only half
of its seed to generate its value we would have a counterexample, but which PRG would do that.... wait a minute! if we
use for \\(G\\) the \\(G^\prime\\) defined for case (a) we have such counterexample :) This generator will output always
the same string making it distinct from a random string.

For case (c) we can take a PRG like the case (a) but with the higher-bits: if we interpret the seed as a binary digit
with addition modulo \\(\|s\|\\) in that case only when the "discarded" bits are all set the \\(s + 1\\) part generates
a different input seed TODO the proof.

## 3.7

Prove the converse of theorem \\(3.18\\). Namely, show that if \\(G\\) is not a pseudorandom generator then construction \\(3.17\\)
does not have indistinguishable encryption in the presence of an eavesdropper.

### Solution

It seems obvious from the final step of the proof itself TODO
