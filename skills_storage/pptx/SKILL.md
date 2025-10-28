---
name: pptx
description: "创建和编辑演示文稿。当用户需要制作 PPT、幻灯片或演示文稿时使用此技能。支持：(1) 创建新的演示文稿，(2) 使用模板创建正式汇报，(3) 自定义设计和布局"
license: Proprietary
---

# PPT 演示文稿创建

## 概述

当用户需要创建演示文稿时，根据场景选择合适的创建方式：
- **公司汇报类**：添加公司logo（logo1.png）到每页右上角
- **普通PPT**：不添加logo，直接生成

## 🔍 判断规则：公司汇报类 vs 普通PPT

### 公司汇报类（需要添加logo）

**触发关键词**（用户消息包含以下任一词汇）：
- "公司汇报"、"工作汇报"、"述职"
- "转正"、"晋升答辩"、"答辩"
- "季度汇报"、"年度总结"、"年终总结"
- "项目汇报"、"正式汇报"、"部门汇报"
- 明确要求"添加公司logo"或"使用公司模板"

**特征**：
- 正式场合
- 需要体现公司形象
- 每页右上角添加 `logo1.png`

### 普通PPT（不添加logo）

**触发场景**：
- 介绍类PPT（如"介绍深圳"、"介绍产品"）
- 教学类、培训类PPT
- 个人展示、非正式场合
- 创意型、娱乐型演示
- 没有提到上述公司汇报关键词

**特征**：
- 非正式场合
- 不需要公司标识
- 清爽简洁的设计

## ⚠️ 使用模板的强制规则

**使用公司汇报模板时，必须严格按照以下代码模板（复制并修改内容）：**

**重要：** 模板 `附件2：进门_转正答辩PPT模板.pptx` 只有 **3张幻灯片**，不要试图访问第4张！

```python
from pptx import Presentation

# 第1步：加载模板（绝对不能用 Presentation() 空括号！）
prs = Presentation('skills_storage/pptx/temple/附件2：进门_转正答辩PPT模板.pptx')

# 第2步：检查模板幻灯片数量，不要超出范围
print(f"模板有 {len(prs.slides)} 张幻灯片")
# 注意：这个模板只有3张幻灯片！

# 如果模板幻灯片数量足够，可以删除多余的；否则只使用现有的
# 这个模板有3张，所以通常不需要删除

# 第3步：修改每页的文本内容（只修改文本，不修改形状、背景、logo）
# 第1页 - 封面
for shape in prs.slides[0].shapes:
    if hasattr(shape, "text_frame"):
        if shape.top < 2000000:  # 标题区域
            shape.text = "您的标题"
        else:  # 副标题区域
            shape.text = "您的副标题"

# 第2-3页 - 内容页（模板只有3张幻灯片！）
for slide_idx in [1, 2]:  # 只访问索引1和2，因为模板只有3张
    slide = prs.slides[slide_idx]
    title_set = False
    for shape in slide.shapes:
        if hasattr(shape, "text_frame"):
            if shape.top < 1500000 and not title_set:
                shape.text = f"第{slide_idx+1}页标题"
                title_set = True
            elif shape.top >= 1500000:
                tf = shape.text_frame
                tf.clear()
                tf.text = "• 第一点内容"
                p = tf.add_paragraph()
                p.text = "• 第二点内容"
                p.level = 0

# 第4步：保存
prs.save('output.pptx')
```

**❌ 绝对禁止的错误写法：**
```python
prs = Presentation()  # ❌ 错误！空括号会创建空白演示
prs.slides.add_slide(layout)  # ❌ 错误！add_slide会丢失模板设计
slide.shapes.add_textbox(...)  # ❌ 错误！手动添加形状会丢失模板
```

**✅ 记住：**
- 使用 `Presentation('模板路径')`，不是 `Presentation()`
- 修改现有幻灯片，不是添加新幻灯片
- 只修改 `.text` 属性，不添加新形状

---

## 决策规则：何时使用模板 vs 从头创建

### 使用模板（temple 文件夹）

**触发关键词**（用户提到以下任一词汇）：
- "公司汇报"、"工作汇报"、"述职"
- "转正"、"晋升答辩"
- "季度汇报"、"年度总结"
- "项目汇报"、"正式汇报"
- 或明确说"使用模板"

**操作方式**：
- 模板位置：`skills_storage/pptx/temple/附件2：进门_转正答辩PPT模板.pptx`
- 使用 python-pptx 库加载模板
- 修改模板中的文本内容
- 保持模板原有设计和布局

### 从头创建

**触发场景**：
- 用户要求自定义设计
- 非正式场合的演示
- 创意型、教学型 PPT

**操作方式**：
- 使用 python-pptx 库创建空白演示文稿
- 根据用户需求设计布局和样式

## 核心工具：python-pptx 库

### 基础用法

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

# 创建新演示文稿
prs = Presentation()

# 或加载现有模板
prs = Presentation('template.pptx')

# 添加幻灯片
slide_layout = prs.slide_layouts[0]  # 0=标题页, 1=标题和内容
slide = prs.slides.add_slide(slide_layout)

# 修改文本
title = slide.shapes.title
title.text = "演示标题"

# 保存
prs.save('output.pptx')
```

### 常用布局索引

- `0`: 标题幻灯片（封面）
- `1`: 标题和内容
- `2`: 节标题
- `5`: 标题和两栏内容
- `6`: 空白

### 修改模板文本的完整示例

```python
from pptx import Presentation

# 加载模板
template_path = 'skills_storage/pptx/temple/附件2：进门_转正答辩PPT模板.pptx'
prs = Presentation(template_path)

# 遍历所有幻灯片
for slide_idx, slide in enumerate(prs.slides):
    print(f"幻灯片 {slide_idx}:")
    
    # 遍历所有形状（文本框）
    for shape_idx, shape in enumerate(slide.shapes):
        if hasattr(shape, "text_frame"):
            print(f"  形状 {shape_idx}: {shape.text[:50]}")
            
            # 修改文本
            if slide_idx == 0 and shape_idx == 0:  # 第一页标题
                shape.text = "新的标题"
            
            # 或逐段修改
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    run.text = "新内容"

# 保存修改后的演示文稿
prs.save('output.pptx')
```

### 创建带格式文本的幻灯片

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[1])

# 标题
title = slide.shapes.title
title.text = "标题文字"

# 内容
content = slide.placeholders[1]
tf = content.text_frame
tf.text = "第一段"

# 添加段落
p = tf.add_paragraph()
p.text = "第二段"
p.level = 1  # 缩进级别

# 设置字体
run = p.runs[0]
run.font.size = Pt(18)
run.font.bold = True

prs.save('output.pptx')
```

## 工作流程

### 场景 1：使用模板创建正式汇报

**重要原则**：使用模板时，必须保留模板的背景、logo 和所有设计元素。只修改文本内容，不修改设计。

#### 正确的模板使用方法

1. **加载模板**：使用 `Presentation(template_path)` 加载
2. **使用模板幻灯片**：选择合适的模板幻灯片（根据需要复制）
3. **只修改文本**：遍历文本框，只修改 `text` 内容
4. **保留所有设计**：不删除、不添加形状，保持原有布局

#### 示例代码：使用模板创建 4 页 PPT

```python
from pptx import Presentation
from copy import deepcopy

# 1. 加载模板
template_path = 'skills_storage/pptx/temple/附件2：进门_转正答辩PPT模板.pptx'
prs = Presentation(template_path)

# 2. 选择需要使用的模板幻灯片索引
# 建议：先查看模板，选择合适的幻灯片作为基础
# 例如：0=封面, 1=目录, 2-5=内容页等

# 3. 创建新演示（只包含需要的幻灯片）
# 方法：从模板中选择幻灯片，删除不需要的
slides_to_keep = [0, 2, 3, 4]  # 保留第 0, 2, 3, 4 张幻灯片

# 删除不需要的幻灯片（从后往前删，避免索引错乱）
slides_to_delete = []
for i in range(len(prs.slides)):
    if i not in slides_to_keep:
        slides_to_delete.append(i)

for i in sorted(slides_to_delete, reverse=True):
    rId = prs.slides._sldIdLst[i].rId
    prs.part.drop_rel(rId)
    del prs.slides._sldIdLst[i]

# 4. 修改保留的幻灯片文本
# 第1页（原索引0）- 封面
slide_0 = prs.slides[0]
for shape in slide_0.shapes:
    if hasattr(shape, "text_frame"):
        if "标题" in shape.text or shape.text.strip() == "":
            shape.text = "杨柳公司汇报"
        elif "副标题" in shape.text:
            shape.text = "2024年度工作总结"

# 第2页（原索引2）- 内容页1
slide_1 = prs.slides[1]
for shape in slide_1.shapes:
    if hasattr(shape, "text_frame"):
        if shape.text_frame.text.strip() in ["", "标题"]:
            shape.text = "公司概况"
        else:
            # 清空并添加新内容
            tf = shape.text_frame
            tf.clear()
            tf.text = "• 公司名称：杨柳有限公司"
            p = tf.add_paragraph()
            p.text = "• 成立时间：2010年"
            p.level = 0

# 继续修改其他页...

# 5. 保存
prs.save('output.pptx')
```

#### 更简单的方法：直接修改文本（推荐）

```python
from pptx import Presentation

# 加载模板
prs = Presentation('skills_storage/pptx/temple/附件2：进门_转正答辩PPT模板.pptx')

# 定义每页要修改的内容
content_map = {
    0: {  # 第1页 - 封面
        "title": "杨柳公司汇报",
        "subtitle": "2024年度工作总结"
    },
    1: {  # 第2页
        "title": "公司概况",
        "content": ["公司名称：杨柳有限公司", "成立时间：2010年", "员工人数：200+"]
    },
    2: {  # 第3页
        "title": "主要业务",
        "content": ["技术研发", "市场营销", "咨询服务"]
    },
    3: {  # 第4页
        "title": "发展展望",
        "content": ["扩大市场份额", "拓展国际业务", "技术创新"]
    }
}

# 只保留前4页，删除其他
total_slides = len(prs.slides)
for i in range(total_slides - 1, 3, -1):  # 从后往前删除
    rId = prs.slides._sldIdLst[i].rId
    prs.part.drop_rel(rId)
    del prs.slides._sldIdLst[i]

# 修改每页内容
for slide_idx, content in content_map.items():
    slide = prs.slides[slide_idx]
    
    # 遍历形状，根据位置和类型识别并修改
    for shape in slide.shapes:
        if not hasattr(shape, "text_frame"):
            continue
        
        # 根据形状的位置和大小判断是标题还是内容
        # 通常标题在上方且字体较大
        if shape.top < 1500000:  # 顶部区域，可能是标题
            if "title" in content:
                shape.text = content["title"]
        else:  # 内容区域
            if "content" in content:
                tf = shape.text_frame
                tf.clear()
                for i, text in enumerate(content["content"]):
                    if i == 0:
                        tf.text = "• " + text
                    else:
                        p = tf.add_paragraph()
                        p.text = "• " + text
                        p.level = 0

prs.save('output.pptx')
print("✅ PPT 已生成，保留了模板的背景和 logo")
```

**关键点**：
- ✅ 使用 `Presentation(template_path)` 加载模板
- ✅ 删除不需要的幻灯片（而不是创建新幻灯片）
- ✅ 只修改 `text` 属性，不改变形状、背景、logo
- ✅ 保存时，所有设计元素（背景、logo、配色）都会保留

### 场景 2：从头创建自定义 PPT

1. **确认需求**：
   - 主题是什么？
   - 需要几页？
   - 每页包含什么内容？

2. **生成代码**：
   ```python
   from pptx import Presentation
   from pptx.util import Inches, Pt
   
   prs = Presentation()
   
   # 第1页：标题页
   slide1 = prs.slides.add_slide(prs.slide_layouts[0])
   slide1.shapes.title.text = "主标题"
   slide1.placeholders[1].text = "副标题"
   
   # 第2页：内容页
   slide2 = prs.slides.add_slide(prs.slide_layouts[1])
   slide2.shapes.title.text = "内容标题"
   content = slide2.placeholders[1].text_frame
   content.text = "要点 1"
   p = content.add_paragraph()
   p.text = "要点 2"
   p.level = 1
   
   prs.save('output.pptx')
   ```

## 重要说明

### ⚠️ 使用模板的关键规则（必须遵守）

**使用模板时的代码必须遵循以下模式：**

```python
from pptx import Presentation

# ✅ 正确：加载模板（这样会保留背景、logo、所有设计）
prs = Presentation('skills_storage/pptx/temple/附件2：进门_转正答辩PPT模板.pptx')

# ❌ 错误：创建空白演示（这样会丢失所有设计）
# prs = Presentation()  # 永远不要这样做！

# ❌ 错误：添加新幻灯片（会丢失模板设计）
# slide = prs.slides.add_slide(layout)  # 不要添加新幻灯片！

# ✅ 正确：使用模板现有的幻灯片，删除不需要的
# 从后往前删除多余的幻灯片
for i in range(len(prs.slides) - 1, 3, -1):  # 保留前4页
    rId = prs.slides._sldIdLst[i].rId
    prs.part.drop_rel(rId)
    del prs.slides._sldIdLst[i]

# ✅ 正确：只修改文本，不修改形状
for slide in prs.slides:
    for shape in slide.shapes:
        if hasattr(shape, "text_frame"):
            shape.text = "新内容"  # 只修改文本

prs.save('output.pptx')  # 保存时会保留所有设计
```

### 其他说明

1. **生成完整可执行代码**：
   - 不要只给步骤，要给完整的 Python 代码
   - 代码中包含所有必要的导入语句
   - 包含正确的文件路径

2. **路径规范**：
   - 模板路径：`skills_storage/pptx/temple/附件2：进门_转正答辩PPT模板.pptx`
   - 输出文件：在当前目录创建，文件名根据用户需求命名

3. **错误处理**：
   ```python
   import os
   
   template_path = 'skills_storage/pptx/temple/附件2：进门_转正答辩PPT模板.pptx'
   if not os.path.exists(template_path):
       print(f"错误：找不到模板文件 {template_path}")
   else:
       # 继续处理
       prs = Presentation(template_path)
   ```

4. **用户体验**：
   - 代码要简洁清晰
   - 添加注释说明关键步骤
   - 提供执行结果的预期说明

## 依赖安装

```bash
pip install python-pptx
```

## 常见场景模板

### 个人汇报 PPT（使用模板）

```python
from pptx import Presentation

# 加载模板
prs = Presentation('skills_storage/pptx/temple/附件2：进门_转正答辩PPT模板.pptx')

# 根据模板结构修改内容
# 注意：实际的 shape 索引需要根据模板结构调整
slides_content = [
    {"slide": 0, "shapes": {0: "个人工作汇报", 1: "汇报人：XXX"}},
    {"slide": 1, "shapes": {0: "工作概述", 1: "主要工作内容..."}},
]

for slide_info in slides_content:
    slide = prs.slides[slide_info["slide"]]
    for shape_idx, text in slide_info["shapes"].items():
        if shape_idx < len(slide.shapes):
            if hasattr(slide.shapes[shape_idx], "text"):
                slide.shapes[shape_idx].text = text

prs.save('个人汇报.pptx')
print("✅ PPT 已生成：个人汇报.pptx")
```

### 简单介绍 PPT（从头创建）

```python
from pptx import Presentation
from pptx.util import Pt

prs = Presentation()

# 封面
title_slide = prs.slides.add_slide(prs.slide_layouts[0])
title_slide.shapes.title.text = "主题介绍"
title_slide.placeholders[1].text = "副标题"

# 内容页
content_slide = prs.slides.add_slide(prs.slide_layouts[1])
content_slide.shapes.title.text = "要点介绍"
tf = content_slide.placeholders[1].text_frame
tf.text = "第一个要点"

for point in ["第二个要点", "第三个要点"]:
    p = tf.add_paragraph()
    p.text = point
    p.level = 1

prs.save('介绍.pptx')
print("✅ PPT 已生成：介绍.pptx")
```
