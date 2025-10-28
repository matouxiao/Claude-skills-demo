# Claude Skills Clone - PPT 生成系统

基于智谱AI GLM-4模型的技能管理和PPT自动生成系统。

## 功能特点

- 🎯 **智能技能路由**：基于用户需求自动匹配合适的技能
- 📊 **PPT自动生成**：支持两种PPT生成模式
  - **普通PPT**：适用于介绍、教学等非正式场合
  - **公司汇报PPT**：自动添加公司logo，适用于正式汇报
- 🔧 **工具调用机制**：使用GLM-4的function calling功能
- 📁 **技能管理**：上传、管理、删除自定义技能
- 💾 **缓存优化**：内存缓存技能元数据，提升性能

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

#### 1. 生成普通PPT

```
用户输入："帮我做个介绍深圳的PPT"
```

系统会生成一个3页的PPT，不带公司logo。

#### 2. 生成公司汇报PPT（带logo）

```
用户输入："帮我做个2023年度公司绩效汇报"
```

系统会：
1. 识别"公司汇报"关键词
2. 生成3页PPT
3. 在每页右上角添加 `logo1.png`

#### 3. 上传自定义技能

将包含 `SKILL.md` 的文件夹上传到系统，例如：

```
pptx/
  ├── SKILL.md          # 技能定义文件
  ├── temple/           # 资源文件夹
  │   └── logo1.png
  └── scripts/          # 辅助脚本
```

## 项目结构

```
claude-skills-clone/
├── main.py                      # 后端主程序
├── index.html                   # 前端界面
├── generate_ppt_from_json.py    # PPT生成脚本
├── requirements.txt             # Python依赖
├── function-calling.md          # 工具调用文档
├── skills_storage/              # 技能存储目录
│   └── pptx/                   # PPT生成技能
│       ├── SKILL.md            # 技能定义
│       └── temple/             # 模板资源
│           └── logo1.png       # 公司logo
└── example_skills/              # 示例技能（可选）
```

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

## PPT生成逻辑

### 判断规则

系统通过关键词判断是否生成公司汇报类PPT：

**公司汇报关键词**（会添加logo）：
- "公司汇报"、"工作汇报"、"述职"
- "转正"、"晋升答辩"、"答辩"
- "季度汇报"、"年度总结"、"年终总结"
- "项目汇报"、"正式汇报"、"部门汇报"

**普通PPT**（不添加logo）：
- "介绍"、"教学"、"培训"等其他场景

### 生成流程

1. 用户发送请求
2. 后端识别是否为PPT生成请求
3. 调用AI提取内容为JSON格式
4. 判断是否为公司汇报类
5. 调用 `generate_ppt_from_json.py` 生成PPT
6. 返回生成结果

## 配置说明

### 修改logo

将您的公司logo替换为：
```
skills_storage/pptx/temple/logo1.png
```

建议尺寸：1.5英寸 x 1英寸（约144x96像素）

### 自定义PPT样式

编辑 `generate_ppt_from_json.py` 中的样式设置：
- 字体大小：`Pt(44)`, `Pt(36)`, `Pt(18)`
- 幻灯片尺寸：`Inches(13.33)` x `Inches(7.5)` (16:9)
- Logo位置：`left=Inches(11.5)`, `top=Inches(0.3)`

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

- [ ] 支持更多PPT模板
- [ ] 支持自定义页数
- [ ] 支持图片插入
- [ ] 支持表格和图表
- [ ] 多技能串联支持

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

如有问题，请提交 Issue。

