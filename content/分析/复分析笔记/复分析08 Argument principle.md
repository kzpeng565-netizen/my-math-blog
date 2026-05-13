---
tags:
  - 复分析
  - 分析
---
**重点** Rouche 定理. 

# 1. Argument Principle

## 1.1 Logarithm of Holomorphic Functions
$z=\rho e^{i\theta},\theta=\text{argument of }z_{0}$
$z=e^{r+i\theta}$ with $r=\log \rho\in \mathbb{R}$. We want for a holomorphic function f, can we write $f(z)=e^{g(z)}$ with g holomorphic. If this is true, $\mathrm{Re}(g(z))=\log \lvert f(z) \rvert$
$\mathrm{Im}(g(z))$ argument of $f(z)$

We consider log as a primitive $z\to \frac{1}{z}$. More generally, we want to define $\log f$ as a primitive.
We note that $\frac{d}{dz}(\log f(z))= \frac{f'(z)}{f(z)}$ formally. In this section, we will consider $\int_{\gamma} \frac{f'(z)}{f(z)}dz$, $\gamma$ is a closed curve.

If $f:\Omega \to \mathbb{C}$ is holomorphic $D\subset \bar{D}\subset\Omega$, $D$ is a disc.
If $f(z)\neq0, \forall z\in \bar{D}$, then $\frac{f'}{f}$ is holomorphic in a neighborhood of $\bar{D}$.
By previous theorems, it has a primitive $g(z)$. Then $e^{g(z)}=f(z)$.
Moreover $\int_{\gamma} \frac{f'(z)}{f(z)}dz=0$ for any closed curve $\gamma \subset D$.

## 1.2 Special Case: Function with Zeros
Now we assume f has zero in D.

Special case: $f(z_{0})=0$
$$
f(z)=(z-z_{0})^{n}\cdot G(z)
$$
where $G(z)\neq0$ for all $z\in \bar{D}$. Then we can write
$$
\frac{f'(z)}{f(z)} = \frac{n}{z-z_{0}}+ \frac{G'(z)}{G(z)}
$$
Then, $\int_{C} \frac{f'(z)}{f(z)}dz=\int_{C} \frac{n}{z-z_{0}}dz+\int_{C} \frac{G'(z)}{G(z)}dz$ where $C=\partial D$
$$
\int_{C} \frac{f'(z)}{f(z)}dz=2\pi in+0=2n\pi i
$$

**We remark that**, if $n<0$ is a negative integer, the calculation is still valid.

In this previous example, $\frac{1}{2\pi i}\int \frac{f'(z)}{f(z)}dz$ computes the order of f at $z_{0}$. If we know that $f(z)\neq0$ and $f(z)\neq \infty$ for all $z\in \bar{D}-\{z_{0}\}$

## 1.3 Argument Principle Theorem

> [!Note]  Argument Principle
>Let f be a meromorphic function on $\Omega$. Let D be a disc with $\bar{D}\subset\Omega$. Assume that $f(z)\neq \{0,\infty\}$ for any $z\in \partial \bar{D}=C$. Then,
>1. exists $z_{1},\dots,z_{n}\in D$ s.t. the pole and the zeros of f are $z_{1},\dots,z_{n}$
>2. $\frac{1}{2\pi i}\int_{C} \frac{f'(z)}{f(z)}=(\text{the numbers of zeros of f})-(\text{numbers of pole of f})$.
>Here, every zero or pole is counted with multiplicity for the number in 2.

### 1.3.1 Explanation

Intuitively, we write $\int_{C} \frac{f'(z)}{f(z)}=\int_{f(C)} \frac{1}{w}dw$ 
If the zero is of k multipicity, then $f(C)$ is winding around zero for k times. And we can add all of zeros and poles.
### 1.3.2 Proof of Argument Principle
We know that the zeros and poles of f do not accumulate inside $\Omega$.
Since $\bar{D}$ is compact, any infinite subset of $\bar{D}$ has an accumulation point in $\bar{D}\subset\Omega$. For this reason, we conclude there are finite many zeros and poles in $\bar{D}$. 


For 2, we consider keyhole contours $C_\delta,\varepsilon$ which have holes at $z_{1},\dots,z_{n}$
*First, we close the circle, let $\delta \to0$*

Since $\frac{f'}{f}$ is holomorphic in a neighborhood of the shaded region *(it's the region of interior of keyhole contour)*, and the region is simply connected, we obtain
$$
\int_{C_{\delta,\varepsilon}} \frac{f'}{f}=0
$$

We let $\delta \to0$. We get $\int_{C} \frac{f'}{f}=\sum_{i=1}^{n}\int_{\delta_{i,\varepsilon}} \frac{f'}{f}$ where $\gamma$ is the circle centered at $z_{i}$ with radius $\varepsilon$
For $\varepsilon$, very small, f has exactly one zero or pole in the disc centered at$z_{i}$ with radius $2\varepsilon$
By previous calculation, we get for $\varepsilon>0$ very small,
$$
\int_{\gamma_{i,\varepsilon}} \frac{f'}{f}= 2\pi i \cdot(\text{order of f at }z_{1})
$$
This completes the proof of the theorem.

**Corollary** The same conclusion holds, if we replace $C$ by any other toy contours, for example, keyhole contours, rectangles, polygons.

# 2. Rouche's Theorem

^e4a105

> [!Note]  Rouche's Theorem
>Let $\Omega$ be an open subset of $\mathbb{C}$, Let $D$ be a disc with $\bar{D}\subset\Omega$ we write $C=\partial D$
>Let f, g be holomorphic functions on $\Omega$. Assume that $\lvert f(z) \rvert>\lvert g(z) \rvert$ for all $z\in C$
>Then f and $f+g$ have the same number of zeros in D.

$\left| f(z) \right|>\left| g(z) \right|$ holds for $z\in C$ not the entire $\bar{D}$ 
## 2.1 Proof of Rouche's Theorem
For any $t\in[0,1]$, we set $F(t,z)=f(z)+t\cdot g(z)$ for any $z\in\Omega$
Then, $F(0,z)=f(z),F(1,z)=f(z)+g(z)$. We let $n_{t}$ be the number of zeros of $F(t,z)$ in $D$. We will prove that $n_{t}$ is a continuous function on t. If this holds, then $n_{t}$ must be constant since $n_{t}$ is always an integer.
*skill: to prove a function is continuous, we try to write it as an integral*

We note that $F(t,z)\neq0$ for any $t\in[0,1]$ and $z\in C$, since $\lvert f(z) \rvert>\lvert g(z) \rvert\geq t\lvert g(z) \rvert$. Hence, by the argument theorem, we have
$$
n_{t}= \frac{1}{2\pi i}\int_{C} \frac{\frac{\partial}{\partial z} F(t,z)}{F(t,z)}dz
$$

If $G(t,z)= \frac{\frac{\partial}{\partial z}F(t,z)}{F(t,z)}$ for any $z\in C$ and $t\in[0,1]$
Then G is continuous on the compact set $[0,1]\times C$,
It follows that $n_{t}$ is continuous in t. This completes the proof of Rouche's Theorem.

## 2.2 appllication of Rouche's Theorem

If we can ​	seperate ​	$h=f+g$ in $S$ , a simply connected open subset. $\lvert f \rvert>\lvert g \rvert$, which means the modulo of f is dominating, then the zero number of h is exactly the number of f.

> [!Note] Prove fundamental theorem with Rouche's Theorem

$f(z)=\sum_{i=0}^{n}a_{i}z^{i}$ is a polynomial. We know $z^{n}$ has n roots. Then we can make $R$ is large enough such that $\lvert z^{n} \rvert>\left\lvert  \sum_{i=0}^{n}a_{i}z^{i}  \right\rvert$
# 3. Open Mapping Theorem (考试不会考到, 但很重要)

**Definition** Let $f:X\to Y$ be a map between topological spaces. f is called an open map if for any open subset $U\subset X,\: f(U)$ is an open subset of Y.
**Remark**: f is open if and only if the following holds:
For any $x\in X$, let $y=f(x)\in Y$. Then there is open neighborhood $x\in U\subset X,y\in V\subset Y$ such that $V\subset f(U)$
**Open mapping theorem is not correct in real number** Consider $f(x)=x^{2},x\in(-1,1)$. 

> [!Note]  Open Mapping Theorem
>Let $f:\Omega \to \mathbb{C}$ be a holomorphic function. Then f is an open map.

## 3.1 Proof of Open Mapping Theorem
We will use the criterion of the remark.
Let $z_{0}\in\Omega$, let $w_{0}=f(z_{0})$. We need to prove the image under f of $\Omega$ contains a disc centered at $w_{0}$
Let $\delta>0$ such that $\bar{D}_{\delta}(z_{0})\subset\Omega$. Since $z\to f(z)-w_{0}$ is holomorphic, its zeros do not have accumulation points. Thus, by choosing $\delta$ small, we can assume that $f(z)\neq w_{0}$ for $z\in C_{\delta}(z_{0})=\partial D_{\delta}(z_{0})$
Since $z\to f(z)-w_{0}$ is continuous and since it is never zero on the compact set $C_{\delta}(z_{0})$
Thus, $\exists\varepsilon>0$ such that $\lvert f(z)-w_{0} \rvert>\varepsilon$ for all $z\in C_{\delta}$
Next, we will show that $D_{\varepsilon}(w_{0})\subset f(\Omega)$
Let $w\in D_{\varepsilon}(w_{0})$. We consider $h(z)=f(z)-w$. We have
$h(z)=f(z)-w=f(z)-w_{0}+w_{0}-w=(f(z)-w_{0})+g(z)$ where $g(z)=w_{0}-w$ is constant.
We note that $\lvert g(z) \rvert=\lvert w-w_{0} \rvert<\varepsilon$ and for any $z\in C_{\delta}(z_{0})$
$$
\lvert f(z)-w_{0} \rvert >\varepsilon>\lvert g(z) \rvert
$$
Thus by Rouche's theorem, $h(z)$ has the same number of zeros as $f(z)-w_{0}$ inside D
Thus $h(z)$ has a zero say $z_{1}\in D$ Then $f(z_{1})=w$. This completes the proof.

# 4. Maximum Principle

> [!Note]  Maximum Principle
>Let $f:\Omega \to \mathbb{C}$ be a non-constant holomorphic function ($\Omega$ is an open connected set)
>Then $\lvert f \rvert$ cannot attain a local maximum inside $\Omega$

## 4.1 Proof of Maximum Principle
Assume by contradiction that $f$ has a local maximum at $z_{0}\in\Omega$
Since $f$ is not constant, it is an open map.
Thus $\exists$ disc D centered at $f(z_{0})$ such that $D\subset f(\Omega)$
However, exists $w\in D$ such that $\lvert w \rvert>\lvert f(z_{0}) \rvert$ This is a contradiction.

**Corollary**: assume that $\bar{\Omega}$ is compact. Then
$$
\sup_{z\in\Omega }\lvert f(z) \rvert \leq \sup_{z\in \bar{\Omega}-\Omega}\lvert f(z) \rvert
$$
