# Arxiv-Academy

Arxiv论文转换和处理工具，专为研究人员设计。自动化将PDF论文转换为Markdown格式，支持中英文输出，可用于Obsidian等知识管理工具。

[![Python测试与代码质量检查](https://github.com/yourusername/Arxiv-Academy/actions/workflows/python-test.yml/badge.svg)](https://github.com/yourusername/Arxiv-Academy/actions/workflows/python-test.yml)

## 功能特点

- **PDF转Markdown**: 将学术论文PDF自动转换为结构化Markdown
- **中文翻译**: 支持将英文论文自动翻译为中文
- **数学公式支持**: 完美保留和渲染数学公式
- **表格转换**: 自动将论文中的表格转换为Markdown表格
- **分段处理**: 支持处理长文档，自动分段转换
- **Obsidian兼容**: 专为Obsidian笔记软件优化

## 安装指南

### 前提条件

- Python 3.8+
- pip包管理器

### 安装步骤

1. 克隆仓库:

```bash
git clone https://github.com/yourusername/Arxiv-Academy.git
cd Arxiv-Academy
```

2. 创建虚拟环境:

```bash
python -m venv .arxivenv
source .arxivenv/bin/activate  # Linux/MacOS
# 或
.\.arxivenv\Scripts\activate  # Windows
```

3. 安装依赖:

```bash
pip install -r requirements.txt
```

4. 配置API密钥:

创建`.env`文件并添加DeepSeek API密钥:

```
DEEPSEEK_API_KEY=your_api_key_here
```

## 使用方法

### PDF转Markdown

将PDF文件转换为英文Markdown:

```bash
python pdf_to_md.py path/to/your/paper.pdf
```

### 翻译为中文

将PDF文件转换并翻译为中文Markdown:

```bash
python pdf_to_md.py path/to/your/paper.pdf --chinese
```

### 指定输出路径

```bash
python pdf_to_md.py path/to/your/paper.pdf -o output_path.md
```

### 使用不同的模型

```bash
python pdf_to_md.py path/to/your/paper.pdf -m deepseek-chat
```

## 开发指南

参见[贡献指南](CONTRIBUTING.md)了解如何参与开发。

## 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件。

## 鸣谢

- [DeepSeek AI](https://deepseek.com/)提供的API支持
- [PyMuPDF](https://pymupdf.readthedocs.io/)用于PDF文本提取
- 所有贡献者和测试者

## 常见问题

**Q: 为什么需要API密钥?**  
A: 本工具使用DeepSeek AI的API进行文本处理和翻译，需要有效的API密钥。

**Q: 支持哪些PDF类型?**  
A: 主要支持学术论文PDF，特别是来自Arxiv的论文，但也支持其他格式良好的PDF文件。
