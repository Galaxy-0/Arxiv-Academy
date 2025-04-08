import os
import fitz  # PyMuPDF
# 使用OpenAI客户端连接DeepSeek API
from openai import OpenAI
from dotenv import load_dotenv
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    logging.error("DEEPSEEK_API_KEY not found in .env file or environment variables.")
    exit(1)

# 使用OpenAI客户端但连接到DeepSeek API
try:
    # DeepSeek API与OpenAI兼容，使用官方文档中的URL
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com/v1", # 官方文档确认的URL
    )
except Exception as e:
    logging.error(f"Failed to initialize API client: {e}")
    exit(1)


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extracts text content from a PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        doc.close()
        logging.info(f"Successfully extracted text from {pdf_path}")
        # Basic cleaning: remove excessive newlines
        text = '\n'.join([line.strip() for line in text.splitlines() if line.strip()])
        return text
    except Exception as e:
        logging.error(f"Error extracting text from {pdf_path}: {e}")
        return ""

def summarize_text_with_deepseek(text: str, model_name: str = "deepseek-chat") -> str:
    """Summarizes the text using the DeepSeek API and requests Chinese Markdown output."""
    if not text:
        logging.warning("Input text for summarization is empty.")
        return "Error: Input text was empty."

    logging.info(f"Sending text (length: {len(text)}) to DeepSeek model: {model_name} for summarization.")

    # 准备提示词
    prompt_message = f"""请将以下英文学术论文内容进行详细总结，提取关键信息、方法、结果和结论，并以清晰的结构用中文Markdown格式输出。

论文内容：
---
{text[:30000]} # Limit input length if necessary based on model limits
---

请确保总结内容准确、全面，并保留原文的核心观点。输出格式必须是Markdown。
"""

    try:
        # 使用OpenAI风格的API调用
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant skilled in summarizing academic papers into Chinese Markdown."},
                {"role": "user", "content": prompt_message},
            ],
            max_tokens=2048,
            temperature=0.5,
        )
        
        # 提取结果
        if response.choices and response.choices[0].message:
            summary = response.choices[0].message.content
            logging.info("Successfully received summary from DeepSeek.")
            return summary.strip()
        else:
            logging.error(f"API response format unexpected: {response}")
            return "Error: Failed to get valid summary from API."

    except Exception as e:
        logging.error(f"Error calling API: {e}")
        return f"Error: API call failed - {e}"

def save_markdown(summary: str, output_path: str):
    """Saves the summary to a Markdown file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        logging.info(f"Summary successfully saved to {output_path}")
    except Exception as e:
        logging.error(f"Error saving summary to {output_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Summarize an Arxiv PDF paper using DeepSeek.")
    parser.add_argument("pdf_path", help="Path to the input PDF file.")
    parser.add_argument("-o", "--output", help="Path to the output Markdown file (optional). Defaults to Summaries/<pdf_name>_summary.md")
    parser.add_argument("-m", "--model", default="deepseek-chat", help="DeepSeek model to use (e.g., deepseek-chat, deepseek-coder). Defaults to deepseek-chat.")

    args = parser.parse_args()

    pdf_path = args.pdf_path
    model_name = args.model
    output_path_arg = args.output

    # Determine the final output path
    if output_path_arg:
        output_path = output_path_arg
    else:
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_dir = "Summaries"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{base_name}_summary.md")

    # Workflow
    logging.info(f"Starting processing for: {pdf_path}")
    paper_text = extract_text_from_pdf(pdf_path)

    if not paper_text:
        logging.error("Failed to extract text, exiting.")
        return

    summary_md = summarize_text_with_deepseek(paper_text, model_name=model_name)

    if not summary_md.startswith("Error:"):
        save_markdown(summary_md, output_path)
    else:
        logging.error("Summarization failed. Check logs for details.")


if __name__ == "__main__":
    main() 