# 贡献指南

感谢您对Arxiv-Academy项目的关注！我们非常欢迎社区贡献，无论是修复bug、添加新功能、完善文档还是提出建议。本指南将帮助您了解如何参与项目开发。

## 开发环境设置

1. Fork本仓库并克隆到本地：

```bash
git clone https://github.com/your-username/Arxiv-Academy.git
cd Arxiv-Academy
```

2. 创建并激活虚拟环境：

```bash
python -m venv .arxivenv
source .arxivenv/bin/activate  # Linux/MacOS
# 或
.\.arxivenv\Scripts\activate  # Windows
```

3. 安装开发依赖：

```bash
pip install -r requirements.txt
pip install pytest flake8 black  # 开发工具
```

## 开发流程

1. 创建新分支进行开发：

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/issue-description
```

2. 进行代码修改，并确保：
   - 代码遵循项目风格指南
   - 添加适当的注释和文档
   - 编写相关测试（如果适用）

3. 提交前检查代码质量：

```bash
# 代码格式化
black .

# 代码风格检查
flake8 .

# 运行测试（如果适用）
pytest
```

4. 提交更改：

```bash
git add .
git commit -m "描述性的提交信息"
git push origin your-branch-name
```

5. 在GitHub上创建Pull Request到主仓库的main分支。

## Pull Request指南

- 使用清晰的标题和描述
- 列出实现的功能或修复的问题
- 包含任何相关的截图或演示
- 链接到相关的Issue（如果适用）
- 确保所有CI检查都通过

## 代码风格指南

我们遵循PEP 8风格指南，并使用Black进行代码格式化。一些关键点：

- 使用4个空格缩进
- 最大行长度为88个字符
- 使用有意义的变量和函数名
- 添加类型注释
- 为函数和类添加docstring

## 测试指南

添加新功能时，请编写相应的测试。我们使用pytest进行测试：

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_specific_file.py
```

## Issue指南

创建Issue时，请提供：

- 清晰的问题描述
- 复现步骤（对于bug）
- 预期行为和实际行为
- 环境信息（操作系统、Python版本等）
- 相关截图或日志

## 文档

代码更改通常需要更新相关文档。请确保：

- 更新README.md中的相关部分
- 添加或更新函数和类的docstring
- 更新使用示例（如果适用）

## 许可证

通过贡献代码，您同意您的贡献将根据项目的[MIT许可证](LICENSE)进行许可。

## 联系方式

如有任何问题，请通过GitHub Issues或讨论区联系我们。 