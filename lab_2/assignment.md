# 第二周 – 行动项提取器

本周我们将扩展一个最小化的 FastAPI + SQLite 应用，该应用可以将自由格式的笔记转换为枚举的行动项清单。

***我们建议在开始之前阅读完整个文档。***

提示：预览此 Markdown 文件
- Mac 用户按 `Command (⌘) + Shift + V`
- Windows/Linux 用户按 `Ctrl + Shift + V`


## 开始使用

### Trae CN 设置
按照以下说明设置 Trae CN 并打开你的项目：
1. 下载 Trae CN：https://www.trae.cn/
2. 安装并启动 Trae CN
3. 在 Trae CN 中打开项目：点击 "打开文件夹"，选择项目根目录

### 当前应用
以下是启动当前初始应用的步骤：

1. 激活你的虚拟环境：
```bash
source .venv/bin/activate
```

2. 从项目根目录运行服务器：
```bash
poetry run uvicorn lab_2.app.main:app --reload
```

3. 打开浏览器并访问 http://127.0.0.1:8000/

4. 熟悉应用的当前状态。确保你可以成功输入笔记并生成提取的行动项清单。

## 练习
对于每个练习，使用 Trae CN 帮助你实现对当前行动项提取器应用的指定改进。

在完成作业的过程中，使用 `writeup.md` 记录你的进度。务必包含你使用的提示词，以及你或 Trae CN 所做的任何更改。我们将根据写作报告的内容进行评分。同时请在代码中添加注释以记录你的更改。

### TODO 1: 搭建新功能

分析 `lab_2/app/services/extract.py` 中现有的 `extract_action_items()` 函数，该函数目前使用预定义的启发式规则提取行动项。

你的任务是实现一个 **基于 LLM 的** 替代方案 `extract_action_items_llm()`，利用 Ollama 通过大语言模型执行行动项提取。

一些提示：
- 要生成结构化输出（即 JSON 字符串数组），请参考此文档：https://ollama.com/blog/structured-outputs 
- 要浏览可用的 Ollama 模型，请参考此文档：https://ollama.com/library。注意较大的模型会占用更多资源，建议从小模型开始。拉取并运行模型：`ollama run {MODEL_NAME}`

### TODO 2: 添加单元测试

在 `lab_2/tests/test_extract.py` 中为 `extract_action_items_llm()` 编写单元测试，覆盖多种输入（例如：项目符号列表、关键字前缀行、空输入）。

### TODO 3: 重构现有代码以提高清晰度

对后端代码进行重构，特别关注以下方面：明确定义的 API 契约/模式、数据库层清理、应用生命周期/配置、错误处理。

### TODO 4: 使用 Agentic 模式自动化小任务

1. 将基于 LLM 的提取集成为新端点。更新前端以包含"LLM 提取"按钮，点击时通过新端点触发提取过程。

2. 暴露一个最终端点以检索所有笔记。更新前端以包含"列出笔记"按钮，点击时获取并显示所有笔记。

### TODO 5: 从代码库生成 README

***学习目标：***
*学生学习 AI 如何内省代码库并自动生成文档，展示 Trae CN 解析代码上下文并将其转换为人类可读形式的能力。*

使用 Trae CN 分析当前代码库并生成结构良好的 `README.md` 文件。README 至少应包括：
- 项目简要概述
- 如何设置和运行项目
- API 端点和功能
- 运行测试套件的说明

## 交付物
根据提供的说明填写 `lab_2/writeup.md`。确保你的所有更改都在代码库中有记录。

## 评分标准（总计 100 分）
- 每个部分（1-5）20 分（生成的代码 10 分，提示词 10 分）。