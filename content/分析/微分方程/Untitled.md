### Hopf Lemma (极简版)

**定理：**

设单位球$B_1\subset\mathbb{R}^n$，
1. 函数$u\in C^2(B_1)\cap C(\overline{B_1})$在球内满足$\Delta u\ge 0$。若存在边界点
2. $x_0\in\partial B_1$，使得对所有内部点$x\in B_1$均有$u(x)<u(x_0)$，
3. 且$u$在$x_0$处外法向导数存在，则必有$\frac{\partial u}{\partial n}(x_0)>0$。
​	​	![[Pasted image 20260616093635.png|300]]
### 证明

**1. 构造障碍函数**

设$v(x)=e^{-\alpha|x|^2}-e^{-\alpha}$。计算得$\Delta v(x)=(-2n\alpha+4\alpha^2|x|^2)e^{-\alpha|x|^2}$。

**2. 选取球壳区域**

取半径$R\in(0,1)$，在球壳$A=B_1\setminus\overline{B_R}$中，即$R<|x|<1$。取足够大的$\alpha>0$使得$4\alpha^2R^2-2n\alpha>0$，从而在$A$内恒有$\Delta v>0$。

**3. 边界比较**

构造$w(x)=u(x)+\varepsilon v(x)$。

- 在$\partial B_1$上：$|x|=1$，$v(x)=0$，故$w(x)=u(x)\le u(x_0)$ 
- 在$\partial B_R$上：$u$严格小于$u(x_0)$，存在$\delta>0$使$u(x)\le u(x_0)-\delta$。因$v(x)>0$，取足够小的$\varepsilon>0$使$\varepsilon v(x)\le\delta$，便有$w(x)\le u(x_0)$。
    

**4. 极大值原理**

在$A$内$\Delta w=\Delta u+\varepsilon\Delta v>0$，$w$为严格次调和函数，最大值只能在边界$\partial A$取得。由上步知，在$\overline{A}$上恒有$w(x)\le u(x_0)$。

**5. 导出矛盾**
函数 $w$ 沿外法向 $n$ 的方向导数定义为：
$$\frac{\partial w}{\partial n}(x_0)=\lim_{t\to0^+}\frac{w(x_0)-w(x_0-tn)}{t}$$

在$x_0$处$v(x_0)=0$，故$w(x_0)=u(x_0)$。这说明$w$在$x_0$处取最大值，其外法向导数必满足$\frac{\partial w}{\partial n}(x_0)\ge 0$。

展开得$\frac{\partial u}{\partial n}(x_0)+\varepsilon\frac{\partial v}{\partial n}(x_0)\ge 0$。

因$\frac{\partial v}{\partial n}(x_0)=\nabla v(x_0)\cdot x_0=-2\alpha e^{-\alpha}<0$，代入移项即得：

$\frac{\partial u}{\partial n}(x_0)\ge 2\varepsilon\alpha e^{-\alpha}>0$。证明完毕。


# Hopf Lemma 使用弱极值原理证明

**一句话**：局部切一块区域，给 $u$ 加一个很小的障碍函数，然后对新函数用弱最大值原理。

**定理**：  
设 $u\in C^{2}(B_{1})\cap C^{1}(\overline{B_{1}})$，$\Delta u\ge 0$。若 $x_{0}\in\partial B_{1}$ 满足  
$$u(x_{0})=\max_{\overline{B_{1}}}u,$$  
且 $u$ 非常数，则  
$$\frac{\partial u}{\partial n}(x_{0})>0.$$  
对单位球 $n=x_{0}$。

**证明思路**  
1. **切区域**：取小球 $B_{\rho}(x_{0})$，令 $\Omega=B_{1}\cap B_{\rho}(x_{0})$，边界  
   $$\partial\Omega=\Gamma_{1}\cup\Gamma_{2},$$  
   $\Gamma_{1}$ 在 $\partial B_{1}$ 上，$\Gamma_{2}$ 在球内。

2. **障碍函数**：  
   $$w(x)=e^{-a|x|^{2}}-e^{-a}.$$  
   性质：$w=0$ on $\partial B_{1}$，在球内 $w>0$，$\Delta w\ge0$。

3. **辅助函数**：  
   $$\widetilde{u}=u+\varepsilon w\quad\Rightarrow\quad\Delta\widetilde{u}\ge0,$$  
   可对其用弱最大值原理。
![[Pasted image 20260616093730.png|200]]
4. **边界控制**：  
   - 在 $\Gamma_{1}$ 上：$w=0\;\Rightarrow\;\widetilde{u}=u\le u(x_{0})$。  
   - 在 $\Gamma_{2}$ 上：内部严格小于最大值，取 $\varepsilon$ 充分小有 $\widetilde{u}=u+\varepsilon w\le u(x_{0})$。  **这里是因为$\Gamma_{2}$这个边界远离$x_{0}$** 
   故在整个 $\partial\Omega$ 上 $\widetilde{u}\le u(x_{0})$，由弱最大值原理  
$$\widetilde{u}\le u(x_{0})\quad\text{in }\Omega.$$
　
3. **导出严格导数**：  
   取 $x=x_{0}-tn$（内法向），则  
$$u(x_{0})-u(x_{0}-tn)\ge\varepsilon w(x_{0}-tn).$$  
   除以 $t>0$ 并令 $t\to0^{+}$，右端极限为正（$w$ 沿内法向严格增长），于是  
   $$\frac{\partial u}{\partial n}(x_{0})>0.$$

**核心逻辑**  
由 $u\le u(x_{0})$ 外加正函数 $w$ 得 $u+\varepsilon w\le u(x_{0})$，即  
$$u(x_{0})-u\ge\varepsilon w(x),$$  
从而迫使 $u$ 从内部靠近边界时有一阶严格增长，故外法向导数必 $>0$。