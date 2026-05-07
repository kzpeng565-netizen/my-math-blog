---
tags:
  - 复分析
  - 分析
---
# 1. Schwarz Lemma

## 1.1 Schwarz Lemma
>[!Schwarz Lemma]
>Let $f:\mathbb{D}\to \mathbb{D}$ be a holomorphic function such that $f(0)=0$. Then:
>1. $\lvert f(z) \rvert\leq \lvert z \rvert,\: \forall z\in \mathbb{D}$
>2. If $\exists z_{0}\in \mathbb{D}$ with $\lvert f(z_{0}) \rvert=\lvert z_{0} \rvert$, then $f$ is a rotation
>3. $\lvert f'(0) \rvert\leq1$, and $\lvert f'(0) \rvert=1$ if and only if $f$ is a rotation

### 1.1.1 Proof Outline

[[构造初等辅助函数]] 我们证明$\left| f(z) \right|\leq \left| z \right|$比较困难, 想到证明$\left| \frac{f(z)}{z} \right|\leq1$, 联想到最大模原理, 然后发现还是太宽, 于是我们可以取极限.
$f(0)=0$, so that $\frac{f(z)}{z}$ is well defined and is holomorphic.
$g(z)= \frac{f(z)}{z}$ , $\left| g(z) \right|\leq\frac{1}{z}\leq1$ 
rotation iff $\left| g(z) \right|=1$
### 1.1.1 Proof
Since $f$ is holomorphic in $\mathbb{D}$ and $f(0)=0$, $f$ has a power series development $f(z)=a_{1}z+a_{2}z^{2}+\dots$ in $\mathbb{D}$ with convergence radius at least 1. Define $g(z)=\frac{f(z)}{z}=a_{1}+a_{2}z+\dots$, which is holomorphic in $\mathbb{D}$.

For $z_{0}\in \mathbb{D}$ with $\lvert z_{0} \rvert=r_{0}<1$, we have $\lvert g(z_{0}) \rvert = \left\lvert   \frac{f(z_{0})}{z_{0}}  \right\rvert\leq \frac{1}{\lvert z_{0} \rvert}= \frac{1}{r_{0}}$. By the maximum principle applied to $g$ in the disc with radius $r_{0}$, we deduce $\lvert g(z) \rvert \leq \frac{1}{r_{0}}$ for $\lvert z \rvert\leq r_{0}$.

Fixing $z\in \mathbb{D}$ and letting $r_{0}\to 1$, we get $\lvert g(z) \rvert\leq1$, proving (1).

For (2): If $\lvert f(z_{0}) \rvert=\lvert z_{0} \rvert$ for $z_{0}\neq0$, then $\lvert g(z_{0}) \rvert=1$. Since $\lvert g(z) \rvert\leq1$ for all $z\in \mathbb{D}$, by maximum principle $g$ is constant: $g(z)=e^{i\theta}$, so $f(z)=e^{i\theta}\cdot z$.

For (3): Since $f'(0)=g(0)$ and $\lvert g(0) \rvert\leq1$, we have $\lvert f'(0) \rvert\leq1$. Equality holds if and only if $g$ is constant, i.e., $f$ is a rotation.




# 2. Automorphisms of the Unit Disk

**Definition**: Let $\Omega \subset \mathbb{C}$ be an open set. An **automorphism** $f$ of $\Omega$ is a bijective holomorphic map $f:\Omega\to\Omega$ with holomorphic inverse.

## 2.1 Automorphisms of $\mathbb{D}$

### 2.1.1 Basic Automorphisms
For $\alpha\in \mathbb{D}$, define $\psi_{\alpha}:\mathbb{D}\to \mathbb{D}$ by $\psi_{\alpha}(z)=\frac{z-\alpha}{1-\bar{\alpha}z}$.

**Properties**:
- $\psi_{\alpha}$ is an automorphism of $\mathbb{D}$
- $\psi_{\alpha}(\alpha)=0$, $\psi_{\alpha}(0)=-\alpha$
- $\psi_{\alpha}\circ \psi_{\alpha}$ is the identity

### 2.1.2 Proof that $\psi_{\alpha}$ is an Automorphism
Since $\lvert \bar{\alpha}z \rvert\leq \lvert \alpha \rvert\cdot1<1$ for $\lvert z \rvert\leq1$, we have $1-\bar{\alpha}z\neq0$, so $\psi_{\alpha}$ is holomorphic in $\mathbb{D}_{1+\varepsilon}(0)$ for some $\varepsilon>0$.

To show $\psi_{\alpha}(\mathbb{D})\subset \mathbb{D}$, by maximum principle the supremum of $\lvert \psi_{\alpha}(z) \rvert$ on $\overline{\mathbb{D}}$ is attained on $\partial\mathbb{D}$. For $z=e^{i\theta}$:
$$\psi_{\alpha}(e^{i\theta})=\frac{\alpha-e^{i\theta}}{1-\bar{\alpha}e^{i\theta}}=\frac{1}{-e^{i\theta}}\cdot \frac{\alpha-e^{i\theta}}{\overline{\alpha-e^{i\theta}}}$$
Thus $\lvert \psi_{\alpha}(e^{i\theta}) \rvert=1$.

Bijectivity follows from $\psi_{\alpha}\circ\psi_{\alpha}(z)=z$.

## 2.2 Classification of Automorphisms of $\mathbb{D}$
>[!Theorem: Automorphisms of the Unit Disk]
>Let $f:\mathbb{D}\to \mathbb{D}$ be an automorphism. Then $\exists\alpha\in \mathbb{D}$, $\theta\in[0,2\pi)$, such that $f(z)= e^{i\theta}\cdot \frac{\alpha-z}{1-\bar{\alpha}z}$

**Key point** $f(\alpha)=0$ $g(z)=f(\psi_{\alpha}(z))$ is an automorphism $0\to0$. 
$\left| g \right|\leq \left| z \right|,\left| g^{-1} \right|\leq \left| z \right|\implies \left| g \right|\equiv1\implies$ g is a rotation
### 2.2.1 Proof
Let $f(\alpha)=0$ for some $\alpha\in \mathbb{D}$. Consider $g(z)=(f\circ \psi_{\alpha})(z)$. Then $g(0)=f(\psi_{\alpha}(0))=f(\alpha)=0$, and $g$ is an automorphism of $\mathbb{D}$.

By Schwarz Lemma: $\lvert g(z) \rvert\leq \lvert z \rvert$. Let $h=g^{-1}$, then for $h(w)=z$ we have $\lvert z \rvert=\lvert h(w) \rvert\leq \lvert w \rvert=\lvert g(z) \rvert$, so $\lvert g(z) \rvert=\lvert z \rvert$. Thus $g$ is a rotation: $g(z)=e^{i\theta}z$.

Since $g=f\circ\psi_{\alpha}$, we have $f=g\circ \psi_{\alpha}=e^{i\theta}\cdot \frac{\alpha-z}{1-\bar{\alpha}z}$.

**Corollary**: If $f:\mathbb{D}\to \mathbb{D}$ is an automorphism with $f(0)=0$, then $f$ is a rotation.

**Remark**: The group of automorphisms of $\mathbb{D}$ acts transitively on $\mathbb{D}$.

# 3. Automorphisms of the Upper Half-Plane

## 3.1 Connection Between $\mathbb{H}$ and $\mathbb{D}$

We have conformal maps:
$$F:\mathbb{H}\to \mathbb{D},\ F(z)=\frac{i-z}{i+z}$$
$$G:\mathbb{D}\to \mathbb{H},\ G(w)=i\cdot \frac{1-w}{1+w}$$
with $F^{-1}=G$ and $F(i)=0$.

Thus $Aut(\mathbb{H})\cong Aut(\mathbb{D})$.

## 3.2 Special Linear Group and Automorphisms

**Definition**: $SL_{2}(\mathbb{R})=\{\begin{pmatrix}a & b \\ c & d\end{pmatrix}\mid a,b,c,d \in\mathbb{R}, ad-bc=1\}$

For $M=\begin{pmatrix}a & b \\ c & d\end{pmatrix}\in SL_{2}(\mathbb{R})$, define $f_{M}(z)=\frac{az+b}{cz+d}$.

>[!Theorem: Automorphisms of the Upper Half-Plane]
>Every automorphism of $\mathbb{H}$ can be written as $f(z)=\frac{az+b}{cz+d}$ for some $\begin{pmatrix}a & b \\ c & d\end{pmatrix}\in SL_{2}(\mathbb{R})$

### 3.2.1 Proof Outline

**Step 1**: Show $f_{M}\in Aut(\mathbb{H})$

For $z\in \mathbb{H}$:
$$\mathrm{Im}(f_{M}(z))= \frac{1}{\lvert cz+d \rvert ^{2}}\mathrm{Im}(adz+bc\bar{z})= \frac{1}{\lvert cz+d \rvert ^{2}}\mathrm{Im}z>0$$

If $M^{-1}$ is the inverse of $M$, then $f_{M}\circ f_{M^{-1}}$ is the identity.

**Step 2**: $f_{M}\circ f_{M'}=f_{M\cdot M'}$

**Step 3**: The action of $SL_{2}(\mathbb{R})$ on $\mathbb{H}$ is transitive

For any $z\in \mathbb{H}$, $\exists M$ such that $f_{M}(z)=i$.

**Step 4**: Study automorphisms fixing $i$

Let $M_{\theta}=\begin{pmatrix}\cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{pmatrix}$. Then $F\circ f_{M_{\theta}}\circ G(w)=e^{-2i\theta}w$, so $f_{M}\in Aut(\mathbb{H})$ corresponds to rotation by angle $2\theta$ in $Aut(\mathbb{D})$.

**Step 5**: Every automorphism has the form $f_{M}$

Given $f\in Aut(\mathbb{H})$ with $f(i)=\beta$, choose $M_{1}$ with $f_{M_{1}}(\beta)=i$. Then $g=f_{M_{1}}\circ f$ fixes $i$, so $g=f_{M_{\theta}}$, hence $f=f_{M_{1}^{-1}}\circ f_{M_{\theta}}=f_{M}$ for $M=M_{1}^{-1}M_{\theta}$.

​
## 3.3 Projective Special Linear Group

The map $SL_{2}(\mathbb{R})\to Aut(\mathbb{H})$ has kernel $\{I,-I\}$.

**Definition**: The quotient group $SL_{2}(\mathbb{R})/\{I,-I\}$ is called the **projective special linear group** and is denoted by $PSL_{2}(\mathbb{R})$.

**Final Result**: $PSL_{2}(\mathbb{R})\cong Aut(\mathbb{H})$