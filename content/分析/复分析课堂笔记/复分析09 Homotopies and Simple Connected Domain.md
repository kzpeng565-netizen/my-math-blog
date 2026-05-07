---
tags:
  - 复分析
  - 分析
---
# 1. Homotopies and Simply Connected Domains

## 1.1 Homotopic Curves

**Definition**: Let $\gamma_0, \gamma_1$ be two curves in $\mathbb{C}$. More precisely, $\gamma_0, \gamma_1: [a,b] \to \mathbb{C}$ are continuous maps. Assume that $\gamma_0(a) = \gamma_1(a)$ and $\gamma_0(b) = \gamma_1(b)$. We say that $\gamma_0$ and $\gamma_1$ are **homotopic** (homotopy equivalent) in $\Omega$ if there is a continuous map $H: [0,1] \times [0,1] \to \Omega$ such that:
1. $H(0,t) = \gamma_0(t)$
2. $H(1,t) = \gamma_1(t)$
3. $H(s,a) = \gamma_0(a)$, $H(s,b) = \gamma_0(b)$

In other words, we can move $\gamma_0$ to $\gamma_1$ inside $\Omega$ continuously while keeping the endpoints invariant.

## 1.2 Integral of Holomorphic Functions on Homotopic Curves

>[! Theorem]
> Assume $\gamma_0, \gamma_1$ are piecewise $C^1$. Let $f: \Omega \to \mathbb{C}$ be holomorphic. If $\gamma_0, \gamma_1$ are homotopic, then $\int_{\gamma_0} f = \int_{\gamma_1} f$.

### 1.2.1 Proof of the Theorem

The proof relies on **Goursat's theorem**. We can approximate $H$ by piecewise functions.

![[Pasted image 20251105134344.png|400]]

There exists $\varepsilon$ such that $|C_1(t) - C_2(t)| < \varepsilon$ for all $t \in [a,b]$. Then, we can divide $[a,b]$ into $t_1, \dots, t_n$ and we join $C_1(t_i)$ and $C_2(t_i)$ with a line. $S_i$ is a curve, which is shown in the figure. $S_i$ is contained in a disk $D_i$ with $\overline{D_i} \subset \Omega$. Then by summing $\sum_{i=0}^{n-1} \int_{S_i} f$, we have $\int_{C_1} f = \int_{C_2} f$.

## 1.3 Simply Connected Domains

**Definition**: $\Omega$ is called **simply connected** if it is path-connected, and every closed curve is homotopic to the constant curve. In other words, every closed curve $\gamma_1: [a,b] \to \Omega$ is homotopic to $\gamma_0: [a,b] \to \Omega$ with $\gamma_0(t) \equiv \gamma_0(a)$.

**Property**: If $\Omega$ is simply connected and $f$ is holomorphic on $\Omega$, then $\int_{\gamma} f = 0$ for every closed curve $\gamma$ in $\Omega$.

**Example**: Let $f: D_2(0) \setminus \{0\} \to \mathbb{C}$, $z \mapsto 1/z$. Then $f$ is holomorphic. The integral around the circle of radius 1 centered at 0 is $2\pi i$, which is not zero. Therefore, $D_2(0) \setminus \{0\}$ is not simply connected.

## 1.4 Existence of Primitives on Simply Connected Domains

>[! Theorem]
> If $\Omega$ is simply connected and $f$ is holomorphic on $\Omega$, then $f$ has a primitive on $\Omega$.

### 1.4.1 Proof of the Theorem

Fix $z_0 \in \Omega$. For $z \in \Omega$, let $\gamma_1$ be a curve from $z_0$ to $z$. Define $F(z) = \int_{\gamma_1} f$. If $\gamma_2$ is another curve from $z_0$ to $z$, then $\gamma_1 + (-\gamma_2)$ is a closed curve. By the property above, $\int_{\gamma_1} f - \int_{\gamma_2} f = 0$, so $F$ is independent of the choice of $\gamma$. By a similar argument, we can prove that $F'(z) = f(z)$.