[
    // Math mode
	{trigger: "mk", replacement: "$$0$", options: "tA"},
	{trigger: "dm", replacement: "$$\n$0\n$$", options: "tAw"},
	{trigger: "beg", replacement: "\\begin{$0}\n$1\n\\end{$0}", options: "mA"},
    {trigger: "dsp", replacement: "\\displaystyle ", options: "mA"},
    {trigger: "align", replacement:"\\begin{align}\n$0\n\\end{align}", options: "mA"},
    
    // Greek letters
    // 希腊字母后跟数字自动添加下标
    {trigger: "\\xii", replacement: "x_{i}", options: "mA", priority: 1},
    {trigger: /(\\alpha)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\beta)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\gamma)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\Gamma)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\delta)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\Delta)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\epsilon)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\varepsilon)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\zeta)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\eta)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\theta)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\Theta)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\vartheta)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\iota)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\kappa)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\lambda)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\Lambda)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\mu)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\nu)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\xi)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\Xi)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\pi)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\Pi)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\rho)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\sigma)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\Sigma)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\tau)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\upsilon)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\Upsilon)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\phi)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\Phi)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\varphi)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\chi)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\psi)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\Psi)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\omega)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: /(\\Omega)(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", priority: 1},
    {trigger: "lambda", replacement: "\\lambda", options: "mA"},
	{trigger: "@a", replacement: "\\alpha", options: "mA"},
	{trigger: "@b", replacement: "\\beta", options: "mA"},
	{trigger: "@g", replacement: "\\gamma", options: "mA"},
	{trigger: "@G", replacement: "\\Gamma", options: "mA"},
	{trigger: "@d", replacement: "\\delta", options: "mA"},
	{trigger: "@D", replacement: "\\Delta", options: "mA"},
	{trigger: "@e", replacement: "\\epsilon", options: "mA"},
	{trigger: ":e", replacement: "\\varepsilon", options: "mA"},
	{trigger: "@z", replacement: "\\zeta", options: "mA"},
	{trigger: "@t", replacement: "\\theta", options: "mA"},
	{trigger: "@T", replacement: "\\Theta", options: "mA"},
	{trigger: ":t", replacement: "\\vartheta", options: "mA"},
	{trigger: "@i", replacement: "\\iota", options: "mA"},
	{trigger: "@k", replacement: "\\kappa", options: "mA"},
	{trigger: "@l", replacement: "\\lambda", options: "mA"},
	{trigger: "@L", replacement: "\\Lambda", options: "mA"},
	{trigger: "@s", replacement: "\\sigma", options: "mA"},
	{trigger: "@S", replacement: "\\Sigma", options: "mA"},
	{trigger: "@u", replacement: "\\upsilon", options: "mA"},
	{trigger: "@U", replacement: "\\Upsilon", options: "mA"},
	{trigger: "@o", replacement: "\\omega", options: "mA"},
	{trigger: "@O", replacement: "\\Omega", options: "mA"},
	{trigger: "ome", replacement: "\\omega", options: "mA"},
	{trigger: "Ome", replacement: "\\Omega", options: "mA"},

    // Text environment
    {trigger: "text", replacement: "\\text{$0}$1", options: "mA"},
    {trigger: "\"", replacement: "\\text{$0}$1", options: "mA"},
    {trigger: "'''", replacement: "\\text{$0}$1", options: "mA"},

    // Basic operations
    {trigger: "sr", replacement: "^{2}", options: "mA"},
	{trigger: "cb", replacement: "^{3}", options: "mA"},
	{trigger: "rd", replacement: "^{$0}$1", options: "mA"},
	{trigger: "_", replacement: "_{$0}$1", options: "mA"},
	{trigger: "sts", replacement: "_\\text{$0}", options: "mA"},
	{trigger: "sq", replacement: "\\sqrt{$0}$1", options: "mA"},
	{trigger: "//", replacement: "\\frac{$0}{$1}$2", options: "mA"},
	{trigger: "ee", replacement: "e^{$0}$1", options: "mA"},
    {trigger: "invs", replacement: "^{-1}", options: "mA",priority:1},
    {trigger: "\\xi nvs", replacement: "x^{-1}", options: "mA",priority:1}, 
    // 修复问题1：更精确的自动下标，避免在符号后误触发
    {trigger: /([a-zA-Z])(\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA", description: "Auto letter subscript", priority: -1},

    {trigger: /([^\\])(exp|log|ln)/, replacement: "[[0]]\\[[1]]", options: "rmA"},
    {trigger: "conj", replacement: "^{*}", options: "mA"},
    {trigger: "RE", replacement: "\\mathrm{Re}", options: "mA"},
	{trigger: "Im", replacement: "\\mathrm{Im}", options: "mA"},
    {trigger: "bf", replacement: "\\mathbf{$0}", options: "mA"},
	{trigger: "rm", replacement: "\\mathrm{$0}$1", options: "mA"},
    {trigger: "bb([A-Z])", replacement: "\\mathbb{[[0]]}", options: "rmA"},
    {trigger: "mcl([A-Z])", replacement: "\\mathcal{[[0]]}", options: "rmA"},
    
    // Linear algebra
    {trigger: /([^\\])(det)/, replacement: "[[0]]\\[[1]]", options: "rmA"},
    {trigger: "trace", replacement: "\\mathrm{Tr}", options: "mA"},

    // More operations
	{trigger: "([a-zA-Z])hat", replacement: "\\widehat{[[0]]}", options: "rmA"},
    {trigger: "([a-zA-Z])bar", replacement: "\\bar{[[0]]}", options: "rmA"},
	{trigger: "([a-zA-Z])dot", replacement: "\\dot{[[0]]}", options: "rmA", priority: -1},
	{trigger: "([a-zA-Z])ddot", replacement: "\\ddot{[[0]]}", options: "rmA", priority: 1},
	{trigger: "([a-zA-Z])tilde", replacement: "\\widetilde{[[0]]}", options: "rmA"},
	{trigger: "([a-zA-Z])und", replacement: "\\underline{[[0]]}", options: "rmA"},
	{trigger: "([a-zA-Z])vec", replacement: "\\vec{[[0]]}", options: "rmA"},
	{trigger: "\\\\(${GREEK})\\.,", replacement: "\\boldsymbol{\\[[0]]}", options: "rmA"},
    {trigger: "([a-zA-Z])\\.,", replacement: "\\boldsymbol{[[0]]}", options: "rmA"},

    {trigger: "**", replacement: "^{*}", options: "mA"},
    {trigger: "vert", replacement: "\\Vert{$0}\\Vert$1", options: "mA"},
	{trigger: "hat", replacement: "\\widehat{$0}$1", options: "mA"},
    {trigger: "bar", replacement: "\\bar{$0}$1", options: "mA"},
	{trigger: "dot", replacement: "\\dot{$0}$1", options: "mA", priority: -1},
	{trigger: "ddot", replacement: "\\ddot{$0}$1", options: "mA"},
	{trigger: "c..", replacement: "\\cdot", options: "mA"},
    {trigger: "circ", replacement: "{\\circ}", options: "mA"},
	{trigger: "tilde", replacement: "\\widetilde{$0}$1", options: "mA"},
	{trigger: "uline", replacement: "\\underline{$0}$1", options: "mA"},
	{trigger: "vec", replacement: "\\vec{$0}$1", options: "mA"},
    {trigger: "oline", replacement: "\\overline{$0}$1", options: "mA"},
    {trigger: "overset", replacement: "\\overset{$0}{$1}$2", options: "mA"},
    

    // More auto letter subscript
    {trigger: /([A-Za-z])_(\d\d)/, replacement: "[[0]]_{[[1]]}", options: "rmA"},
	{trigger: /\\hat{([A-Za-z])}(\d)/, replacement: "\\hat{[[0]]}_{[[1]]}", options: "rmA"},
	{trigger: /\\vec{([A-Za-z])}(\d)/, replacement: "\\vec{[[0]]}_{[[1]]}", options: "rmA"},
	{trigger: /\\mathbf{([A-Za-z])}(\d)/, replacement: "\\mathbf{[[0]]}_{[[1]]}", options: "rmA"},
    
    {trigger: "([a-zA-Z])kk", replacement: "[[0]]_{k}", options: "rmA"},
    {trigger: "([a-zA-Z])ii", replacement: "[[0]]_{i}", options: "rmA"},
    {trigger: "([a-zA-Z])jj", replacement: "[[0]]_{j}", options: "rmA"},
    {trigger: "([a-zA-Z])nn", replacement: "[[0]]_{n}", options: "rmA"},
    {trigger: "([a-zA-Z])mm", replacement: "[[0]]_{m}", options: "rmA"},
    {trigger: "npp", replacement: "_{n+1}", options: "mA"},
    {trigger: "ipp", replacement: "_{i+1}", options: "mA"},
    {trigger: "jpp", replacement: "_{j+1}", options: "mA"},
    {trigger: "kpp", replacement: "_{k+1}", options: "mA"},
    {trigger: "xnn", replacement: "x_{n}", options: "mA"},
	{trigger: "xii", replacement: "x_{i}", options: "mA", priority: 1},
	{trigger: "xjj", replacement: "x_{j}", options: "mA"},
	{trigger: "xp1", replacement: "x_{n+1}", options: "mA"},

    //sequence
    {trigger: "([A-Za-z]+)ppp", replacement: "[[0]]_1+[[0]]_2+\\cdots+[[0]]_{${0:n}} ", options: "rm"},
    
    // Symbols
    {trigger: "rhook", replacement: "\\hookrightarrow", options: "mA"},
    {trigger: "rhc", replacement: "\\curvearrowright", options: "mA"},
    {trigger: "lhc", replacement: "\\curvearrowleft", options: "mA"},
    {trigger: "lhn", replacement: "\\triangleleft", options: "mA"},
    {trigger: "rhn", replacement: "\\triangleright", options: "mA"},
    {trigger: "inff", replacement: "\\inf", options: "mA"},
    {trigger: "supp", replacement: "\\sup", options: "mA"},
    {trigger: "ooo", replacement: "\\infty", options: "mA"},
	{trigger: "sum", replacement: "\\sum", options: "mA"},
	{trigger: "prod", replacement: "\\prod", options: "mA"},
	{trigger: "\\sum", replacement: "\\sum_{${0:k}=${1:1}}^{${2:N}} $3", options: "m"},
	{trigger: "\\prod", replacement: "\\prod_{${0:k}=${1:1}}^{${2:N}} $3", options: "m"},
    {trigger: "lim", replacement: "\\lim_{${0:n}\\to${1:\\infty}} $2", options: "mA"},
    {trigger: "+-", replacement: "\\pm", options: "mA"},
	{trigger: "-+", replacement: "\\mp", options: "mA"},
    {trigger: "...", replacement: "\\dots", options: "mA"},
    {trigger: "v.", replacement: "\\vdots", options: "mA"},
    {trigger: "nabl", replacement: "\\nabla", options: "mA"},
	{trigger: "del", replacement: "\\nabla", options: "mA"},
    {trigger: "xx", replacement: "\\times", options: "m"},
    {trigger: "para", replacement: "\\parallel", options: "mA"},

	{trigger: "===", replacement: "\\equiv", options: "mA"},
    {trigger: "!=", replacement: "\\neq", options: "mA"},
	{trigger: ">=", replacement: "\\geq", options: "mA"},
	{trigger: "<=", replacement: "\\leq", options: "mA"},
	{trigger: ">>", replacement: "\\gg", options: "mA"},
	{trigger: "<<", replacement: "\\ll", options: "mA"},
	{trigger: "simm", replacement: "\\sim", options: "mA",priority: 1},
	{trigger: "sim=", replacement: "\\simeq", options: "mA"},
    {trigger: "cong", replacement: "\\cong", options: "mA"},
    {trigger: "prop", replacement: "\\propto", options: "mA"},

    {trigger:"upp", replacement:"\\uparrow ",options: "mA"},
    {trigger:"loww", replacement:"\\downarrow ",options: "mA"},
    {trigger: "||", replacement: "\\mid", options: "mA"},
    {trigger: "<->", replacement: "\\longleftrightarrow ", options: "mA"},
	{trigger: "to", replacement: "\\to", options: "mA"},
	{trigger: "!>", replacement: "\\mapsto", options: "mA"},
    {trigger: "=>", replacement: "\\implies", options: "mA"},
	{trigger: "=<", replacement: "\\impliedby", options: "mA"},

    {trigger: "And", replacement: "\\bigcap", options: "mA"},
    {trigger: "And", replacement: "\\bigcap", options: "mA"},
    {trigger: "Orr", replacement: "\\bigcup", options: "mA"},
    {trigger: "DOrr", replacement: "\\bigsqcup", options: "mA"},
	{trigger: "and", replacement: "\\cap", options: "mA"},
	{trigger: "orr", replacement: "\\cup", options: "mA"},
	{trigger: ".in", replacement: "\\in", options: "mA"},
	{trigger: "notin", replacement: "\\not\\in", options: "mA"},
    {trigger: "\\\\\\", replacement: "\\setminus", options: "mA"},
    {trigger: "sub=", replacement: "\\subseteq", options: "mA"},
    {trigger: "sup=", replacement: "\\supseteq", options: "mA"},
	{trigger: "eset", replacement: "\\emptyset", options: "mA"},
	{trigger: "set", replacement: "\\{$0\\}$1", options: "mA"},
	{trigger: "e\\xi sts", replacement: "\\exists", options: "mA", priority: 1},

    {trigger: "PP", replacement: "\\mathcal{P}", options: "mA"},
    {trigger: "SS", replacement: "\\mathcal{S}", options: "mA"},
    {trigger: "FF", replacement: "\\mathcal{F}", options: "mA"},
	{trigger: "LL", replacement: "\\mathcal{L}", options: "mA"},
	{trigger: "HH", replacement: "\\mathcal{H}", options: "mA"},
	{trigger: "CC", replacement: "\\mathbb{C}", options: "mA"},
	{trigger: "RR", replacement: "\\mathbb{R}", options: "mA"},
	{trigger: "ZZ", replacement: "\\mathbb{Z}", options: "mA"},
	{trigger: "NN", replacement: "\\mathbb{N}", options: "mA"},
    {trigger: "QQ", replacement: "\\mathbb{Q}", options: "mA"},

    // 修复问题2：统一空格处理
    // 添加专门处理符号后数字的规则，避免自动下标
   {trigger: /(\\[a-zA-Z]+)(\d)/, replacement: "[[0]][[1]]", options: "rmA", description: "Keep numbers after commands as normal", priority: 0},
    
    // 添加好用的空格替换（问题3）
    {trigger: "sp", replacement: "\\:", options: "mA", description: "Medium space"},
    {trigger: "\\:p", replacement: "\\ ", options: "mA", description: "Thick space"},
    {trigger: "\\ p", replacement: "\\quad", options: "mA", description: "Thick space"},
    {trigger: "qq", replacement: "\\quad ", options: "mA", description: "Quad space"},
    {trigger: ".q", replacement: "\\qquad ", options: "mA", description: "Double quad space"},
    {trigger: "nsp", replacement: "\\!", options: "mA", description: "Negative space"},

	{trigger: "([^\\\\])(${GREEK})", replacement: "[[0]]\\[[1]]", options: "rmA", description: "Add backslash before Greek letters"},
	{trigger: "([^\\\\])(${SYMBOL})", replacement: "[[0]]\\[[1]]", options: "rmA", description: "Add backslash before symbols"},

    // Insert space after Greek letters and symbols
	{trigger: "\\\\(${GREEK}|${SYMBOL}|${MORE_SYMBOLS})([A-Za-z])", replacement: "\\[[0]] [[1]]", options: "rmA"},
	{trigger: "\\\\(${GREEK}|${SYMBOL}) sr", replacement: "\\[[0]]^{2}", options: "rmA"},
	{trigger: "\\\\(${GREEK}|${SYMBOL}) cb", replacement: "\\[[0]]^{3}", options: "rmA"},
	{trigger: "\\\\(${GREEK}|${SYMBOL}) rd", replacement: "\\[[0]]^{$0}$1", options: "rmA"},
	{trigger: "\\\\(${GREEK}|${SYMBOL}) hat", replacement: "\\hat{\\[[0]]}", options: "rmA"},
	{trigger: "\\\\(${GREEK}|${SYMBOL}) dot", replacement: "\\dot{\\[[0]]}", options: "rmA"},
	{trigger: "\\\\(${GREEK}|${SYMBOL}) bar", replacement: "\\bar{\\[[0]]}", options: "rmA"},
	{trigger: "\\\\(${GREEK}|${SYMBOL}) vec", replacement: "\\vec{\\[[0]]}", options: "rmA"},
	{trigger: "\\\\(${GREEK}|${SYMBOL}) tilde", replacement: "\\tilde{\\[[0]]}", options: "rmA"},{trigger: "\\\\(${GREEK}|${SYMBOL}|${MORE_SYMBOLS}) over", replacement: "\\overset{$0}{\\[[0]]}$1", options: "rmA"},
    {trigger: "([a-zA-Z])over", replacement: "\\overset{$0}{[[0]]}$1", options: "rmA"},
    {trigger: "=over", replacement: "\\overset{$0}{=}$1", options: "mA"},

    // Derivatives and integrals
    {trigger:"ppp", replacement: "\\partial", options: "mA"},
    {trigger: "par", replacement: "\\frac{\\partial ${0:y}}{\\partial ${1:x}} $2", options: "mA"},
    {trigger: /p([A-Za-z])p([A-Za-z])/, replacement: "\\frac{\\partial [[0]]}{\\partial [[1]]} ", options: "mA"},
    {trigger: "ppa", replacement: "\\frac{ \\partial^{2} ${0:y}}{\\partial ${1:x}^{2}} $2", options: "mA"},
    {trigger: "ddt", replacement: "\\frac{d}{dt} ", options: "mA"},
    {trigger: "ppz", replacement: "\\frac{\\partial}{\\partial z} ", options: "mA"},
    {trigger: /([^\\])int/, replacement: "[[0]]\\int", options: "mA", priority: -1},
    {trigger: "\\int", replacement: "\\int $0 \\, d${1:x} $2", options: "m"},
    {trigger: "dint", replacement: "\\int_{${0:0}}^{${1:1}} $2 \\, d${3:x} $4", options: "mA"},
    {trigger: "oint", replacement: "\\oint", options: "mA"},
	{trigger: "iint", replacement: "\\iint", options: "mA"},
    {trigger: "i_{i}nt", replacement: "\\iiint", options: "mA"},
    {trigger: "oinf", replacement: "\\int_{0}^{\\infty} $0 \\, d${1:x} $2", options: "mA"},
	{trigger: "infi", replacement: "\\int_{-\\infty}^{+\\infty} $0 \\, d${1:x} $2", options: "mA"},
    {trigger: "infty", replacement: "\\infty", options:"mA"},

    // Trigonometry
    {trigger: /([^\\])(arcsin|sin|arccos|cos|arctan|tan|csc|sec|cot)/, replacement: "[[0]]\\[[1]]", options: "rmA", description: "Add backslash before trig funcs"},

    {trigger: /\\(arcsin|sin|arccos|cos|arctan|tan|csc|sec|cot)([A-Za-gi-z])/,
     replacement: "\\[[0]] [[1]]", options: "rmA",
     description: "Add space after trig funcs. Skips letter h to allow sinh, cosh, etc."},

    {trigger: /\\(sinh|cosh|tanh|coth)([A-Za-z])/,
     replacement: "\\[[0]] [[1]]", options: "rmA",
     description: "Add space after hyperbolic trig funcs"},

    // Visual operations
	{trigger: "U", replacement: "\\underbrace{${VISUAL}}_{$0}", options: "mA"},
	{trigger: "O", replacement: "\\overbrace{${VISUAL}}^{$0}", options: "mA"},
	{trigger: "B", replacement: "\\underset{$0}{${VISUAL}}", options: "mA"},
	{trigger: "C", replacement: "\\cancel{${VISUAL}}", options: "mA"},
	{trigger: "K", replacement: "\\cancelto{$0}{${VISUAL}}", options: "mA"},
	{trigger: "S", replacement: "\\sqrt{${VISUAL}}", options: "mA"},

    // Physics
	{trigger: "kbt", replacement: "k_{B}T", options: "mA"},
	{trigger: "msun", replacement: "M_{\\odot}", options: "mA"},

    // Quantum mechanics
    {trigger: "dag", replacement: "^{\\dagger}", options: "mA"},
	{trigger: "o+", replacement: "\\oplus ", options: "m"},
    {trigger: "O+", replacement: "\\bigoplus ", options: "m"},
	{trigger: "ox", replacement: "\\otimes ", options: "mA"},
    {trigger: "bra", replacement: "\\bra{$0} $1", options: "mA"},
	{trigger: "ket", replacement: "\\ket{$0} $1", options: "mA"},
	{trigger: "brk", replacement: "\\braket{$0|$1} $2", options: "mA"},
    {trigger: "outer", replacement: "\\ket{${0:\\psi}}\\bra{${0:\\psi}} $1", options: "mA"},

    // Chemistry
	{trigger: "pu", replacement: "\\pu{$0}", options: "mA"},
	{trigger: "cee", replacement: "\\ce{$0}", options: "mA"},
	{trigger: "he4", replacement: "{}^{4}_{2}He ", options: "mA"},
	{trigger: "he3", replacement: "{}^{3}_{2}He ", options: "mA"},
	{trigger: "iso", replacement: "{}^{${0:4}}_{${1:2}}${2:He}", options: "mA"},

    // Environments
	{trigger: "pmat", replacement: "\\begin{pmatrix}\n$0\n\\end{pmatrix}", options: "MA"},
	{trigger: "bmat", replacement: "\\begin{bmatrix}\n$0\n\\end{bmatrix}", options: "MA"},
	{trigger: "Bmat", replacement: "\\begin{Bmatrix}\n$0\n\\end{Bmatrix}", options: "MA"},
	{trigger: "vmat", replacement: "\\begin{vmatrix}\n$0\n\\end{vmatrix}", options: "MA"},
	{trigger: "Vmat", replacement: "\\begin{Vmatrix}\n$0\n\\end{Vmatrix}", options: "MA"},
	{trigger: "matrix", replacement: "\\begin{matrix}\n$0\n\\end{matrix}", options: "MA"},

	{trigger: "pmat", replacement: "\\begin{pmatrix}$0\\end{pmatrix}", options: "nA"},
	{trigger: "bmat", replacement: "\\begin{bmatrix}$0\\end{bmatrix}", options: "nA"},
	{trigger: "Bmat", replacement: "\\begin{Bmatrix}$0\\end{Bmatrix}", options: "nA"},
	{trigger: "vmat", replacement: "\\begin{vmatrix}$0\\end{vmatrix}", options: "nA"},
	{trigger: "Vmat", replacement: "\\begin{Vmatrix}$0\\end{Vmatrix}", options: "nA"},
	{trigger: "matrix", replacement: "\\begin{matrix}$0\\end{matrix}", options: "nA"},

	{trigger: "cases", replacement: "\\begin{cases}\n$0\n\\end{cases}", options: "mA"},
	{trigger: "align", replacement: "\\begin{align}\n$0\n\\end{align}", options: "mA"},
	{trigger: "array", replacement: "\\begin{array}\n$0\n\\end{array}", options: "mA"},

    // Brackets
	{trigger: "avg", replacement: "\\langle $0 \\rangle $1", options: "mA"},
	{trigger: "norm", replacement: "\\lvert $0 \\rvert $1", options: "mA", priority: 1},
	{trigger: "Norm", replacement: "\\lVert $0 \\rVert $1", options: "mA", priority: 1},
	{trigger: "ceil", replacement: "\\lceil $0 \\rceil $1", options: "mA"},
	{trigger: "floor", replacement: "\\lfloor $0 \\rfloor $1", options: "mA"},
	{trigger: "mod", replacement: "|$0|$1", options: "mA"},
	{trigger: "(", replacement: "(${VISUAL})", options: "mA"},
	{trigger: "[", replacement: "[${VISUAL}]", options: "mA"},
	{trigger: "{", replacement: "{${VISUAL}}", options: "mA"},
	{trigger: "(", replacement: "($0)$1", options: "mA"},
	{trigger: "{", replacement: "{$0}$1", options: "mA"},
	{trigger: "[", replacement: "[$0]$1", options: "mA"},
	{trigger: "lr(", replacement: "\\left( $0 \\right) $1", options: "mA"},
	{trigger: "lr{", replacement: "\\left\\{ $0 \\right\\} $1", options: "mA"},
	{trigger: "lr[", replacement: "\\left[ $0 \\right] $1", options: "mA"},
	{trigger: "abs", replacement: "\\left| $0 \\right| $1", options: "mA"},
	{trigger: "lra", replacement: "\\left< $0 \\right> $1", options: "mA"},
    {trigger: "-->", replacement: "\\rightrightarrows", options: "mA"},

    // Snippet replacements can have placeholders.
	{trigger: "tayl", replacement: "${0:f}(${1:x}+${2:h})=${0:f}(${1:x})+${0:f}'(${1:x})${2:h}+${0:f}''(${1:x})\\frac{${2:h}^{2}}{2!}+\\dots$3", options: "mA", description: "Taylor expansion"},

    // Snippet replacements can also be JavaScript functions.
    // See the documentation for more information.
	{trigger: /iden(\d)/, replacement: (match) => {
		const n = match[1];

		let arr = [];
		for (let j = 0; j < n; j++) {
			arr[j] = [];
			for (let i = 0; i < n; i++) {
				arr[j][i] = (i === j) ? 1 : 0;
			}
		}

		let output = arr.map(el => el.join(" & ")).join(" \\\\\n");
		output = `\\begin{pmatrix}\n${output}\n\\end{pmatrix}`;
		return output;
	}, options: "mA", description: "N x N identity matrix"},
]
