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

\\(\def\l#1#2{l_{\rm #1}({#2})}\\)

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

The book introduces some fundamental concepts:

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

Another important concept is **pseudorandom function**: a function 

$$
F\colon\{0,1\}^{\l{key}n}\times\{0,1\}^{\l{in}n}\to\{0,1\}^{\l{out}n}
$$

has such property if for all polynomial-time distinguisher \\(D\\), there is a
negligible function \\(\negl{}\\) such that

$$
\left\|\Pr{D^{F_k(\cdot)}(1^n) = 1} - \Pr{D^{f(\cdot)}(1^n) = 1}\right\|\leq\negl{}(n)
$$

where the first probability is taken over uniform choice of \\(k\in\\{0,1\\}^n\\) and the randomness of \\(D\\), and the second probability
is taken over uniform choice of \\(f\in\hbox{Func}_n\\) and the randomness of \\(D\\).


\\(F\\) is called a **keyed function**: \\(F(k,x) = F_k(x)\\); obviously there
are \\(2^{\l{key}n}\\) of them, instead in the general case of all
possible functions we have \\(2^{\l{out}n\cdot2^{\l{in}n}}\\).

The pseudo is chosen from a distribution over at most \\(2^n\\) distinct
functions, whereas the real random function is chosen from  all \\(2^{n\cdot2^n}\\) functions in \\(\hbox{Func}_n\\).

At this point is introduced the concept of **CPA-security**: i.e. the idea that
an encryption scheme is secure also in the case the attacker
has the "power" to obtain ciphertext from plaintext of her choice.

The simplest example of attack possible in case of **not** \\(CPA\\)-secure
schemes is the **replay attack**; the necessity of \\(CPA\\)-secure scheme is
for **randomness** to be added to a scheme! We need the encryption to be
    non-deterministic with respect to only \\(m\\).

**Note** that randomness in this case comes from the pseudorandom generator, the
pseudorandom function are used as encryption primitive.

Another useful concept is the security for **multiple encryptions**: the case
when, with the same key, more than one message is exchanged.

The main idea for the \\(CPA\\)-indistinguishability experiment is that the
attacker has access to an **encryption oracle**, i.e. a function that encrypts
messages of her choice.

**Theorem:** Any private-key encryption scheme that is \\(CPA\\)-secure is also
\\(CPA\\)-secure for multiple encryptions.

Reusing the one time pad we can define the following encryption scheme that is
\\(CPA\\)-secure:

Let \\(F\\) be a pseudorandom function. Define a private-key encryption scheme
for messages of length \\(n\\) and key \\(k\in\\{0,1\\}^n\\) as follow:

 - \\(\rm Gen\\): on input \\(1^n\\), choose uniform key and output it
 - \\(\rm Enc\\): on input a key and a message
   \\(m\in\\{0,1\\}^n\\), choose uniform \\(r\in\\{0,1\\}^n\\) and output the
   ciphertext \\(c := \langle r, F_k(r)\oplus m\rangle\\).
 - \\(\rm Dec\\): on input a key and a ciphertext \\(c = \langle r, s\rangle\\),
   output the plaintext message \\(m :=F_k(r)\oplus s\\).

$$
\Pr{ {\rm PrivK}^{\rm cpa}_{A, \Pi}(n) = 1} \leq {1\over2} + {q(n)\over 2^n} + \negl{}(n)
$$

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

 - (a) Define \\(G^\prime (s){\buildrel\rm def\over=} G(s_1\dots s_{\lceil n/2\rceil})\\)
 - (b) Define \\(G^\prime (s){\buildrel\rm def\over=} G(0^{\|s\|}\Vert s)\\)
 - (c) Define \\(G^\prime (s){\buildrel\rm def\over=} G(s)\Vert G(s + 1)\\)

### Solution

Let's first of all calculate the expansion factor:

 - (a) there are two cases
   - \\(n\\) even: \\(l^\prime(n) = l^\prime(\|s\|) = l(\lceil\|s\|/2\rceil) > 2\lceil\|s\|/2\rceil = 2\lceil 2k/2\rceil = 2\lceil k\rceil = 2k = n\\)
   - \\(n\\) odd: \\(l^\prime(n) = l^\prime(\|s\|) = l(\lceil\|s\|/2\rceil) > 2\lceil\|s\|/2\rceil = 2\lceil {2k + 1\over2}\rceil = 2\lceil k + {1\over 2}\rceil = 2(k + 1) = (2k + 1) + 1 = n + 1\\)
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
the same string making it distinct from a random string. As a further argument
think that we cannot use the pseudorandomness of the original \\(G\\) in the
proof since we should use a random distributed seed, but \\(0^{\|s\|}\Vert s\\)
is not random distributed. 

For case (c) we can take a PRG like the case (a) but with the higher-bits: if we interpret the seed as a binary digit
with addition modulo \\(\|s\|\\) in that case only when the "discarded" bits are all set the \\(s + 1\\) part generates
a different input seed TODO the proof.

## 3.7

Prove the converse of theorem \\(3.18\\). Namely, show that if \\(G\\) is not a pseudorandom generator then construction \\(3.17\\)
does not have indistinguishable encryption in the presence of an eavesdropper.

### Solution

It seems obvious from the final step of the proof itself TODO

## 3.9

Prove unconditionally the existence of a pseudorandom function \\(F:\,\\{0,1\\}^\star\times\\{0,1\\}^\star\to\\{0,1\\}\\)
with \\(\l{key}{n} = n\\) and \\(\l{in}{n} = O(\log n)\\).

**Hint:** Implement a uniform function with logarithmic input length.

### Solution

Expliciting the function form we have \\(F:\,\\{0,1\\}^n\times\\{0,1\\}^{O(\log n)}\to\\{0,1\\}\\); A simple solution is
defining the function as taking an \\(N=2^n\\) bits key and input an \\(n\\) bit
string and returning the bit indicated by the input:

$$
F(k, x) = k[x]
$$

In this case we have the number of pseudorandom functions (i.e. \\(2^n\\)) equal
to the number of possible functions (i.e. \\(2^{1\cdot{2^{\log n}}} = 2^n\\))
and the key acts as a random "index".

## 3.10

Let \\(F\\) be a length preserving pseudorandom function. For the following
constructions of a keyed function
\\(F^\prime\colon\\{0,1\\}^n\times\\{0,1\\}^{n - 1}\to\\{0,1\\}^{2n}\\)
state whether \\(F^\prime\\) is a pseudorandom function If yes, prove it; if not show an attack.

 - (a) \\(F^\prime_k(x) {\buildrel {\rm def}\over=} F_k(0\Vert x)\Vert F_k(1\Vert x)\\)
 - (b) \\(F^\prime_k(x) {\buildrel \hbox{def}\over=} F_k(0\Vert x)\Vert F_k(x\Vert 1)\\)

### Solution

For case (a) it's a pseudorandom function since any attack for it would work also
on the original \\(F\\).

For case (b) we can defeat the randomness simply by evaluating \\(F^\prime\\)
with argument \\(x_A = 1\cdots1\\) and \\(x_B = 01\cdots1\\) so to obtain

$$
\eqalign{
F_k^\prime(x_A) &= F_k(01\cdots1)\Vert F_k(1\cdots11) \cr
F_k^\prime(x_B) &= F_k(001\cdots1)\Vert F_k(01\cdots11) \cr
}
$$

This allows to distinguish this function from one chosen at random since the
first half of \\(F^\prime_k(x_A)\\) is equal to the second half of
\\(F^\prime_k(x_B)\\).

## 3.20

Consider a stateful variant of \\(CBC\\)-mode encryption where the sender simply
increments the \\(IV\\) by 1 each time a message is encrypted (rather than
choosing \\(IV\\) at random each time). Show that the resulting scheme is not
\\(CPA\\)-secure.

### Solution

This seems a more constrained case of \\(CBC\\)-chained mode (that the textbook
gives an attack): in practice we can provide a message as \\(m = (IV + 1)\oplus\\)
