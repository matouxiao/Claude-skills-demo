# PPT生成问题修复说明

## 🐛 问题描述

**症状**：AI生成公司汇报PPT时，没有添加logo

**根本原因**：AI没有遵循SKILL.md的指导，而是自己编写了完整的python-pptx代码

## 🔍 问题分析

### AI实际做了什么（错误）：

```python
# ❌ AI自己写了160行python-pptx代码
from pptx import Presentation
prs = Presentation()  # 创建空白PPT
slide1 = prs.slides.add_slide(...)
# ... 手动创建每一页
prs.save("深圳介绍汇报.pptx")  # 没有logo
```

### AI应该做什么（正确）：

```python
# ✅ 使用SKILL.md的代码模板
import json
import subprocess
import sys

ppt_data = {...}  # JSON数据

with open('ppt_data.json', 'w', encoding='utf-8') as f:
    json.dump(ppt_data, f, ensure_ascii=False, indent=2)

cmd = [sys.executable, 'skills_storage/pptx/generate_ppt_from_json.py', 'ppt_data.json']
cmd.append('--add-logo')  # 如果是公司汇报，添加这行

result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
```

## 🛠️ 修复措施

### 1. 修改 SKILL.md

**添加了醒目的警告**：
```markdown
## ⚠️ 重要：必须遵守的规则

**禁止直接使用python-pptx库手动创建PPT！**

必须使用以下固定流程：
1. 生成JSON数据
2. 调用固定脚本 `skills_storage/pptx/generate_ppt_from_json.py`
3. 根据PPT类型决定是否添加 `--add-logo` 参数
```

**简化了代码模板**：
```python
# ⚠️ 强制要求：使用以下代码模板，只修改【】中的内容，其他代码不得更改！

ppt_data = {
    "output_file": "【PPT文件名】.pptx",
    "slides": [...]
}

# 保存JSON（不要修改）
with open('ppt_data.json', 'w', encoding='utf-8') as f:
    json.dump(ppt_data, f, ensure_ascii=False, indent=2)

# 调用脚本（不要修改）
cmd = [sys.executable, 'skills_storage/pptx/generate_ppt_from_json.py', 'ppt_data.json']

# ⚠️ 关键：如果是公司汇报类，必须添加这行（去掉注释）
# cmd.append('--add-logo')

result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
```

**标记了参考内容**：
```markdown
## 📖 说明

上面的**快速指南**是唯一需要遵循的流程。下面的内容仅供参考，**不要直接使用**。

---

## ⚠️ 以下内容仅供参考（不要在实际操作中使用）

下面的内容是技术文档和参考资料，用于了解PPT生成的底层原理。
**在实际操作时，必须使用上面的快速指南，不要使用下面的代码示例。**
```

### 2. 修改 main.py

**优化了 system_prompt**：
```python
system_prompt = (
    "你是一个有帮助的助手。\n\n"
    "【工作流程】\n"
    "1. 先调用 list_skills_catalog 查看可用技能\n"
    "2. 匹配到技能后，调用 get_skill_content(name) 获取完整指南\n"
    "3. **严格遵循**SKILL.md中的步骤和代码模板\n"
    "4. 使用 execute_python_code 执行代码生成文件\n\n"
    "【重要规则】\n"
    "- 必须完全按照SKILL.md的代码模板操作，不要自己编写代码\n"
    "- 只修改模板中【】标记的内容，其他部分不得更改\n"
    "- 如果SKILL.md明确禁止某种做法，绝对不能使用\n"
    "- 始终只使用一个技能，不要串联多个技能\n\n"
    "【生成文件时】\n"
    "- 使用 execute_python_code 直接执行代码并生成文件\n"
    "- 不要只给用户代码让他们手动执行\n"
    "- 按照SKILL.md的快速指南操作，不要跳过步骤"
)
```

**优化了获取技能后的提示**：
```python
working_msgs.append({
    "role": "system",
    "content": (
        "✅ 你已获取技能的完整操作指南（SKILL.md）。\n\n"
        "【强制要求】：\n"
        "1. 仔细阅读SKILL.md开头的「快速指南」部分\n"
        "2. 严格按照快速指南的3个步骤操作\n"
        "3. 使用SKILL.md提供的代码模板，只修改【】中的内容\n"
        "4. 不要自己编写新的代码，必须使用模板\n"
        "5. 如果SKILL.md明确禁止某种做法，绝对不能使用\n\n"
        "【执行流程】：\n"
        "- 步骤1：判断任务类型（根据SKILL.md的判断规则）\n"
        "- 步骤2：提取用户需求的内容\n"
        "- 步骤3：复制代码模板 → 填充【】内容 → 调用execute_python_code执行\n\n"
        "现在，请按照SKILL.md的快速指南完成任务。"
    )
})
```

## ✅ 测试方法

### 测试1：普通PPT（无logo）

**测试命令**：
```
用户输入: "帮我做个介绍深圳的PPT"
```

**预期行为**：
1. AI调用 `get_skill_content("pptx")`
2. AI判断：这是"介绍类" → 普通PPT
3. AI生成代码：
   ```python
   ppt_data = {"output_file": "魅力深圳.pptx", "slides": [...]}
   cmd = [..., 'generate_ppt_from_json.py', 'ppt_data.json']
   # 不添加 --add-logo
   ```
4. 执行生成PPT（无logo）

**验证**：
- ✅ 使用了固定脚本而非手动编写python-pptx代码
- ✅ 生成了ppt_data.json文件
- ✅ 调用了generate_ppt_from_json.py
- ✅ 没有添加--add-logo参数
- ✅ PPT没有logo

### 测试2：公司汇报PPT（带logo）

**测试命令**：
```
用户输入: "帮我做个2023年度公司绩效汇报"
```

**预期行为**：
1. AI调用 `get_skill_content("pptx")`
2. AI判断：包含"公司"、"汇报"关键词 → 公司汇报类
3. AI生成代码：
   ```python
   ppt_data = {"output_file": "2023年度公司绩效汇报.pptx", "slides": [...]}
   cmd = [..., 'generate_ppt_from_json.py', 'ppt_data.json']
   cmd.append('--add-logo')  # ✅ 添加logo参数
   ```
4. 执行生成PPT（带logo）

**验证**：
- ✅ 使用了固定脚本
- ✅ 生成了ppt_data.json文件
- ✅ 调用了generate_ppt_from_json.py
- ✅ 添加了--add-logo参数
- ✅ PPT每页右上角都有logo

### 测试3：检查生成的代码

**查看文件**：
```bash
# 查看AI生成的代码
cat last_generated_code.py

# 查看JSON数据
cat ppt_data.json
```

**正确的特征**：
- ✅ 代码中有 `import json`, `import subprocess`, `import sys`
- ✅ 代码中有 `ppt_data = {...}` JSON结构
- ✅ 代码中有 `subprocess.run([sys.executable, 'skills_storage/pptx/generate_ppt_from_json.py', ...])`
- ❌ 代码中没有 `from pptx import Presentation`
- ❌ 代码中没有 `prs = Presentation()`
- ❌ 代码中没有 `slide.shapes.add_textbox(...)`

## 📊 修复前后对比

| 维度 | 修复前 | 修复后 |
|------|--------|--------|
| AI行为 | 自己编写python-pptx代码 | 使用SKILL.md的代码模板 |
| 代码行数 | 160行手动代码 | 20行模板代码 |
| Logo添加 | ❌ 从未添加 | ✅ 根据类型自动添加 |
| SKILL.md | 被忽略 | 被严格遵循 |
| 可靠性 | ⚠️ 不稳定 | ✅ 稳定可靠 |

## 🎯 关键改进点

### 1. **明确的禁止条款**
在SKILL.md开头明确禁止直接使用python-pptx，强制使用固定脚本。

### 2. **简化的代码模板**
减少了模板的复杂度，只需填充【】中的内容。

### 3. **清晰的判断规则**
```python
# ⚠️ 关键：如果是公司汇报类，必须添加这行（去掉注释）
# cmd.append('--add-logo')
```
AI只需要判断是否去掉 `#` 注释符号。

### 4. **强化的System Prompt**
在main.py中多次强调必须遵循SKILL.md，不能自行编写代码。

### 5. **参考内容标记**
将后面的详细文档标记为"仅供参考"，防止AI误用。

## 🚀 运行测试

### 启动服务器
```bash
python main.py
```

### 通过API测试

**测试1：普通PPT**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "帮我做个介绍深圳的PPT"}'
```

**测试2：公司汇报PPT**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "帮我做个2023年度公司绩效汇报"}'
```

### 检查结果

```bash
# 查看生成的PPT
ls -la *.pptx

# 查看生成的代码
cat last_generated_code.py

# 查看JSON数据
cat ppt_data.json

# 打开PPT检查是否有logo
open *.pptx  # macOS
start *.pptx  # Windows
```

## 📝 总结

通过以下3个方面的修复：

1. **SKILL.md** - 添加明确警告，简化模板，标记参考内容
2. **main.py** - 强化system prompt，强调遵循规则
3. **测试验证** - 建立测试流程确保修复有效

现在AI应该能够：
- ✅ 正确识别PPT类型（公司汇报 vs 普通）
- ✅ 使用固定的代码模板
- ✅ 在公司汇报时添加logo
- ✅ 生成稳定可靠的PPT

## 🎉 预期结果

**普通PPT**：
- 使用代码模板 ✅
- 调用generate_ppt_from_json.py ✅
- 不添加--add-logo ✅
- PPT干净简洁，无logo ✅

**公司汇报PPT**：
- 使用代码模板 ✅
- 调用generate_ppt_from_json.py ✅
- 添加--add-logo ✅
- PPT每页右上角有logo ✅

