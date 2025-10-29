"""
固定的 PPT 生成脚本
AI 只需要提供 JSON 数据，这个脚本负责生成PPT
支持可选的logo添加功能（仅用于公司汇报类PPT）
"""
import json
import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt

def add_logo_to_slide(slide, logo_path):
    """在幻灯片右上角添加logo"""
    if os.path.exists(logo_path):
        # 添加logo到右上角
        # 位置：距离左边缘 11.5 英寸，距离顶部 0.3 英寸
        # 大小：1.5 x 1 英寸
        slide.shapes.add_picture(
            logo_path,
            left=Inches(11.5),
            top=Inches(0.3),
            width=Inches(1.5),
            height=Inches(1)
        )

def generate_ppt_from_json(json_file, add_logo=False):
    """从 JSON 数据生成 PPT
    
    参数:
        json_file: JSON数据文件路径
        add_logo: 是否添加logo（仅公司汇报类PPT需要）
    """
    # 读取 JSON 数据
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 创建新的演示文稿
    prs = Presentation()
    
    # 设置幻灯片尺寸为16:9
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)
    
    # logo路径（相对于脚本所在目录）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(script_dir, 'temple', 'logo1.png')
    
    if add_logo:
        print("[OK] 创建公司汇报PPT（带logo）")
    else:
        print("[OK] 创建普通PPT（不带logo）")
    
    # 第1页 - 封面
    if len(data['slides']) > 0:
        slide_data = data['slides'][0]
        slide = prs.slides.add_slide(prs.slide_layouts[0])  # 标题幻灯片布局
        
        # 添加标题
        title = slide.shapes.title
        title.text = slide_data.get('title', '标题')
        title.text_frame.paragraphs[0].font.size = Pt(44)
        title.text_frame.paragraphs[0].font.bold = True
        
        # 添加副标题
        if len(slide.placeholders) > 1:
            subtitle = slide.placeholders[1]
            subtitle.text = slide_data.get('subtitle', '')
            subtitle.text_frame.paragraphs[0].font.size = Pt(28)
        
        # 仅公司汇报类添加logo
        if add_logo:
            add_logo_to_slide(slide, logo_path)
    
    # 第2页 - 内容页
    if len(data['slides']) > 1:
        slide_data = data['slides'][1]
        slide = prs.slides.add_slide(prs.slide_layouts[1])  # 标题和内容布局
        
        # 添加标题
        title = slide.shapes.title
        title.text = slide_data.get('title', '内容')
        title.text_frame.paragraphs[0].font.size = Pt(36)
        title.text_frame.paragraphs[0].font.bold = True
        
        # 添加内容
        if len(slide.placeholders) > 1:
            content_placeholder = slide.placeholders[1]
            tf = content_placeholder.text_frame
            tf.clear()
            
            for i, item in enumerate(slide_data.get('content', [])):
                if i == 0:
                    tf.text = f"• {item}"
                else:
                    p = tf.add_paragraph()
                    p.text = f"• {item}"
                    p.level = 0
                    p.font.size = Pt(18)
        
        # 仅公司汇报类添加logo
        if add_logo:
            add_logo_to_slide(slide, logo_path)
    
    # 第3页 - 内容页
    if len(data['slides']) > 2:
        slide_data = data['slides'][2]
        slide = prs.slides.add_slide(prs.slide_layouts[1])  # 标题和内容布局
        
        # 添加标题
        title = slide.shapes.title
        title.text = slide_data.get('title', '内容')
        title.text_frame.paragraphs[0].font.size = Pt(36)
        title.text_frame.paragraphs[0].font.bold = True
        
        # 添加内容
        if len(slide.placeholders) > 1:
            content_placeholder = slide.placeholders[1]
            tf = content_placeholder.text_frame
            tf.clear()
            
            for i, item in enumerate(slide_data.get('content', [])):
                if i == 0:
                    tf.text = f"• {item}"
                else:
                    p = tf.add_paragraph()
                    p.text = f"• {item}"
                    p.level = 0
                    p.font.size = Pt(18)
        
        # 仅公司汇报类添加logo
        if add_logo:
            add_logo_to_slide(slide, logo_path)
    
    # 保存
    output_file = data.get('output_file', 'output.pptx')
    prs.save(output_file)
    print(f"[SUCCESS] PPT 已生成：{output_file}")
    if add_logo:
        print(f"[INFO] 共 {len(prs.slides)} 页，每页右上角都有公司logo")
    else:
        print(f"[INFO] 共 {len(prs.slides)} 页，普通PPT（不带logo）")
    return output_file

if __name__ == "__main__":
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        # 检查是否有 --add-logo 参数
        add_logo = '--add-logo' in sys.argv
        generate_ppt_from_json(json_file, add_logo)
    else:
        print("用法: python generate_ppt_from_json.py data.json [--add-logo]")
        print("  --add-logo: 仅用于公司汇报类PPT，在每页右上角添加logo")

