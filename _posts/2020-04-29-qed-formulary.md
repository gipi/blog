---
layout: post
comments: true
title: "QED formulary"
tags: [physics,mathematics]
---

\\(\def\Tr{\hbox{Tr}}\\)
\\(\def\slashme#1{\rlap{\backslash}{#1}}\\)
\\(\def\pslash{\rlap{\backslash}{p}}\\)
\\(\def\partialslash{\rlap{\backslash}{\partial}}\\)

This post is personal: I found some notes taken more than 10 years ago
and I'm worried to lost them, so I write it down here in order to preserve
the memory; maybe one day I'll write a post about the physics behind this stuff.
<div>
$$
\int d^Nq\,\left(q^2 + \mu^2 -i\epsilon\right)^{-\alpha} = i{\pi^{N/2}\over 2}{\Gamma(N/2)\Gamma(\alpha - N/2)\over\Gamma(\alpha)}\left(\mu^2\right)^{N/2 - \alpha}
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
\int d^4k\,\theta(k_0)\delta(k^2 + m^2) \sim \int{d^3k\over2 k_0}
$$

## Tensorial integrals

For some informations see this [slides](http://hanka.hluchy.sk/pdf/Svit-lecture.pdf).
<div>
$$
\eqalign{
J_0 &= \int d^Nq\,{1\over\left(q^2 + 2kq+\mu^2\right)^\alpha} = i\pi^{N/2}{\Gamma(\alpha - N/2)\over\Gamma(\alpha)}\left(\mu^2 - k^2\right)^{N/2 - \alpha} \cr
J_\mu(k) &= \int d^Nq\,{q_\mu\over\left(q^2 + 2kq+\mu^2\right)^\alpha} = -J_0 k_\mu\cr
J_{\mu\nu}(k) &= \int d^Nq{q_\mu q_\nu\over\left(q^2 + 2kq+\mu^2\right)^\alpha} = -J_0\left(k_\mu k_\nu + {1\over2}{\mu^2 - k^2\over\alpha - 1 - N/2}\delta_{\mu\nu}\right)\cr
}
$$
</div>

## Gamma matrices

Suppose \\(D\\) is the dimensionality of the space-time

<div>
$$
\eqalign{
\Tr(\mathbf{I}_{n}) &= 4\cr
\left\{\gamma^\mu,\gamma^\nu\right\} &= 2g^{\mu\nu}\mathbf{I}_{n} \cr
\gamma^\mu\gamma_\mu &= g^\mu_\mu = D \cr
Tr(\gamma^\mu\gamma^\nu) &= 4g^{\mu\nu} \cr
Tr(\gamma^\mu\gamma^\nu\gamma^\rho\gamma^\sigma) &= 4\left(g^{\mu\nu}g^{\rho\sigma} - g^{\mu\rho}g^{\nu\sigma}  + g^{\mu\sigma}g^{\nu\rho}\right) \cr
Tr(\gamma^\mu\gamma^\nu\gamma^\sigma\gamma^\rho\gamma^\xi) &= \epsilon^{\mu\nu\sigma}\quad\hbox{(TO FIX)}\cr
}
$$
</div>

## Spinors

<div>
$$
\eqalign{
\pslash &= \gamma^\mu p_\mu \cr
\left(i\pslash + m\right)u(\vec{p}) &= 0 \cr
\left(-i\pslash + m\right)v(\vec{p}) &= 0 \cr
\sum_{\hbox{spin}}u(p)\bar{u}(p) = {1\over2 p_0}\left(-i\pslash + m\right) \cr
\sum_{\hbox{spin}}v(p)\bar{v}(p) = {1\over2 p_0}\left(i\pslash + m\right) \cr
}
$$
</div>

## Lagrangian

$$
L = -{1\over4} F_{\mu\nu}F_{\mu\nu} - {1\over2}\left(\partial_\mu A_\mu\right)^2 - \bar\psi\left(\partialslash + m \right)\psi + ie A_\mu\bar\psi\gamma^\mu\psi
$$

## 1loop photon

$$
\eqalign{
\Pi_{\mu\nu} &= e^2\int d^nq{1\over \left(q^2 + m^2\right)\left(\left(q+p\right)^2 + m^2\right)}\Tr\left\{\gamma^\mu\left(-i\slashme{q} + m\right)\gamma^\nu\left(-i\left(\slashme{p} + \slashme{q}\right) + m\right)\right\} \cr
&= -i8\pi^2e^2 \int^1_0dx\,J_0\left(p^2\delta_{\mu\nu} - p_\mu p_\nu\right) x(1 - x)\cr
&\sim -i8\pi^2e^2 \int_0^1 dx\,\left(\Delta - \ln \mu^2\right) x\left(1 - x\right)\left(p^2 \delta_\mu\nu - p_\mu p_\nu\right) \cr
}
$$

## QED renormalization

From an analysis using the propagators of photons and fermions and the vertex we can tell that the
global degree of divergence of a diagram is given by

$$
D(G) = 4 - {3\over2}E_e - E_\gamma\quad\left\{\eqalign{
    &D(G) < 0\quad\hbox{converges} \cr
    &D(G) \ge0\quad\hbox{diverges} \cr
}\right.
$$

### Weinberg theorem

Given a \\(G\\) such that \\(D(G) < 0\\) and for all its subdiagrams
then \\(G\\) converges.
