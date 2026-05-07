import os
import re

# 你的笔记存放目录
vault_path = r"D:\mathblog\quartz\content"

# 正则魔法：精准抓取以 > $$ 开头，以 $$ 结尾的闭合区块
# (?m) 是多行模式，re.DOTALL 让 .*? 能跨行匹配
pattern = re.compile(r"(?m)^[ \t]*>[ \t]*\$\$(.*?)\$\$", re.DOTALL)

def replacer(match):
    block = match.group(0)
    
    # 【绝对安全断路器】
    # 1. 如果这个块超过了 100 行（说明可能匹配失控跨越了文章）
    # 2. 如果块内出现了 Markdown 标题语法（\n# ）
    # 3. 如果块内嵌套了其他的标注块（\n> [!）
    # 只要满足以上任何一条，立刻原样返回，绝不乱加 >
    if block.count('\n') > 10 or "\n#" in block or "\n> [!" in match.group(1):
        return block
        
    # 如果安全，才开始逐行补全 >
    lines = block.split('\n')
    new_lines = []
    for line in lines:
        if line.strip() == "":
            new_lines.append("> ")
        elif not line.lstrip().startswith(">"):
            new_lines.append("> " + line)
        else:
            new_lines.append(line)
    return '\n'.join(new_lines)

fixed_count = 0

for root, dirs, files in os.walk(vault_path):
    for file in files:
        if not file.endswith(".md"): 
            continue
        
        filepath = os.path.join(root, file)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # 执行精确替换
        new_content = pattern.sub(replacer, content)
        
        # 只有真正发生改变时才写入文件
        if new_content != content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)
            fixed_count += 1
            print(f"✅ 精准修复: {file}")

print("-" * 30)
print(f"🎉 扫描完毕，安全修复了 {fixed_count} 个文件。")