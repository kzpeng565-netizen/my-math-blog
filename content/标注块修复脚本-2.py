import os

# 你的笔记存放目录
vault_path = r"D:\mathblog\quartz\content"
fixed_count = 0

for root, dirs, files in os.walk(vault_path):
    for file in files:
        if not file.endswith(".md"): 
            continue
        
        filepath = os.path.join(root, file)
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        new_lines = []
        in_lazy_quote = False
        changed = False
        
        for line in lines:
            lstripped = line.lstrip()
            stripped = line.strip()
            
            # 场景 1：这一行明确以 > 开头，说明进入或维持在引用块内
            if lstripped.startswith(">"):
                in_lazy_quote = True
                new_lines.append(line)
                
            # 场景 2：我们在引用块的“惯性”范围内
            elif in_lazy_quote:
                # 【绝对安全断路器】：遇到空行，立刻切断“惯性”，引用块结束
                if stripped == "":
                    in_lazy_quote = False
                    new_lines.append(line)
                else:
                    # 核心修复：非空行紧紧贴在 > 后面，帮它补上 >
                    new_lines.append("> " + line)
                    changed = True
                    
            # 场景 3：正常的非引用正文，安全放行
            else:
                new_lines.append(line)
                
        # 只有真正发生改变时才写入文件
        if changed:
            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            print(f"✅ 修复懒人引用: {file}")
            fixed_count += 1

print("-" * 30)
print(f"🎉 扫描完毕，安全修复了 {fixed_count} 个文件。")