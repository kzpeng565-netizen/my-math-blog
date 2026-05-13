---
tags:
  - 复分析
  - 分析
---
辐角原理: $\frac{1}{2\pi i}\int_{C} \frac{f'(z)}{f(z)}dz=$ 零点个数-极点个数. 如果没有零点没有极点, 那么$\frac{f'(z)}{f(z)}$有原函数, 设为$g(z)+C$. 我们计算得$\frac{d}{dz}[f(z)e^{-g(z)-C}]=0$, 因此我们可以选择$C$使得$f(z)=e^{g(z)}$, 其中$C$是多值的.
一般地, 我们这么定义$\log f(z):= \int_{z_{0}\to z} \frac{f'(z)}{f(z)}dz$, 即使有零点或者非单连通, 也可以局部得定义全纯函数.
为什么要单连通: 假如$z=0$有一个单零点, 那么我们在$\mathbb{C}-\{0\}$ (这个区域没有零点) 定义的$\log f(z)$, 会导致从$1$逆时针绕一圈变为$1+2\pi i$, 不连续.

# 1. Complex Logarithm

## 1.1 Theorem (Existence of Complex Logarithm) 
> [!Note] Theorem
>Let $f:\Omega \to \mathbb{C}$ be a holomorphic function, $\Omega$ simply connected and $f(z)\neq 0$ for all $z\in\Omega$. Then there exists $g:\Omega \to \mathbb{C}$ such that $f=e^{g}$.

### 1.1.1 Proof
Let $h(z)= \frac{f'(z)}{f(z)}$, which is holomorphic on $\Omega$ since $f(z)\neq 0$. **Since $\Omega$ is simply connected, $h$ has a primitive $H$.** *If we can ensure the primitive existing, then simply-connected condition isn't needed*

Compute $e^{H(z_{0})}$ for some $z_{0}\in\Omega$. There exists a constant $c\in \mathbb{C}$ such that $f(z_{0})=e^{H(z_{0})+c}$. Define $g(z)=H(z)+c$.

To show $f(z)=e^{g(z)}$ for all $z\in\Omega$, compute:
$$
\frac{d}{dz}\left(  \frac{f(z)}{e^{g(z)}} \right)= \frac{d}{dz}(f(z)e^{-g(z)})=f'(z)e^{-g(z)}-f(z)e^{-g(z)}\cdot g'(z)
$$
Since $g'(z)=H'(z)=h(z)=\frac{f'(z)}{f(z)}$, we have:
$$
f'(z)e^{-g(z)}-f(z)e^{-g(z)} \cdot \frac{f'(z)}{f(z)}=0
$$
Since $\Omega$ is connected, $\frac{f(z)}{e^{g(z)}}$ is constant. Since $\frac{f(z_{0})}{e^{g(z_{0})}}=1$, we conclude $f=e^{g}$.

# 2. Harmonic Functions

## 2.1 Mean Value Equality
Let $f:\Omega \to \mathbb{C}$ be holomorphic with $D_{R}(z_{0})\subset\Omega$. Then $f(z)=\sum_{n=0}^{+\infty}a_{n}(z-z_{0})^{n}$ with convergence radius at least $R$, where:
$$
a_{n}= \frac{f^{(n)}(z_{0})}{n!}= \frac{1}{2\pi i}\int_{C_{R}} \frac{f(\xi)}{(\xi-z_{0})^{n+1}}d\xi
$$
Using polar coordinates $\xi=z_{0}+re^{i\theta}$:
$$
a_{n}=\frac{1}{2\pi}\int_{0}^{2\pi} \frac{f(z_{0}+re^{i\theta})}{r^{n}e^{in\theta}}  d\theta
$$
In particular:
$$
a_{0}=\frac{1}{2\pi}\int_{0}^{2\pi} f(z_{0}+re^{i\theta})  d\theta
$$
Since $f(z_{0})=a_{0}$, we obtain the **mean value equality**:
$$
f(z_{0})= \frac{1}{2\pi}\int_{0}^{2\pi} f(z_{0}+re^{i\theta})  d\theta
$$

## 2.2 Corollary (Harmonicity of Real Part)
**Corollary**: Let $u=\mathrm{Re}(f)$. Taking real parts in the mean value equality:
$$
u(z_{0})= \frac{1}{2\pi}\int_{0}^{2\pi} u(z_{0}+re^{i\theta})  d\theta
$$
This means $u$ is a **harmonic function**.

## 2.3 Theorem (Harmonic Functions and Holomorphic Functions)
> [!Note] Theorem
>Let $\Omega$ be a **simply connected subset** of $\mathbb{C}$. A function $u:\Omega\to \mathbb{R}$ is harmonic (i.e., $u\in C^{2}$ and $\Delta u=0$) if and only if there exists a holomorphic function $f:\Omega \to \mathbb{C}$ such that $u=\mathrm{Re}(f)$.

### 2.3.1 Proof
Let $g(z)=u_{x}-u_{y}i$. Then $g:\Omega \to \mathbb{C}$ is $C^{1}$. Check Cauchy-Riemann equations:
- $\frac{\partial u_{x}}{\partial x}=\frac{\partial (-u_{y})}{\partial y}$ becomes $u_{xx}=-u_{yy}$, which holds since $\Delta u=0$
- $\frac{\partial u_{x}}{\partial y}=-\frac{\partial (-u_{y})}{\partial x}$ becomes $u_{xy}=u_{yx}$, which holds

Thus $g$ is holomorphic. **Since $\Omega$ is simply connected, $g$ has a primitive $h$ with $h'=g$.**
==这里要求单连通的原因: 在单连通集上全纯函数有原函数== 

Write $h=\mathrm{Re}(h)+i\mathrm{Im}(h)$. Then:
- $\frac{\partial \mathrm{Re}(h)}{\partial x}=\mathrm{Re}(g)=u_{x}$
- $\frac{\partial \mathrm{Re}(h)}{\partial y}=-\mathrm{Im}(g)=u_{y}$

Thus $\frac{\partial }{\partial x}(\mathrm{Re}(h)-u)=\frac{\partial }{\partial y}(\mathrm{Re}(h)-u)=0$, so $\mathrm{Re}(h)-u$ is constant $c\in \mathbb{R}$.

Let $f=h-c$, then $u=\mathrm{Re}(f)$.
