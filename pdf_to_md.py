import os
import fitz  # PyMuPDF
from openai import OpenAI
from dotenv import load_dotenv
import argparse
import logging
import re

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 加载环境变量
load_dotenv()

# 获取API密钥
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    logging.error("DEEPSEEK_API_KEY未在.env文件或环境变量中找到。")
    exit(1)

# 初始化API客户端
try:
    # DeepSeek API与OpenAI兼容
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com/v1",
    )
except Exception as e:
    logging.error(f"初始化API客户端失败: {e}")
    exit(1)


def extract_text_from_pdf(pdf_path: str) -> str:
    """从PDF文件中提取文本内容"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        doc.close()
        logging.info(f"成功从{pdf_path}提取文本")
        # 基本清理：移除多余的换行符
        text = '\n'.join([line.strip() for line in text.splitlines() if line.strip()])
        return text
    except Exception as e:
        logging.error(f"从{pdf_path}提取文本时出错: {e}")
        return ""

def fix_math_formula(formula):
    """
    修复数学公式中的常见问题
    """
    # 移除不必要的空格
    formula = formula.strip()
    
    # 修复常见的LaTeX命令
    latex_fixes = {
        '\\text{': '\\text{',  # 确保text命令正确
        '\\mathbf{': '\\mathbf{',  # 粗体数学符号
        '\\mathit{': '\\mathit{',  # 斜体数学符号
        '\\mathrm{': '\\mathrm{',  # 罗马体数学符号
    }
    
    for wrong, correct in latex_fixes.items():
        formula = formula.replace(wrong, correct)
    
    # 修复常见的矩阵环境
    formula = formula.replace('\\begin{matrix}', '\\begin{pmatrix}').replace('\\end{matrix}', '\\end{pmatrix}')
    
    # 确保公式有正确的格式
    return f'$${formula}$$'

def post_process_markdown(content):
    """
    对生成的Markdown内容进行后处理，使其与Obsidian兼容
    """
    if not content:
        return ""

    # 移除可能包含的介绍性短语
    intro_patterns = [
        r'^Here is the markdown content:[\s\n]*',
        r'^The Markdown content is:[\s\n]*',
        r'^The converted markdown is:[\s\n]*',
        r'^I have converted the PDF to markdown:[\s\n]*',
        r'^Here\'s the extracted content in markdown:[\s\n]*',
        r'^Below is the markdown version:[\s\n]*',
        r'^The academic paper in markdown format:[\s\n]*',
    ]
    for pattern in intro_patterns:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)

    # 1. 增强的代码块清理
    # 首先移除所有明确的markdown代码块标记
    content = re.sub(r'```markdown\s*', '', content)
    content = re.sub(r'```md\s*', '', content)
    
    # 处理嵌套代码块和各种语言代码块
    code_block_start_pattern = r'```[a-zA-Z0-9_+#-]*\s*'
    
    # 多次递归处理代码块嵌套问题
    max_iterations = 5  # 防止无限循环
    iteration = 0
    
    while '```' in content and iteration < max_iterations:
        # 移除所有代码块开始标记（带或不带语言标识符）
        content = re.sub(code_block_start_pattern, '', content)
        # 移除所有代码块结束标记
        content = re.sub(r'```\s*', '', content)
        iteration += 1
    
    # 2. 增强的数学公式处理
    # 标准化数学公式分隔符间距
    content = re.sub(r'(?<!\$)\$\$(?!\$)', '\n$$\n', content)  # 为块级公式确保前后有换行
    content = re.sub(r'(?<!\$)\$(?!\$)', ' $ ', content)     # 为行内公式添加空格
    
    # 处理块级公式：确保使用$$ ... $$格式并且独立成行
    def replace_block_math(match):
        formula = match.group(1).strip()
        return f'\n$$\n{formula}\n$$\n'
    
    content = re.sub(r'\$\$(.*?)\$\$', replace_block_math, content, flags=re.DOTALL)
    
    # 处理行内公式：确保使用$ ... $格式并有适当的空格
    def replace_inline_math(match):
        formula = match.group(1).strip()
        # 行内公式保持使用单个$并确保两侧有空格
        return f' ${formula}$ '
    
    content = re.sub(r'\$(.*?)\$', replace_inline_math, content)
    
    # 3. 处理LaTeX常见错误
    # 修复常见的LaTeX命令错误
    latex_errors = {
        r'\\frac\{([^{}]*)\}\{([^{}]*)\}': r'\\frac{\1}{\2}',  # 修复错误的大括号
        r'\\sum\_': r'\\sum_',  # 修复下标符号
        r'\\int\_': r'\\int_',  # 修复积分下限
        r'\\text\{([^{}]*)\}': r'\\text{\1}',  # 修复text命令
    }
    
    for error_pattern, correction in latex_errors.items():
        content = re.sub(error_pattern, correction, content)
    
    # 4. 保留必要的换行符
    # 在标题前后添加换行
    content = re.sub(r'([^\n])#', r'\1\n#', content)  # 确保标题前有换行
    content = re.sub(r'(#{1,6}\s+[^\n]+)([^\n])', r'\1\n\2', content)  # 确保标题后有换行
    
    # 确保列表项有正确的换行
    content = re.sub(r'([^\n])([\*\-\+]\s+)', r'\1\n\2', content)  # 确保列表项前有换行
    
    # 确保段落之间有空行
    content = re.sub(r'\.([A-Z])', r'.\n\n\1', content)  # 在句号后跟大写字母处添加空行
    
    # 5. 规范化空格，但保留换行
    content = re.sub(r' {2,}', ' ', content)  # 将连续2个以上空格替换为1个
    
    # 6. 保护公式中的换行
    # 首先标记所有公式
    content = re.sub(r'\$\$(.*?)\$\$', lambda m: f'$$FORMULA_START$${m.group(1)}$$FORMULA_END$$', content, flags=re.DOTALL)
    
    # 清理多余的空行，但保持基本结构
    content = re.sub(r'\n{4,}', '\n\n\n', content)  # 最多保留三个连续换行
    
    # 恢复公式标记
    content = content.replace('$$FORMULA_START$$', '$$').replace('$$FORMULA_END$$', '$$')
    
    # 7. 最终检查是否还有代码块标记残留
    if '```' in content:
        print("警告: post_process_markdown 清理后仍有代码块标记残留")
        # 尝试最后的强制清理
        content = content.replace('```', '')
    
    return content

def convert_to_markdown(text: str, model_name: str = "deepseek-chat", chinese: bool = False) -> str:
    """将文本转换为Markdown格式，可选中文输出"""
    if not text:
        logging.warning("转换的输入文本为空。")
        return "错误：输入文本为空。"

    logging.info(f"正在发送文本(长度: {len(text)})到DeepSeek模型: {model_name}进行Markdown转换。")

    # 对于长文本，可能需要分段处理
    max_chunk_size = 25000
    
    if chinese and len(text) > max_chunk_size:
        logging.info("文本较长，将使用分段翻译处理...")
        # 分段处理
        chunks = []
        for i in range(0, len(text), max_chunk_size):
            chunk = text[i:i + max_chunk_size]
            chunks.append(chunk)
        
        results = []
        for i, chunk in enumerate(chunks):
            logging.info(f"处理第 {i+1}/{len(chunks)} 段内容...")
            chunk_result = _process_chunk(chunk, model_name, chinese, is_first=(i==0))
            if chunk_result.startswith("错误:"):
                return chunk_result  # 如果有错误，立即退出
            results.append(chunk_result)
        
        # 合并结果
        markdown_content = "\n".join(results)
        return markdown_content
    else:
        # 单次处理全文
        return _process_chunk(text, model_name, chinese)

def _process_chunk(text: str, model_name: str, chinese: bool, is_first: bool = True) -> str:
    """处理单个文本块的翻译/转换"""
    # 根据语言选择不同的提示词
    if chinese:
        # 第一段需要处理标题等，非第一段则侧重于连续翻译
        if is_first:
            prompt_message = f"""请将以下学术论文片段完整翻译为中文，并保持Markdown格式：

文章内容：
---
{text[:25000]} 
---

核心要求：
1. 完整翻译所提供的文本，不要省略或总结任何内容
2. 保持原论文的结构、章节和段落
3. 所有数学公式保持原样，仅翻译周围的文字
4. 表格、图表和引用都需完整翻译

格式要求：
1. 使用标准Markdown格式（标题用#，列表用-，等）
2. 行内公式用单$包围，块级公式用$$包围并独立成行
3. 不要使用```markdown包裹内容
4. 直接输出翻译结果，不要添加任何注释或说明

严禁：
1. 不要添加"未完待续"、"篇幅限制"等任何解释或注释
2. 不要说明哪些内容未被翻译
3. 不要总结，必须完整翻译提供的全部内容"""
        else:
            prompt_message = f"""请将以下学术论文片段完整翻译为中文，这是论文的续段：

文章内容：
---
{text[:25000]} 
---

核心要求：
1. 这是上一段翻译的继续，请直接翻译，不要重复标题或前言
2. 完整翻译所提供的全部内容，不要省略或总结
3. 保持原论文的结构和段落
4. 所有数学公式保持原样，仅翻译周围的文字

格式要求：
1. 使用标准Markdown格式
2. 行内公式用单$包围，块级公式用$$包围并独立成行
3. 不要使用```markdown包裹内容
4. 直接输出翻译结果，不要添加任何注释或说明

严禁：
1. 不要添加"未完待续"、"篇幅限制"等任何解释或注释
2. 不要提及这是部分翻译
3. 必须完整翻译提供的全部内容，不要缩略或总结"""
    else:
        prompt_message = f"""请将以下学术论文内容转换为精确的Markdown格式，特别优化为在Obsidian中正确显示。保持原文的所有内容和结构，不做简化或删减。
        
文章内容：
---
{text[:25000]} 
---

格式要求：
1. 直接输出Markdown内容，不要使用```或任何标记包裹
2. 不要添加介绍性文字，如"以下是转换后的内容"等
3. 使用标准Markdown格式（标题用#，列表用-，等）
4. 对重要内容进行适当的强调（如**粗体**或*斜体*）

数学公式渲染规则：
1. 行内公式：使用单个$符号包围，如：$a = b + c$
2. 块级公式：使用双$$符号包围并独立成行
3. 将复杂的LaTeX命令原样保留，确保在MathJax环境中能正确渲染"""

    try:
        # 为中文翻译使用不同的系统提示
        if chinese:
            system_content = """You are an expert academic translator. Your task is to translate English academic papers to Chinese completely. Rules:
1. Translate the ENTIRE content without any omissions or summaries
2. Preserve all mathematical formulas exactly as they appear
3. NEVER add any disclaimers about content being truncated or incomplete
4. Do not add any notes or comments about translation status
5. Format properly in Markdown
6. NEVER mention that this is a partial translation, even if the content seems incomplete
7. Just translate what is provided completely without any additional commentary"""
        else:
            system_content = "You are an expert at converting academic papers to Markdown format optimized for Obsidian. VERY IMPORTANT: Do NOT wrap your output in ```markdown and ``` tags, just output pure Markdown content directly. Also do NOT include any introductory text."
        
        # 使用API调用
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": prompt_message},
            ],
            max_tokens=8000,  # 增加token限制以确保完整转换
            temperature=0.2,   # 降低温度以确保更精确的转换
        )
        
        # 提取结果
        if response.choices and response.choices[0].message:
            markdown_content = response.choices[0].message.content
            # 清理可能的注释文字
            if chinese:
                # 移除模型可能添加的注释
                notes_patterns = [
                    r'[\(（]?注[:：].*[\)）]?\n',
                    r'[\(（]?译者注[:：].*[\)）]?\n',
                    r'（?此处省略.*）?',
                    r'（?篇幅限制.*）?',
                    r'（?内容太长.*）?',
                    r'.*未完待续.*',
                    r'.*部分翻译.*',
                    r'.*完整论文.*',
                    r'.*注意：.*',
                ]
                for pattern in notes_patterns:
                    markdown_content = re.sub(pattern, '', markdown_content, flags=re.IGNORECASE)
            
            logging.info("成功获取转换结果")
            return markdown_content.strip()
        else:
            logging.error(f"API响应格式异常: {response}")
            return "错误：无法获取有效的转换结果。"

    except Exception as e:
        logging.error(f"调用API时出错: {e}")
        return f"错误：API调用失败 - {e}"

def save_markdown(content: str, output_path: str):
    """保存Markdown内容到文件，添加后处理步骤改善公式渲染"""
    try:
        # 应用后处理来优化数学公式
        processed_content = post_process_markdown(content)
        
        # 确认最终生成的内容不含有```markdown和```
        if "```markdown" in processed_content or processed_content.rstrip().endswith("```"):
            logging.warning("后处理后仍然检测到代码块标记，尝试再次清理...")
            processed_content = processed_content.replace("```markdown", "").replace("```", "")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)
        logging.info(f"Markdown内容已成功保存到{output_path}")
    except Exception as e:
        logging.error(f"保存Markdown到{output_path}时出错: {e}")

def main():
    parser = argparse.ArgumentParser(description="将Arxiv PDF论文转换为Markdown格式")
    parser.add_argument("pdf_path", help="输入PDF文件的路径")
    parser.add_argument("-o", "--output", help="输出Markdown文件的路径（可选）。默认为Markdown/<pdf_name>.md")
    parser.add_argument("-m", "--model", default="deepseek-chat", help="使用的DeepSeek模型（例如，deepseek-chat）。默认为deepseek-chat。")
    parser.add_argument("--chinese", action="store_true", help="中文模式：将文章翻译为中文并保持Markdown格式")
    
    args = parser.parse_args()

    pdf_path = args.pdf_path
    model_name = args.model
    output_path_arg = args.output
    chinese_mode = args.chinese

    # 确定输出路径
    if output_path_arg:
        output_path = output_path_arg
    else:
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_dir = "Markdown"  # 创建与Summaries同级的Markdown目录
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{base_name}.md")
        # 如果是中文模式，在文件名中添加cn标识
        if chinese_mode:
            output_path = os.path.join(output_dir, f"{base_name}_cn.md")

    # 工作流
    logging.info(f"开始处理: {pdf_path}")
    paper_text = extract_text_from_pdf(pdf_path)

    if not paper_text:
        logging.error("提取文本失败，退出。")
        return

    markdown_content = convert_to_markdown(paper_text, model_name=model_name, chinese=chinese_mode)

    if not markdown_content.startswith("错误:"):
        # 对于中文版本，简化后处理步骤，仅移除可能的代码块标记
        if chinese_mode:
            # 简单清理，只移除可能的```markdown和```标记
            if "```markdown" in markdown_content or "```" in markdown_content:
                markdown_content = markdown_content.replace("```markdown", "").replace("```", "")
            # 移除介绍性文本
            intro_patterns = [
                r'^以下是中文版本.*?\n',
                r'^这是该论文的中文翻译.*?\n',
                r'^论文的中文Markdown版本.*?\n',
            ]
            for pattern in intro_patterns:
                markdown_content = re.sub(pattern, '', markdown_content, flags=re.IGNORECASE)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
        else:
            # 原始英文版本使用完整的后处理步骤
            save_markdown(markdown_content, output_path)
        
        logging.info(f"Markdown内容已成功保存到{output_path}")
    else:
        logging.error("Markdown转换失败。查看日志获取详细信息。")


if __name__ == "__main__":
    main() 