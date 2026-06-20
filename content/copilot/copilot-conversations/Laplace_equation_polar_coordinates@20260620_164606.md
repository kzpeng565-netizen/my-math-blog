---
epoch: 1781945166797
modelKey: deepseek-reasoner|deepseek
tags:
  - copilot-conversation
topic: Laplace equation polar coordinates
---

**user**: 拉普拉斯方程在极坐标 $(r,\theta)$ 下为 $u_{rr}+\frac{1}{r}u_r+\frac{1}{r^2}u_{\theta\theta}=0$。设 $u(r,\theta)=R(r)\Theta(\theta)$，得 $\Theta''+n^2\Theta=0$ 和径向欧拉方程 $r^2R''+rR'-n^2R=0$。

**2. 求解并舍弃奇性项**

角度解 $e^{in\theta}$（$n$ 整数以保证 $2\pi$ 周期性）。径向方程通解 $R_n(r)=A_n r^{|n|}+B_n r^{-|n|}$。$r=0$ 处需有界，故 $B_n=0$，解展开为：
$$
u(r,\theta)=\sum_{n=-\infty}^{\infty}C_n r^{|n|}e^{in\theta}
$$
**3. 利用边界条件求系数**

边界 $r=1$，$u(1,\theta)=g(\theta)$，得 $g(\theta)=\sum C_n e^{in\theta}$，即 $g$ 的傅里叶级数，系数由欧拉-傅里叶公式给出：
$$
C_n=\frac{1}{2\pi}\int_0^{2\pi}g(\tau)e^{-in\tau}d\tau
$$
**4. 级数求和推导圆盘泊松核**

代入 $C_n$ 并交换求和与积分：
$$
u(r,\theta)=\frac{1}{2\pi}\int_0^{2\pi}g(\tau)\left(\sum_{n=-\infty}^{\infty}r^{|n|}e^{in(\theta-\tau)}\right)d\tau
$$
令 $\varphi=\theta-\tau$，计算和
$$
S=\sum_{n=-\infty}^{\infty}r^{|n|}e^{in\varphi}
=1+\sum_{n=1}^{\infty}(re^{i\varphi})^n+\sum_{n=1}^{\infty}(re^{-i\varphi})^n
$$
利用等比数列求和得：
$$
S=1+\frac{re^{i\varphi}}{1-re^{i\varphi}}+rac{re^{-i\varphi}}{1-re^{-i\varphi}}
=\frac{1-r^2}{1-2r\cos\varphi+r^2}
$$
代入得圆盘的泊松积分公式：
$$
u(r,\theta)=\frac{1}{2\pi}\int_0^{2\pi}\frac{1-r^2}{1-2r\cos(\theta-\tau)+r^2}g(\tau)d\tau
$$
与几何反演法结果一致。


把这个证明写的更简洁, 适合考场上书写
[Context: Notes: 分析/微分方程/调和方程格林函数的推导.md]
[Timestamp: 2026/06/20 16:46:06]