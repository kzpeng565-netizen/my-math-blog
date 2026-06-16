### Hopf Lemma (极简版)

**定理：**

设单位球$B_1\subset\mathbb{R}^n$，
1. 函数$u\in C^2(B_1)\cap C(\overline{B_1})$在球内满足$\Delta u\ge 0$。若存在边界点
2. $x_0\in\partial B_1$，使得对所有内部点$x\in B_1$均有$u(x)<u(x_0)$，
3. 且$u$在$x_0$处外法向导数存在，则必有$\frac{\partial u}{\partial n}(x_0)>0$。
​	​	
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

在$x_0$处$v(x_0)=0$，故$w(x_0)=u(x_0)$。这说明$w$在$x_0$处取最大值，其外法向导数必满足$\frac{\partial w}{\partial n}(x_0)\ge 0$。

展开得$\frac{\partial u}{\partial n}(x_0)+\varepsilon\frac{\partial v}{\partial n}(x_0)\ge 0$。

因$\frac{\partial v}{\partial n}(x_0)=\nabla v(x_0)\cdot x_0=-2\alpha e^{-\alpha}<0$，代入移项即得：

$\frac{\partial u}{\partial n}(x_0)\ge 2\varepsilon\alpha e^{-\alpha}>0$。证明完毕。

