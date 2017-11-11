---
layout: post
comments: true
title: "Modern cryptography: exercises chapter 2"
tags: [cryptography, exercises]
---

**2.1:** Prove that, by redefining the key space, we may assume that the key generation
algorithm \\(Gen\\) choose a key uniformly at random from the key space, without changing
\\(\hbox{Pr}\left[C = c \| M = m\right]\\) for any \\(m, c\\).

### solution

The encryption scheme can be described using the following diagram:

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

**2.3:** Prove or refute: an encryption scheme with message space \\(M\\) is perfectly
secret if and only if for every probability distribution over \\(M\\) and every \\(c_0,\,c_1\in C\\)
we have \\(\hbox{Pr}\left[C = c_0\right] = \hbox{Pr}\left[C = c_1\right]\\).
