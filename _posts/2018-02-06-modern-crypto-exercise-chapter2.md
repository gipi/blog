---
layout: post
comments: true
title: "Modern cryptography: exercises chapter 2"
tags: [cryptography, exercises, WIP]
---

These are some solved exercises of chapter 2 of the book ["Introduction to
modern cryptography"](http://www.cs.umd.edu/~jkatz/imc.html) by Jonathan Katz and Yehuda Lindell.

I'm not sure are correct but if anyone find any error let me know. It's a work in progress
and more exercises will follow in future, when I finally find time to solve more. Also,
enjoy my hand made diagrams :).

## Definitions

An encryption scheme \\((\hbox{Gen}, \hbox{Enc}, \hbox{Dec})\\) with message space \\(M\\)
is **perfectly secret** if for every probability distribution over \\(M\\), every message
\\(m\in M\\), and every ciphertext \\(c\in C\\) for which \\(\hbox{Pr}\left[C = c\right] > 0\\):

$$
\hbox{Pr}\left[M = m\,|\, C = c\right] = \hbox{Pr}\left[M = m\right]
$$

This is equivalent to **a prior indistinguishibility**:

$$
\hbox{Pr}\left[\hbox{Enc}_K(m) = c\right] = \hbox{Pr}\left[\hbox{Enc}_K(m^\prime) = c\right]
$$

i.e. the ciphertext's probability distribution is independent from the message's probability distribution.

For notation purpose take in mind this way of writing:

$$
\hbox{Pr}\left[C = c\,|\,M = m\right] = \hbox{Pr}\left[\hbox{Enc}_K(M) = c\,|\, M = m\right] = \hbox{Pr}\left[\hbox{Enc}_K(m) = c\right]
$$

## Exercises

**2.1:** Prove that, by redefining the key space, we may assume that the key generation
algorithm \\(Gen\\) choose a key uniformly at random from the key space, without changing
\\(\hbox{Pr}\left[C = c \| M = m\right]\\) for any \\(m, c\\).

### solution

The encryption scheme can be described using the following diagram:

![]({{ site.baseurl }}/public/images/redefining-key-space-as-random.png)

where the \\(\hbox{Gen}\\) algorithm creates a key using a random tape \\(r\\) from the
space \\(R\\). Redefining
\\(\hbox{Enc}\\) to include \\(\hbox{Gen}\\) and using \\(r\\) as new key we have
that

$$
\eqalign{
\hbox{Pr}\left[K=k\right] &= \hbox{Pr}\left[\hbox{Gen}(R)=k\right] \cr
  &= \sum_r\hbox{Pr}\left[\hbox{Gen}(R)=k\,|\,R = r\right]\hbox{Pr}\left[R = r\right]
}
$$

This means that we simply shift the key to be the random tape that provides
random values to the Turing machine implementing the probabilistic algorithm \\(\hbox{Gen}\\).

we can verify

$$
\eqalign{
\hbox{Pr}\left[ C = c \,|\, M = m\right] &= \hbox{Pr}\left[\hbox{Enc}_K(m) = c\right] \cr
  &= \sum_k\hbox{Pr}\left[\hbox{Enc}_K(m) \,|\, K = k \right]\cdot\hbox{Pr}\left[K = k\right] \cr
  &= \sum_k\hbox{Pr}\left[\hbox{Enc}_K(m) \,|\, K = k \right]\cdot\sum_r\hbox{Pr}\left[\hbox{Gen}(R) = k\,|\,R = r\right]\cdot\hbox{Pr}\left[R = r\right] \cr
  &= \sum_{k, r}\hbox{Pr}\left[\hbox{Enc}_K(m) \,|\, K = k \right]\cdot\hbox{Pr}\left[\hbox{Gen}(R) = k\,|\,R = r\right]\cdot\hbox{Pr}\left[R = r\right] \cr
  &= \sum_{k, r}\hbox{Pr}\left[\hbox{Enc}_K(m) \,|\, K = k \right]\cdot\hbox{Pr}\left[K = k\,|\,R = r\right]\cdot\hbox{Pr}\left[R = r\right] \cr
  &= \sum_r\hbox{Pr}\left[\hbox{Enc}^\prime_R(m) \,|\, R = r \right]\cdot\hbox{Pr}\left[R = r\right] \cr
  &= \hbox{Pr}\left[\hbox{Enc}^\prime_R(m) = m \right] \cr
  &= \hbox{Pr}^\prime\left[ C = c \,|\, M = m\right] \cr
}
$$

<hr/>

**2.2:** Prove that, by redefining the key space, we may assume that \\(Enc\\) is
deterministic without changing 
\\(\hbox{Pr}\left[C = c \,|\, M = m\right]\\) for any \\(m, c\\).


### solution

\\(\hbox{Enc}\\) can become deterministic using the random tape as a component of the key;

![]({{ site.baseurl }}/public/images/redefining-key-space-with-enc-deterministic.png)

$$
\eqalign{
\hbox{Pr}^\prime\left[C = c\,|\, M = m \right] &= \hbox{Pr}\left[\hbox{Enc}^\prime_k(m = c)\right] \cr
  &= \sum_{k^\prime}\hbox{Pr}\left[\hbox{Enc}_{k^\prime}(m) = c \,|\, K^\prime = k^\prime\right]\cdot\hbox{Pr}\left[K^\prime = k^\prime\right] \cr
  &= \sum_{k,\,r}\hbox{Pr}\left[\hbox{Enc}_{k,\,r}(m) = c \,|\, K = k,\,R = r\right]\cdot\hbox{Pr}\left[K = k\right]\cdot\hbox{Pr}\left[R = r\right] \cr
  &= \sum_k\left(\sum_r\hbox{Pr}\left[\hbox{Enc}_{k,\,r}(m) = c \,|\, K = k,\,R = r\right]\cdot\hbox{Pr}\left[R = r\right]\right)\cdot\hbox{Pr}\left[K = k\right] \cr
  &= \sum_k\hbox{Pr}\left[\hbox{Enc}_{k}(m) = c \,|\, K = k\right]\cdot\hbox{Pr}\left[K = k\right] \tag{verificare}\cr
  &= \hbox{Pr}\left[\hbox{Enc}_{k}(m) = c\right] \cr
  &= \hbox{Pr}\left[C = c\,|\, M = m \right] \cr
}
$$

Expanding the relation \\(k^\prime=(k, r)\\) we obtain

$$
\eqalign{
\hbox{Pr}\left[K^\prime = k^\prime\right] &= \hbox{Pr}\left[K=k,\, R = r\right] \cr
  &= \hbox{Pr}\left[K = k\right]\cdot\hbox{Pr}\left[R = r\right] \cr
}
$$

<hr/>

**2.3:** Prove or refute: an encryption scheme with message space \\(M\\) is perfectly
secret if and only if (\\(\iff\\)) for every probability distribution over \\(M\\) and every \\(c_0,\,c_1\in C\\)
we have \\(\hbox{Pr}\left[C = c_0\right] = \hbox{Pr}\left[C = c_1\right]\\).

### solution

For this one I have not yet a solution but I think has to do with the dimension of the
cipher and message space: the ``iff`` holds if we take the conditions from the Shannon's theorem,
i.e. if the all the spaces have the same dimensions.

<hr/>

**2.4:** Prove the second direction of Lemma 2.4

### solution

We must proof that perfect secrecy implies perfect indistinguishibility; this can be
done using the Bayes' theorem

$$
\hbox{Pr}\left[M = m \,|\, C = c\right] = {\hbox{Pr}\left[C = c \,|\, M = m\right]\cdot\hbox{Pr}\left[M = m\right]\over\hbox{Pr}\left[C = c\right]}
$$

together with perfect secrecy 

$$
\hbox{Pr}\left[M = m \,|\, C = c\right] = \hbox{Pr}\left[M = m\right]
$$

to obtain

$$
\eqalign{
{\hbox{Pr}\left[C = c \,|\, M = m\right]\cdot\hbox{Pr}\left[M = m\right]\over\hbox{Pr}\left[C = c\right]} &= \hbox{Pr}\left[M = m\right] \cr
{\hbox{Pr}\left[C = c \,|\, M = m\right]\over\hbox{Pr}\left[C = c\right]} &= 1 \cr
}
$$

<hr/>

**2.5:** Prove Lemma 2.6.

### solution

We need to proof that

$$
\hbox{Pr}\left[\hbox{PrivK}_{A,\Pi}^{\hbox{eav}} = 1\right] = {1\over 2}\iff \hbox{Perfectly secret}
$$

\\(\Rightarrow\\)) If we have one half as probability of success in the experiment,
then this means that the ciphertext is indipendent from the message, stated with maths

$$
\hbox{Pr}\left[\hbox{Priv}\right] = \hbox{Pr}\left[M = m_b \,|\, C = c\right] = {1\over2}
$$

\\(\Leftarrow\\))

$$
\eqalign{
\hbox{Pr}\left[\hbox{Priv} = 1\right] &= \hbox{Pr}\left[\hbox{Priv} = 1\,|\,b = 0\right]\cdot\hbox{Pr}\left[b = 0\right] + \hbox{Pr}\left[\hbox{Priv} = 1 \,|\, b = 1\right]\cdot\hbox{Pr}\left[b = 1\right] \cr
  &= {1\over2}\left\{\hbox{Pr}\left[\hbox{A outputs 0}\,|\,b = 0\right] + \hbox{Pr}\left[\hbox{A output 1}\,|\,b = 1\right]\right\} \cr
  &= {1\over2}\left\{\hbox{Pr}\left[M = m_0\,|\,C = c, b = 0\right] + \hbox{Pr}\left[M = m_1\,|\,C = c, b = 1\right]\right\} \cr
  &= {1\over2}\left\{\hbox{Pr}\left[M = m_0\,|\,C = c, b = 0\right] + \hbox{Pr}\left[M = m_1\,|\,C = c, b = 1\right]\right\} \cr
  &= {1\over2}\left\{\hbox{Pr}\left[M = m_0\right] + \hbox{Pr}\left[M = m_1\right]\right\} \cr
  &= {1\over2}
}
$$

<hr />

**2.6:** For each of the following encryption schemes, state wheter the scheme is perfectly secret. Justify your answer in each case.

 - (a) The message space is \\(M = \left\\{0,\dots, 4\right\\}\\). Algorithm \\(\hbox{Gen}\\) chooses a uniform key from the key space \\(\\{0,\dots, 5\\}\\).
    \\(\hbox{Enc}_k(m)\\) returns \\(\left[k + m \mod 5 \right]\\), and \\(\hbox{Dec}_k(c)\\) returns \\(\left[c - k \mod 5\right]\\).
 - (b) The message space is \\(M=\\{m\in\\{0,1\\}^l\,|\,\hbox{the last bit of m is 0}\\}\\). \\(\hbox{Gen}\\) chooses an uniform key from \\(\\{0,1\\}^l\\).
    \\(\hbox{Enc}_k(m)\\) returns ciphertext \\(m\oplus\left(k\|0\right)\\), and \\(\hbox{Dec}_k(c)\\) returns \\(c\oplus\left(k\|0\right)\\).

### solution

For the (a) part I can start saying that because of the particular that the value \\(0\\) and \\(5\\) under the module operation
give the same result, when we use these keys the ciphertext is equal to the original message we can have perfect secrecy
