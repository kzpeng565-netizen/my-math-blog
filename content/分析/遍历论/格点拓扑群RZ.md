---
aliases:
  - 格点拓扑群R/Z
---







# 1. 商空间、度量与拓扑

在 $\mathbb R$ 上定义 $r\sim s\iff r-s\in\mathbb Z$，所得商空间记为

$$
\mathbb T=\mathbb R/\mathbb Z,
$$
自然商映射为 $q(r)=r+\mathbb Z$。集合 $U\subseteq\mathbb T$ 是开集，当且仅当 $q^{-1}(U)$ 在 $\mathbb R$ 中开。每个等价类在 $[0,1)$ 中有唯一代表元；几何上即把区间两端粘合成圆。

在 $\mathbb T$ 上定义圆周距离

$$
d(r+\mathbb Z,s+\mathbb Z)=\min_{m\in\mathbb Z}|r-s+m|.
$$
更换代表元只会平移整数 $m$，故 $d$ 良定义；三角不等式则来自实数情形。

> [!Note] 结论
> 度量 $d$ 诱导的拓扑 $\tau_d$ 与商拓扑 $\tau_q$ 相同。

**证明思路**：由 $d(q(r),q(s))\le |r-s|$，$q$ 连续，故 $\tau_d\subseteq\tau_q$。反之，$q^{-1}(U)$ 的开性保证每个 $q(r)\in U$ 都含有某个度量开球，故 $\tau_q\subseteq\tau_d$。

# 2. 紧阿贝尔拓扑群

在 $\mathbb T$ 上定义

$$
(r+\mathbb Z)+(s+\mathbb Z)=(r+s)+\mathbb Z.
$$
该运算良定义，并使 $\mathbb T$ 成为阿贝尔群。圆周距离满足

$$
d(x+y,x'+y')\le d(x,x')+d(y,y'),\qquad d(-x,-y)=d(x,y),
$$
因此加法与取负连续，$\mathbb T$ 是拓扑群。

又因 $q|_{[0,1]}$ 是连续满射，而 $[0,1]$ 紧，故 $\mathbb T$ 紧。

> [!Note] 结论
> $\mathbb T=\mathbb R/\mathbb Z$ 是紧阿贝尔拓扑群。

# 3. 拓扑群的局部性质

固定 $a\in G$，左平移 $L_a(x)=ax$ 的逆为 $L_{a^{-1}}$，故左右平移都是同胚。于是各点附近具有相同的局部结构，局部问题可平移到单位元处研究。

若群同态 $\varphi:G\to H$ 在 $e_G$ 处连续，则它处处连续：当 $x$ 接近 $x_0$ 时，$x_0^{-1}x$ 接近 $e_G$，且

$$
\varphi(x)=\varphi(x_0)\varphi(x_0^{-1}x).
$$

# 4. 与单位圆的同构

定义

$$
\Phi:\mathbb T\to S^1,\qquad \Phi(t+\mathbb Z)=e^{2\pi it}.
$$
它良定义且为群同态。又因 $\Phi$ 是连续双射、$\mathbb T$ 紧且 $S^1$ 为 Hausdorff 空间，所以 $\Phi$ 是同胚。

> [!Note] 最终结论
> $\mathbb R/\mathbb Z\cong S^1$，并且这是拓扑群同构。
