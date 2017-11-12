---
layout: post
comments: true
title: "Modern cryptography: exercises chapter 2"
tags: [cryptography, exercises]
---

## Definitions

An encryption scheme \\((\hbox{Gen}, \hbox{Enc}, \hbox{Dec})\\) with message space \\(M\\)
is **perfectly secret** if for every probability distribution over \\(M\\), every message
\\(m\in M\\), and every ciphertext \\(c\in C\\) for which \\(\hbox{Pr}\left[C = c\right] > 0\\):

$$
\hbox{Pr}\left[M = m\,|\, C= C\right] = \hbox{Pr}\left[M = m\right]
$$

This is equivalent to **a prior indistinguishibility**:

$$
\hbox{Pr}\left[\hbox{Enc}_K(m) = c\right] = \hbox{Pr}\left[\hbox{Enc}_K(m^\prime) = c\right]
$$

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

where the \\(\hbox{Gen}\\) algorithm creates a key using a random tape \\(r\\). Redefining
\\(\hbox{Enc}\\) to include \\(\hbox{Gen}\\) and using \\(r\\) as new key we can verify
that

$$
\eqalign{
\hbox{Pr}^\prime\left[C = c\,|\,M=m \right] &= \hbox{Pr}\left[\hbox{Enc}^\prime_k(m)\right]       \cr
  &= \sum_k\hbox{Pr}\left[\hbox{Enc}_k(m) \,|\, \hbox{Gen}(r) = k \right]\cdot\hbox{Pr}\left[\hbox{Gen}(r) = k\right] \cr
  &= \sum_k\hbox{Pr}\left[\hbox{Enc}_k(m) \,|\, K = k \right]\cdot\hbox{Pr}\left[K = k\right] \cr
  &= \hbox{Pr}\left[\hbox{Enc}_k(m) = c\right] \cr
  &= \hbox{Pr}\left[ C = c \,|\, M = m\right] \cr
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

\\(\Rightarrow\\)) If the encryption scheme is perfectly secret we know from the a prior indistinguishibility

$$
\eqalign{
\hbox{Pr}\left[C = c\right] &= \sum_m\hbox{Pr}\left[C = c\,|\, M = m\right]\cdot\hbox{Pr}\left[M = m\right] \cr
  &= \sum_m \Delta\cdot\hbox{Pr}\left[M = m\right] \cr
  &= \Delta\sum_m \hbox{Pr}\left[M = m\right] \cr
  &= \Delta
}
$$

that doesn't depend on the cyphertext.

\\(\Leftarrow\\)) The hypothesis means that \\(\forall c\in C,\,\hbox{Pr}\left[C = c\right]\\) is equal to a
constant independent from the ciphertext so that for properties of a probability distribution

$$
\sum_c\hbox{Pr}\left[ C = c\right] = 1\, \Rightarrow\, \hbox{Pr}\left[C = c\right] = {1\over|C|}
$$

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
