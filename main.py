"""
Claude Skills Clone - 使用国产大模型
后端主程序 (main.py)

依赖安装:
pip install fastapi uvicorn python-multipart pyyaml zhipuai python-dotenv
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import re
import yaml
import json
from pathlib import Path
from zhipuai import ZhipuAI
from dotenv import load_dotenv
from typing import Dict

# 加载环境变量
load_dotenv()

app = FastAPI(title="Claude Skills Clone API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置
SKILLS_DIR = Path("skills_storage")
SKILLS_DIR.mkdir(exist_ok=True)

# 全局缓存：name -> metadata(dict: name, description, tags, content, file_path)
SKILLS_CACHE: Dict[str, dict] = {}

def load_skills_cache(force: bool = False) -> Dict[str, dict]:
    """加载/重建 skills 缓存。
    返回: name -> metadata
    """
    global SKILLS_CACHE
    if SKILLS_CACHE and not force:
        return SKILLS_CACHE
    cache: Dict[str, dict] = {}
    for skill_file in SKILLS_DIR.rglob("SKILL.md"):
        metadata = parse_skill_file(skill_file)
        if metadata and metadata.get('name'):
            cache[metadata['name']] = metadata
    SKILLS_CACHE = cache
    return SKILLS_CACHE

def add_or_update_skill(metadata: dict) -> None:
    """加入或更新单个 skill 到缓存。"""
    if metadata and metadata.get('name'):
        SKILLS_CACHE[metadata['name']] = metadata

def remove_skill_from_cache(skill_name: str) -> None:
    """从缓存中移除一个 skill。"""
    if skill_name in SKILLS_CACHE:
        del SKILLS_CACHE[skill_name]

# 初始化智谱AI客户端
client = ZhipuAI(api_key=os.getenv("ZHIPUAI_API_KEY", "your-api-key-here"))

# ==================== 数据模型 ====================

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    skills_used: List[str]
    model: str

class SkillMetadata(BaseModel):
    name: str
    description: str
    tags: Optional[List[str]] = []
    file_path: str

# ==================== Skills 管理 ====================

def parse_skill_file(file_path: Path) -> Optional[dict]:
    """解析 SKILL.md 文件的 YAML frontmatter"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有 YAML frontmatter
        if not content.startswith('---'):
            return None
        
        # 提取 YAML 部分
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None
        
        yaml_content = parts[1]
        markdown_content = parts[2].strip()
        
        # 解析 YAML
        metadata = yaml.safe_load(yaml_content)
        metadata['content'] = markdown_content
        metadata['file_path'] = str(file_path)
        
        return metadata
    except Exception as e:
        print(f"Error parsing skill file {file_path}: {e}")
        return None

def get_all_skills() -> List[dict]:
    """获取所有 skills 的元数据（基于缓存）"""
    if not SKILLS_CACHE:
        load_skills_cache(force=False)
    return list(SKILLS_CACHE.values())

def get_skill_by_name(skill_name: str) -> Optional[dict]:
    if not SKILLS_CACHE:
        load_skills_cache(force=False)
    return SKILLS_CACHE.get(skill_name)

def build_lightweight_skills_prompt() -> str:
    """构建轻量级 skills 索引 prompt"""
    skills = get_all_skills()
    if not skills:
        return "当前没有可用的 skills。"
    
    prompt = "=== 可用的 Skills ===\n\n"
    for skill in skills:
        prompt += f"- **{skill['name']}**: {skill['description']}\n"
        if skill.get('tags'):
            prompt += f"  标签: {', '.join(skill['tags'])}\n"
    
    prompt += "\n请根据用户的问题,判断是否需要使用这些 skills。如果需要,请明确说明需要哪个 skill。"
    return prompt

def load_full_skill_content(skill_name: str) -> Optional[str]:
    """加载完整的 skill 内容（基于缓存）"""
    skill = get_skill_by_name(skill_name)
    return skill.get('content') if skill else None

# ==================== AI 调用 ====================

def call_glm4(messages: List[dict]) -> str:
    """调用智谱 GLM-4"""
    try:
        response = client.chat.completions.create(
            model="glm-4.6",
            messages=messages,
            temperature=0.7,
            max_tokens=7000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"模型调用失败: {str(e)}"

def _message_to_dict(msg_obj) -> dict:
    """将 SDK 返回的 message 转为可再次发送的 dict。"""
    # 兼容 zai/zhipuai SDK 的不同实现
    try:
        if hasattr(msg_obj, 'model_dump'):
            d = msg_obj.model_dump()
        elif hasattr(msg_obj, '__dict__'):
            d = dict(msg_obj.__dict__)
        else:
            # 尝试直接当作 dict 使用
            d = dict(msg_obj)
    except Exception:
        d = {"role": "assistant", "content": getattr(msg_obj, 'content', '')}

    # 规范必要字段
    role = d.get('role') or getattr(msg_obj, 'role', 'assistant')
    content = d.get('content', getattr(msg_obj, 'content', ''))
    tool_calls = d.get('tool_calls', getattr(msg_obj, 'tool_calls', None))
    out = {"role": role}
    if content is not None:
        out["content"] = content
    if tool_calls:
        # 尽量取简单可序列化结构
        try:
            out["tool_calls"] = json.loads(json.dumps(tool_calls, default=lambda o: getattr(o, '__dict__', str(o))))
        except Exception:
            out["tool_calls"] = tool_calls
    return out

def call_glm4_with_tools(messages: List[dict], tools: List[dict], max_tool_rounds: int = 6) -> dict:
    """开启函数调用（tools）的对话流程，自动处理 tool_calls。
    返回: {"answer": str, "skills_used": List[str], "model": str}
    """
    skills_used: List[str] = []
    working_msgs: List[dict] = list(messages)

    for _ in range(max_tool_rounds):
        resp = client.chat.completions.create(
            model="glm-4.6",
            messages=working_msgs,
            tools=tools,
            tool_choice="auto",
            temperature=0.7,
            max_tokens=7000,
        )
        assistant_msg = resp.choices[0].message
        assistant_msg_dict = _message_to_dict(assistant_msg)
        working_msgs.append(assistant_msg_dict)

        tool_calls = assistant_msg_dict.get('tool_calls')
        if not tool_calls:
            # 没有工具调用，认为模型已给出最终回答
            return {
                "answer": assistant_msg_dict.get('content', ''),
                "skills_used": skills_used,
                "model": "glm-4.6",
            }

        # 处理每个工具调用
        got_skill_content = False
        for tool_call in tool_calls:
            try:
                function_call = tool_call.get('function', {})
                func_name = function_call.get('name')
                args_json = function_call.get('arguments') or "{}"
                try:
                    args = json.loads(args_json) if isinstance(args_json, str) else args_json
                except Exception:
                    args = {}

                if func_name == 'list_skills_catalog':
                    # 仅返回 YAML 索引（不含 content）
                    catalog = [
                        {
                            "name": s.get('name'),
                            "description": s.get('description'),
                            "tags": s.get('tags', []),
                        }
                        for s in get_all_skills()
                    ]
                    tool_result = {"skills": catalog}
                elif func_name == 'get_skill_content':
                    name = (args or {}).get('name')
                    content = load_full_skill_content(name) or ""
                    if content:
                        skills_used = [name]  # 单技能
                        got_skill_content = True
                    tool_result = {"name": name, "content": content}
                elif func_name == 'execute_python_code':
                    code = (args or {}).get('code', '')
                    tool_result = execute_python_code(code)
                else:
                    tool_result = {"error": f"未知函数: {func_name}"}

                working_msgs.append({
                    "role": "tool",
                    "content": json.dumps(tool_result, ensure_ascii=False),
                    "tool_call_id": tool_call.get('id')
                })
            except Exception as tool_e:
                working_msgs.append({
                    "role": "tool",
                    "content": json.dumps({"error": str(tool_e)}, ensure_ascii=False),
                    "tool_call_id": tool_call.get('id') if isinstance(tool_call, dict) else None
                })
        
        # 如果获取了技能内容，添加提示引导模型使用 execute_python_code
        if got_skill_content:
            # 为 pptx 技能使用固定脚本+JSON数据方式
            if 'pptx' in skills_used:
                code_template = """import json

# 步骤1：创建 PPT 数据（JSON格式）
ppt_data = {
    "output_file": "【文件名】.pptx",
    "slides": [
        {
            "title": "【第1页主标题】",
            "subtitle": "【第1页副标题】"
        },
        {
            "title": "【第2页标题】",
            "content": [
                "【第2页第1点内容】",
                "【第2页第2点内容】",
                "【第2页第3点内容】"
            ]
        },
        {
            "title": "【第3页标题】",
            "content": [
                "【第3页第1点内容】",
                "【第3页第2点内容】",
                "【第3页第3点内容】"
            ]
        }
    ]
}

# 步骤2：保存为 JSON 文件
with open('ppt_data.json', 'w', encoding='utf-8') as f:
    json.dump(ppt_data, f, ensure_ascii=False, indent=2)

# 步骤3：使用固定脚本生成 PPT（保证正确使用模板）
import subprocess
import sys
result = subprocess.run([sys.executable, 'generate_ppt_from_json.py', 'ppt_data.json'], 
                       capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print("错误:", result.stderr)
"""
                working_msgs.append({
                    "role": "system",
                    "content": (
                        "【使用固定脚本生成PPT】\n\n"
                        "由于模型无法正确使用模板，现在改用固定脚本。\n"
                        "你只需要填充以下代码模板中【】的内容：\n\n"
                        f"```python\n{code_template}\n```\n\n"
                        "只替换【】中的内容，不要修改代码结构。\n"
                        "然后调用 execute_python_code 执行这段代码。"
                    )
                })
            else:
                working_msgs.append({
                    "role": "system",
                    "content": (
                        "你已获取技能的完整操作指南。\n\n"
                        "【重要说明】：\n"
                        "1. 对于生成文件的任务（如 PPT、PDF、文档等），请生成完整的 Python 代码\n"
                        "2. 然后调用 execute_python_code 工具执行这段代码，直接生成文件\n"
                        "3. 代码中应包含完整的文件路径、内容生成逻辑和错误处理\n"
                        "4. 根据用户的具体需求（主题、内容要点等）生成定制化的内容\n"
                        "5. 执行成功后，告诉用户文件已生成及文件名\n\n"
                        "现在，请严格按照指南生成代码并调用 execute_python_code 工具来完成任务。"
                    )
                })

    # 超过回合仍未给出最终回答
    return {
        "answer": "工具调用轮次耗尽，未得到最终回答。",
        "skills_used": skills_used,
        "model": "glm-4.6",
    }

def execute_python_code(code: str) -> dict:
    """在受限环境中执行 Python 代码，用于生成文件。
    返回: {"success": bool, "output": str, "error": str, "files_created": List[str]}
    """
    import subprocess
    import tempfile
    import sys
    
    try:
        # 保存生成的代码到文件，方便调试
        debug_code_file = 'last_generated_code.py'
        with open(debug_code_file, 'w', encoding='utf-8') as f:
            f.write(code)
        print(f"[DEBUG] 生成的代码已保存到: {debug_code_file}")
        
        # 创建临时 Python 文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        
        # 执行代码
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd()
        )
        
        # 清理临时文件
        try:
            os.unlink(temp_file)
        except:
            pass
        
        # 检查是否有生成的文件
        files_created = []
        output_patterns = ['.pptx', '.pdf', '.docx', '.html']
        for file in os.listdir('.'):
            if any(file.endswith(ext) for ext in output_patterns):
                files_created.append(file)
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr if result.returncode != 0 else "",
            "files_created": files_created
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": "代码执行超时（超过30秒）",
            "files_created": []
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e),
            "files_created": []
        }

def chat_with_skills(user_message: str) -> dict:
    """带 skills 的对话流程（函数调用版，单技能，未命中可直答）。"""
    # 定义工具
    tools = [
        {
            "type": "function",
            "function": {
                "name": "list_skills_catalog",
                "description": "列出可用的技能目录，仅包含 name/description/tags。",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_skill_content",
                "description": "根据技能名称获取其 SKILL.md 的正文内容。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "技能名称"}
                    },
                    "required": ["name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "execute_python_code",
                "description": "执行 Python 代码生成文件（如 PPT、PDF 等）。代码执行后返回输出和生成的文件列表。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "要执行的完整 Python 代码"
                        }
                    },
                    "required": ["code"]
                }
            }
        }
    ]

    # 提示：说明使用工具的策略
    system_prompt = (
        "你是一个有帮助的助手。\n"
        "如需判断技能，请先调用 list_skills_catalog 获取目录；匹配后再调用 get_skill_content(name) 读取正文；"
        "如果无需技能，可直接回答。始终只选择一个技能，不要串联多个技能。\n\n"
        "重要：当需要生成文件（如 PPT、PDF、文档等）时，使用 execute_python_code 工具直接执行代码并生成文件。"
        "不要只给用户代码让他们手动执行，而是调用 execute_python_code 自动生成文件。"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    # 预热缓存（如未加载）
    if not SKILLS_CACHE:
        load_skills_cache(force=False)

    result = call_glm4_with_tools(messages, tools)
    return result

# ==================== API 路由 ====================

@app.get("/")
async def root():
    return {"message": "Claude Skills Clone API", "status": "running"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """对话接口"""
    try:
        # 特殊处理：如果是生成PPT的请求，直接调用固定脚本
        if any(keyword in request.message for keyword in ["公司汇报", "工作汇报", "述职", "转正", "PPT", "ppt"]):
            result = handle_ppt_generation(request.message)
            return ChatResponse(**result)
        
        result = chat_with_skills(request.message)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def handle_ppt_generation(user_message: str) -> dict:
    """直接处理PPT生成请求，不使用AI生成代码"""
    import json
    import subprocess
    import sys
    
    # 判断是否为公司汇报类PPT
    company_report_keywords = [
        "公司汇报", "工作汇报", "述职",
        "转正", "晋升答辩", "答辩",
        "季度汇报", "年度总结", "年终总结",
        "项目汇报", "正式汇报", "部门汇报",
        "公司logo", "公司模板"
    ]
    
    is_company_report = any(keyword in user_message for keyword in company_report_keywords)
    
    # 使用AI提取内容
    prompt = f"""根据用户需求提取PPT内容，以JSON格式返回。

用户需求：{user_message}

请以JSON格式返回，格式如下（直接返回JSON，不要其他解释）：
{{
  "title": "主标题",
  "subtitle": "副标题",
  "slide2_title": "第2页标题",
  "slide2_content": ["第1点", "第2点", "第3点"],
  "slide3_title": "第3页标题",
  "slide3_content": ["第1点", "第2点", "第3点"]
}}"""
    
    # 调用AI提取内容
    response = client.chat.completions.create(
        model="glm-4.6",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    )
    
    content_text = response.choices[0].message.content.strip()
    
    # 尝试解析JSON
    try:
        # 清理可能的markdown代码块标记
        if "```json" in content_text:
            content_text = content_text.split("```json")[1].split("```")[0]
        elif "```" in content_text:
            content_text = content_text.split("```")[1].split("```")[0]
        
        content_data = json.loads(content_text.strip())
        
        # 构建PPT数据
        ppt_data = {
            "output_file": f"{content_data.get('title', '公司汇报')}.pptx",
            "slides": [
                {
                    "title": content_data.get("title", "公司汇报"),
                    "subtitle": content_data.get("subtitle", "工作总结")
                },
                {
                    "title": content_data.get("slide2_title", "概况"),
                    "content": content_data.get("slide2_content", ["内容1", "内容2"])
                },
                {
                    "title": content_data.get("slide3_title", "展望"),
                    "content": content_data.get("slide3_content", ["目标1", "目标2"])
                }
            ]
        }
        
        # 保存JSON
        with open('ppt_data.json', 'w', encoding='utf-8') as f:
            json.dump(ppt_data, f, ensure_ascii=False, indent=2)
        
        # 调用固定脚本生成PPT（公司汇报类添加 --add-logo 参数）
        cmd = [sys.executable, 'generate_ppt_from_json.py', 'ppt_data.json']
        if is_company_report:
            cmd.append('--add-logo')
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            ppt_type = "公司汇报PPT（带logo）" if is_company_report else "普通PPT"
            return {
                "answer": f"[成功] {ppt_type}已生成：{ppt_data['output_file']}\n\n{result.stdout}\n\n内容包括：\n1. {content_data.get('title', '标题')}\n2. {content_data.get('slide2_title', '第2页')}\n3. {content_data.get('slide3_title', '第3页')}",
                "skills_used": ["pptx"],
                "model": "glm-4.6"
            }
        else:
            return {
                "answer": f"PPT生成失败：{result.stderr}",
                "skills_used": ["pptx"],
                "model": "glm-4.6"
            }
    
    except Exception as e:
        return {
            "answer": f"处理失败：{str(e)}\n\n原始内容：{content_text}",
            "skills_used": ["pptx"],
            "model": "glm-4.6"
        }

@app.post("/api/skills/upload")
async def upload_skill(file: UploadFile = File(...), skill_name: Optional[str] = None):
    """上传 skill 文件"""
    try:
        # 只接受 .md 文件
        if not file.filename.endswith('.md'):
            raise HTTPException(status_code=400, detail="只支持 .md 文件")
        
        # 如果提供了 skill_name，使用它；否则从文件名提取
        if not skill_name:
            skill_name = file.filename.replace('.md', '')  # 从文件名提取skill名称
        
        # 清理 skill_name，移除特殊字符
        skill_name = re.sub(r'[<>:"/\\|?*]', '_', skill_name).strip()
        if not skill_name:
            raise HTTPException(status_code=400, detail="无效的 skill 名称")
        
        skill_dir = SKILLS_DIR / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = skill_dir / "SKILL.md"
        
        # 保存文件
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # 验证文件格式
        metadata = parse_skill_file(file_path)
        if not metadata:
            # 删除无效文件
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=400, detail="无效的 skill 文件格式,需要包含 YAML frontmatter")
        # 缓存更新
        add_or_update_skill(metadata)
        
        return {
            "message": "Skill 上传成功",
            "skill_name": metadata['name'],
            "description": metadata['description']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/skills")
async def list_skills():
    """获取所有 skills 列表"""
    try:
        skills = get_all_skills()
        return {
            "total": len(skills),
            "skills": skills
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/skills/{skill_name}")
async def delete_skill(skill_name: str):
    """删除指定 skill"""
    try:
        skill_dir = SKILLS_DIR / skill_name
        if not skill_dir.exists():
            raise HTTPException(status_code=404, detail="Skill 不存在")
        
        # 删除整个目录
        import shutil
        shutil.rmtree(skill_dir)
        # 同步缓存
        remove_skill_from_cache(skill_name)
        
        return {"message": f"Skill '{skill_name}' 已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 启动时预热缓存
@app.on_event("startup")
def _init_skills_cache():
    load_skills_cache(force=True)

# ==================== 启动配置 ====================

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("Claude Skills Clone 后端服务启动")
    print("=" * 50)
    print(f"Skills 存储目录: {SKILLS_DIR.absolute()}")
    print("API 文档地址: http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)