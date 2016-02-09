---
layout: post
comments: true
title: "volume and surface area of a sphere n-dimensional"
---

I'm starting first calculating the surface area of the \\(N\\)-dimensional sphere, in order
to do that I'll use a well known integral
$$
\int^\infty_0 dt\,e^{-t^2} = \sqrt{\pi}
$$

Taking the \\(N\\)-power of this integral, which value is \\(\pi^{N/2}\\), we can
rewrite this as follows

$$
\eqalign{
\left[\int^\infty_0 dx\,e^{-x^2}\right]^N &= \int^\infty_0 dx_1\dots\int_0^\infty dx_N\,e^{-\left(x^2_1 + \dots + x^2_N\right)} \cr
                                          &= \int d\Omega_{N-1}\int^\infty_0 dr\, e^{-r^2}r^{N - 1} \cr
                                          &= {1\over2}\int d\Omega_{N-1}\int^\infty_0 du\,e^{-u}u^{N/2 - 1} \cr
                                          &= {1\over2}\Gamma\left(N\over2\right)\int d\Omega_{N-1}\cr
}
$$

So that we have

$$
S_N = {\pi^{N/2}\over {1\over2}\Gamma\left(N\over2\right)} r^{N - 1}
$$

Now we can calculate easily the volume:
$$
\eqalign{
V_N &= S_N\,\int^\infty_0 dr\, r^{N-1}\cr
    &= S_N\,{r^N\over N} \cr
    &= {\pi^{N\over2}\over\left(N\over2\right)\Gamma\left(N\over2\right)} r^N\cr
    &= {\pi^{N\over2}\over\Gamma\left({N\over2} + 1\right)} r^N\cr
}
$$

It's interesting at this point observe the ratio

$$
\eqalign{
R   &= {V_N\over S_N} \cr
    &= {r\over N}
}
$$
