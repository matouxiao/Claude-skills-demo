# Claude Skills Clone - 通用技能管理框架

基于智谱AI GLM-4模型的通用技能管理框架，实现Claude-style的技能系统。

## 核心特性

- 🎯 **通用框架设计**：main.py完全通用，不包含业务逻辑
- 🧠 **SKILL.md驱动**：所有业务逻辑由SKILL.md指导AI完成
- 🔧 **Function Calling**：使用GLM-4的工具调用机制
- 📦 **模块化技能**：每个技能是独立的文件夹，易于扩展
- 💾 **缓存优化**：内存缓存技能元数据，提升性能
- 🚀 **易于扩展**：添加新技能无需修改代码

## PPT生成功能

支持两种PPT生成模式：
- 📊 **普通PPT**：适用于介绍、教学等非正式场合
- 🏢 **公司汇报PPT**：自动添加公司logo，适用于正式汇报
- 📄 **灵活页数**：支持任意页数（3页、5页、10页...）
- 🎨 **统一样式**：使用固定脚本保证PPT质量

<img width="1913" height="1042" alt="image" src="https://github.com/user-attachments/assets/d41acbfb-ccb3-4dfc-9a79-edfaec96b228" />

*生成的PPT示例可在项目文件夹中查看*

## 技术栈

- **后端**：FastAPI + Python 3.8+
- **AI模型**：智谱AI GLM-4.6
- **PPT生成**：python-pptx
- **前端**：原生HTML + JavaScript

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/claude-skills-clone.git
cd claude-skills-clone
```

### 2. 创建虚拟环境

```bash
# 使用 conda
conda create -n claude-skills python=3.8
conda activate claude-skills

# 或使用 venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

创建 `.env` 文件并添加智谱AI API密钥：

```env
ZHIPUAI_API_KEY=your_api_key_here
```

获取API密钥：[智谱AI开放平台](https://open.bigmodel.cn/)

## 使用方法

### 启动服务器

```bash
python main.py
```

服务器将在 `http://localhost:8000` 启动

### 访问前端界面

在浏览器中打开：
- 主页面：`http://localhost:8000`（需要单独打开 `index.html`）
- API文档：`http://localhost:8000/docs`

### 使用示例

#### 1. 生成普通PPT（无logo）

```
用户输入："帮我做个介绍深圳的PPT，要5页"
```

AI会：
1. 调用pptx技能
2. 根据SKILL.md的指导判断为"介绍类"
3. 生成JSON数据（5页）
4. 调用脚本生成PPT（不添加logo）

**结果**：生成5页的普通PPT，清爽简洁

#### 2. 生成公司汇报PPT（带logo）

```
用户输入："帮我做个2023年度公司绩效汇报"
```

AI会：
1. 调用pptx技能
2. 根据SKILL.md判断包含"公司汇报"关键词
3. 生成JSON数据
4. 调用脚本并添加 `--add-logo` 参数

**结果**：生成PPT，每页右上角都有公司logo

#### 3. 技能如何工作

```
用户请求 → AI调用 get_skill_content("pptx")
         → 读取 SKILL.md 的快速指南
         → 按照指南生成代码（填充JSON数据）
         → 调用 execute_python_code 执行
         → 生成 PPT 文件
```

**核心理念**：
- ✅ main.py = 通用框架（不含业务逻辑）
- ✅ SKILL.md = 业务大脑（告诉AI如何操作）
- ✅ AI = 执行者（严格遵循SKILL.md）

## 项目结构

```
claude-skills-clone/
├── main.py                          # 🔧 通用框架（不含业务逻辑）
├── index.html                       # 🌐 前端界面
├── requirements.txt                 # 📦 Python依赖
├── 架构说明.md                      # 📖 架构设计文档
├── 架构改进总结.md                  # 📊 改进历程
└── skills_storage/                  # 📁 技能仓库
    └── pptx/                        # 📊 PPT技能包（完整模块）
        ├── SKILL.md                 # 🧠 技能定义（AI的操作指南）
        ├── generate_ppt_from_json.py # ⚙️ PPT生成引擎
        ├── temple/                  # 🎨 资源文件夹
        │   └── logo1.png           # 🏢 公司logo
        └── scripts/                 # 🛠️ 辅助工具（可选）
```

**架构特点**：
- ✅ 每个技能是独立的文件夹（自包含）
- ✅ 添加新技能无需修改main.py
- ✅ 技能可以单独打包、分享、安装

## API 接口

### 对话接口

```http
POST /api/chat
Content-Type: application/json

{
  "message": "帮我做个介绍深圳的PPT"
}
```

### 技能管理

```http
# 上传技能
POST /api/skills/upload

# 列出所有技能
GET /api/skills

# 删除技能
DELETE /api/skills/{skill_name}
```

## 工作原理

### 技能系统架构

```
┌─────────────┐
│  用户请求    │
└──────┬──────┘
       ↓
┌─────────────────────────────┐
│  main.py (通用框架)          │
│  - 提供3个工具函数           │
│  - 不包含业务逻辑            │
└──────┬──────────────────────┘
       ↓
┌─────────────────────────────┐
│  AI (GLM-4.6)               │
│  1. list_skills_catalog()   │
│  2. get_skill_content()     │
│  3. execute_python_code()   │
└──────┬──────────────────────┘
       ↓
┌─────────────────────────────┐
│  SKILL.md (业务指南)         │
│  - 判断规则                  │
│  - 代码模板                  │
│  - 操作步骤                  │
└──────┬──────────────────────┘
       ↓
┌─────────────────────────────┐
│  生成代码 & 执行              │
│  → JSON数据                  │
│  → 调用脚本                  │
│  → 生成文件                  │
└─────────────────────────────┘
```

### PPT生成流程

**步骤1：技能匹配**
- AI调用 `list_skills_catalog()` 查看技能
- 发现pptx技能，调用 `get_skill_content("pptx")`

**步骤2：读取指南**
- 获取SKILL.md的完整内容
- 阅读"快速指南"部分

**步骤3：判断类型**

AI根据SKILL.md中的规则判断：

**公司汇报类**（添加logo）：
- "公司汇报"、"工作汇报"、"述职"
- "转正"、"晋升答辩"、"答辩"
- "季度汇报"、"年度总结"、"年终总结"
- "项目汇报"、"正式汇报"、"部门汇报"

**普通PPT**（不添加logo）：
- "介绍"、"教学"、"培训"等其他场景

**步骤4：生成代码**
- 使用SKILL.md提供的代码模板
- 填充JSON数据（包含用户需求的内容）
- 根据类型决定是否添加 `--add-logo`

**步骤5：执行生成**
- 调用 `execute_python_code()` 执行代码
- 代码调用 `skills_storage/pptx/generate_ppt_from_json.py`
- 生成PPT文件

## 配置说明

### 修改logo

将您的公司logo替换为：
```
skills_storage/pptx/temple/logo1.png
```

建议尺寸：1.5英寸 x 1英寸（约144x96像素）

### 自定义PPT样式

编辑 `skills_storage/pptx/generate_ppt_from_json.py` 中的样式设置：
- 字体大小：`Pt(44)`, `Pt(36)`, `Pt(18)`
- 幻灯片尺寸：`Inches(13.33)` x `Inches(7.5)` (16:9)
- Logo位置：`left=Inches(11.5)`, `top=Inches(0.3)`

### 添加新技能

创建新技能非常简单：

```bash
# 1. 创建技能文件夹
mkdir -p skills_storage/pdf

# 2. 创建SKILL.md（定义技能）
cat > skills_storage/pdf/SKILL.md << 'EOF'
---
name: pdf
description: "创建和编辑PDF文档"
---

# PDF文档生成

## 快速指南
当用户需要生成PDF时：
1. 判断文档类型
2. 提取内容
3. 使用代码模板生成...
EOF

# 3. 重启服务（AI会自动发现新技能）
python main.py
```

**无需修改main.py！**

## 常见问题

### 1. Windows下出现编码错误

项目已处理Windows GBK编码问题，所有输出使用ASCII字符。

### 2. PPT生成失败

检查：
- `skills_storage/pptx/temple/logo1.png` 是否存在
- 是否安装了 `python-pptx` 库
- 查看 `last_generated_code.py` 调试生成的代码

### 3. API密钥无效

确保在 `.env` 文件中设置了有效的智谱AI API密钥。

## 开发计划

### 已完成 ✅
- [x] 通用框架设计（main.py不含业务逻辑）
- [x] SKILL.md驱动的技能系统
- [x] 支持任意页数的PPT生成
- [x] 模块化技能包结构
- [x] 技能缓存优化

### 进行中 🚧
- [ ] 完善SKILL.md的指导内容
- [ ] 优化AI对SKILL.md的遵循度

### 计划中 📋
- [ ] 支持更多PPT模板
- [ ] 支持图片插入
- [ ] 支持表格和图表
- [ ] PDF生成技能
- [ ] Word文档生成技能
- [ ] 技能市场（分享和下载技能）
- [ ] 可视化的技能编辑器

### 架构优势

本项目的架构设计使得：
- ✅ 添加新功能只需创建新的SKILL.md
- ✅ 修改业务逻辑只需编辑SKILL.md
- ✅ 无需修改核心框架代码
- ✅ 技能可以独立开发、测试、分发

## 深入了解

想了解更多架构细节？查看以下文档：

- 📖 [架构说明.md](架构说明.md) - 完整的架构设计理念
- 📊 [架构改进总结.md](架构改进总结.md) - 架构演进历程
- 📝 [项目结构优化说明.md](项目结构优化说明.md) - 模块化重构说明
- 🐛 [PPT生成问题修复说明.md](PPT生成问题修复说明.md) - 问题排查指南

## 核心理念

> **main.py是框架，SKILL.md是大脑，AI是执行者**

这个架构的核心思想是：
- main.py提供基础能力（加载技能、调用AI、执行代码）
- SKILL.md告诉AI如何思考和操作
- AI根据SKILL.md的指导完成具体任务

优势：
- ✅ 符合开闭原则（对扩展开放，对修改关闭）
- ✅ 易于维护和测试
- ✅ 可以无限扩展技能
- ✅ 业务逻辑清晰集中

## 贡献

欢迎提交 Issue 和 Pull Request！

### 如何贡献新技能

1. Fork本项目
2. 在 `skills_storage/` 下创建新技能文件夹
3. 编写 `SKILL.md` 文件
4. 测试技能是否正常工作
5. 提交Pull Request

**注意**：添加新技能完全不需要修改main.py！

## 许可证

MIT License

## 联系方式

如有问题，请提交 Issue。

---

**⭐ 如果这个项目对你有帮助，请给个Star！**

