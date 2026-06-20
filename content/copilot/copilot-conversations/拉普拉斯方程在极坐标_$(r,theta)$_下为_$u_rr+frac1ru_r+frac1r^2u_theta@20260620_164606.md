---
epoch: 1781945166797
modelKey: "deepseek-reasoner|deepseek"
topic: "Laplace equation polar coordinates"



tags:
  - copilot-conversation
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

**ai**: 
<think>我们被要求将单位圆盘泊松核推导的傅里叶方法部分写得更简洁，适合考场书写。原始文本已经比较详细，但可能包含一些解释性文字。需要提取关键步骤，用公式和简短的文字表述。注意保持正确性。

整理思路：

1. 极坐标下拉普拉斯方程：$u_{rr} + \frac{1}{r}u_r + \frac{1}{r^2}u_{\theta\theta}=0$
2. 分离变量 $u(r,\theta)=R(r)\Theta(\theta)$ → $\Theta''+n^2\Theta=0$, $r^2R''+rR'-n^2R=0$
3. 通解：$\Theta(\theta)=e^{in\theta}$（周期性要求 $n$ 整数），$R_n(r)=A_n r^{|n|}+B_n r^{-|n|}$
4. $r=0$ 有界 → $B_n=0$，故 $u(r,\theta)=\sum_{n=-\infty}^\infty C_n r^{|n|} e^{in\theta}$
5. 边界条件 $r=1$: $g(\theta)=\sum C_n e^{in\theta}$ → $C_n=\frac{1}{2\pi}\int_0^{2\pi} g(\tau) e^{-in\tau}d\tau$
6. 代入：$u(r,\theta)=\frac{1}{2\pi}\int_0^{2\pi} g(\tau)\left(\sum_{n=-\infty}^\infty r^{|n|} e^{in(\theta-\tau)}\right)d\tau$
7. 计算内和：令 $\varphi=\theta-\tau$
   $S=\sum_{n=-\infty}^\infty r^{|n|}e^{in\varphi}=1+\sum_{n=1}^\infty (re^{i\varphi})^n+\sum_{n=1}^\infty (re^{-i\varphi})^n$
   $=1+\frac{re^{i\varphi}}{1-re^{i\varphi}}+\frac{re^{-i\varphi}}{1-re^{-i\varphi}}=\frac{1-r^2}{1-2r\cos\varphi+r^2}$
8. 最终：$u(r,\theta)=\frac{1}{2\pi}\int_0^{2\pi} \frac{1-r^2}{1-2r\cos(\theta-\tau)+r^2}g(\tau)d\tau$

需要简洁，可以去掉一些解释如“为了有界”等，但考场书写通常还需要简要说明。我可以用bullet points或紧凑段落。</think>**单位圆盘泊松核（傅里叶方法）**  

1. **分离变量**：  
   - 极坐标下拉普拉斯方程：$u_{rr}+\frac{1}{r}u_r+\frac{1}{r^2}u_{\theta\theta}=0$。  
   - 设 $u(r,\theta)=R(r)\Theta(\theta)$，得 $\Theta''+n^2\Theta=0$（$n$ 整数），$r^2R''+rR'-n^2R=0$。  

2. **通解与有界性**：  
   - $\Theta(\theta)=e^{in\theta}$，$R_n(r)=A_n r^{|n|}+B_n r^{-|n|}$。  
   - $r=0$ 处有界 $\Rightarrow B_n=0$，故  
     $$u(r,\theta)=\sum_{n=-\infty}^{\infty} C_n r^{|n|} e^{in\theta}.$$  

3. **边界条件**：$u(1,\theta)=g(\theta)=\sum C_n e^{in\theta}$ $\Rightarrow$ $C_n=\frac{1}{2\pi}\int_0^{2\pi} g(\tau)e^{-in\tau}d\tau$。  

4. **代入并交换积分与求和**：  
   $$u(r,\theta)=\frac{1}{2\pi}\int_0^{2\pi} g(\tau)\left(\sum_{n=-\infty}^{\infty}r^{|n|} e^{in(\theta-\tau)}\right)d\tau.$$  
   令 $\varphi=\theta-\tau$，计算内和：  
   $$
   \begin{aligned}
   S&=\sum_{n=-\infty}^{\infty}r^{|n|}e^{in\varphi}
   =1+\sum_{n=1}^{\infty}(re^{i\varphi})^n+\sum_{n=1}^{\infty}(re^{-i\varphi})^n \\
   &=1+\frac{re^{i\varphi}}{1-re^{i\varphi}}+\frac{re^{-i\varphi}}{1-re^{-i\varphi}}
   =\frac{1-r^2}{1-2r\cos\varphi+r^2}.
   \end{aligned}
   $$

5. **泊松积分公式**：  
   $$u(r,\theta)=\frac{1}{2\pi}\int_0^{2\pi}\frac{1-r^2}{1-2r\cos(\theta-\tau)+r^2}\,g(\tau)\,d\tau.$$  
   核函数 $K(r,\theta-\tau)=\dfrac{1-r^2}{1-2r\cos(\theta-\tau)+r^2}$ 即单位圆盘的泊松核。
[Timestamp: 2026/06/20 16:46:19]

**user**: 不要用1.2.3加粗
[Context: Notes: 分析/微分方程/调和方程格林函数的推导.md]
[Timestamp: 2026/06/20 16:46:27]