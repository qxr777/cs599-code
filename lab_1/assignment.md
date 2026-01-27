# 第 1 周 — 提示工程技术 (Prompting Techniques)

你将通过设计提示词（Prompts）来完成特定任务，以此练习多种提示工程技术。每个任务的具体指令都位于其对应的源文件顶部。

## 安装与准备
请确保你已经完成了根目录 `README.md` 中描述的安装步骤。

## Ollama 安装
我们将使用 [Ollama](https://ollama.com/) 这一工具在你的本地机器上运行不同的先进大语言模型（LLMs）。请根据你的操作系统选择以下方法之一：

- **macOS (通过 Homebrew):**
  ```bash
  brew install --cask ollama 
  ollama serve
  ```

- **Linux (推荐):**
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```

- **Windows:**
  从 [ollama.com/download](https://ollama.com/download) 下载并运行安装程序。

验证安装：
```bash
ollama -v
```

在运行测试脚本之前，请确保已下载（pull）以下模型。你只需操作一次（除非你以后删除了这些模型）：
```bash
ollama run mistral-nemo:12b
ollama run llama3.1:8b
```

## 技术方案与对应源文件
- **少样本提示 (K-shot prompting)** — `lecture_1/k_shot_prompting.py`
- **思维链 (Chain-of-thought)** — `lecture_1/chain_of_thought.py`
- **工具调用 (Tool calling)** — `lecture_1/tool_calling.py`
- **自洽性采样 (Self-consistency prompting)** — `lecture_1/self_consistency_prompting.py`
- **检索增强生成 (RAG)** — `lecture_1/rag.py`
- **自我反思 (Reflexion)** — `lecture_1/reflexion.py`

## 交付要求
- 阅读每个文件中的任务描述。
- 设计并运行提示词（在代码中寻找所有标注为 `TODO` 的位置）。这应该是你唯一需要修改的地方（即不要调整模型参数）。
- 不断迭代改进提示词，直到测试脚本通过。
- 保存每种技术最终的提示词和输出结果。
- 确保提交的文件中包含所有已完成的提示工程代码。***请双击检查所有 `TODO` 是否均已解决。***

## 评分标准 (总分 60 分)
- 6 种不同的提示工程技术，每项完成得 10 分。