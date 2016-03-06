---
layout: post
comments: true
title: "QED formulary"
tags: [physics,mathematics]
---

This post is personal: I found some notes taken more than 10 years ago
and I'm worried to lost them, so I write it down here in order to preserve
the memory; maybe one day I'll write a post about the physics behind this stuff.
<div>
$$
\int d^Nq_M\,\left(q^2 + \mu^2 -i\epsilon\right)^{-\alpha} = i{\pi^{N/2}\over 2}{\Gamma(N/2)\Gamma(\alpha - N/2)\over\Gamma(\alpha)}\left(\mu^2\right)^{N/2 - \alpha}
$$
</div>

<div>
$$
{1\over\Pi^N_{i=1}a_i} =
\Gamma(N)\int^1_0 dx_1\,
\int_0^{x_1} dx_2
\dots\int^{x_{N - 2} }_0
dx_{N - 1}
\left[a_N x_{N - 1} + \dots + \Bigl(x_{N - 2} - x_{N - 1}\Bigr)a_{N - 1} + \dots + \left(1 - x_1\right)a_1\right]^{-N}
$$
</div>

$$
\Gamma(\epsilon) = {1\over\epsilon} - \gamma + O(\epsilon)
$$

$$
a^\epsilon = 1 + \epsilon\ln a + o(\epsilon)
$$

$$
\int d^4k \theta(k_0)\delta(k^2 + m^2) \sim \int{d^3k\over2 k_0}
$$

## Tensorial integrals

For some informations see this [slides](http://www.hephy.at/fileadmin/user_upload/Vortraege/Svit-lecture.pdf).
<div>
$$
\eqalign{
J_0 &= \int d^Nq{1\over\left(q^2 + 2kq+\mu^2\right)^\alpha} = i\pi^{N/2}{\Gamma(\alpha - N/2)\over\Gamma(\alpha)}\left(\mu^2 - k^2\right)^{N/2 - \alpha} \cr
J_\mu(k) &= \int d^Nq{q_\mu\over\left(q^2 + 2kq+\mu^2\right)^\alpha} = -J_0 k_\mu\cr
J_{\mu\nu}(k) &= \int d^Nq{q_\mu q_\nu\over\left(q^2 + 2kq+\mu^2\right)^\alpha} = -J_0\left(k_\mu k_\nu + {1\over2}{\mu^2 - k^2\over\alpha - 1 - N/2}\delta_{\mu\nu}\right)\cr
}
$$
</div>

## Gamma matrices

Suppose \\(D\\) is the dimensionality of the space-time

<div>
$$
\eqalign{
Tr(\mathbf{I}_{n}) &= 4\cr
\left\{\gamma^\mu,\gamma^\nu\right\} &= 2g^{\mu\nu}\mathbf{I}_{n} \cr
\gamma^\mu\gamma_\mu &= g^\mu_\mu = D \cr
Tr(\gamma^\mu\gamma^\nu) &= 4g^{\mu\nu} \cr
Tr(\gamma^\mu\gamma^\nu\gamma^\rho\gamma^\sigma) &= 4\left(g^{\mu\nu}g^{\rho\sigma} - g^{\mu\rho}g^{\nu\sigma}  + g^{\mu\sigma}g^{\nu\rho}\right) \cr
Tr(\gamma^\mu\gamma^\nu\gamma^\sigma\gamma^\rho\gamma^\xi) &= \epsilon^{\mu\nu\sigma}\quad\hbox{(TO FIX)}\cr
}
$$
</div>

## Spinors

\\(\def\pslash{\rlap{\backslash}{p}}\\)

<div>
$$
\eqalign{
\pslash &= \gamma^\mu p_\mu \cr
\left(i\pslash + m\right)u(\vec{p}) &= 0 \cr
\left(-i\pslash + m\right)v(\vec{p}) &= 0 \cr
}
$$
</div>
