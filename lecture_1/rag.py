import os
import re
from typing import List, Callable
from dotenv import load_dotenv
from ollama import chat

# 加载环境变量
load_dotenv()

# 每个提示词测试的运行次数
NUM_RUNS_TIMES = 5

# 数据文件路径
DATA_FILES: List[str] = [
    os.path.join(os.path.dirname(__file__), "data", "api_docs.txt"),
]


def load_corpus_from_files(paths: List[str]) -> List[str]:
    """从指定路径加载语料库。"""
    corpus: List[str] = []
    for p in paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    corpus.append(f.read())
            except Exception as exc:
                corpus.append(f"[加载错误] {p}: {exc}")
        else:
            corpus.append(f"[文件缺失] {p}")
    return corpus


# 从外部文件加载语料（简单的 API 文档）。如果缺失，则回退。
CORPUS: List[str] = load_corpus_from_files(DATA_FILES)

# 任务问题描述
QUESTION = (
    "编写一个 Python 函数 `fetch_user_name(user_id: str, api_key: str) -> str`，"
    "调用文档中定义的 API 来根据 ID 获取用户，并仅以字符串形式返回用户的姓名 (name)。"
)


# TODO: 在此处填入你的系统提示词！
YOUR_SYSTEM_PROMPT = (
    "你是一个专业的代码助手，负责根据提供的上下文编写 Python 代码。"
    "请严格遵循要求，并仅在 Markdown Python 代码块中返回代码。"
)


# 验证代码是否包含必要的片段（而非精确字符串匹配）
REQUIRED_SNIPPETS = [
    "def fetch_user_name(",
    "requests.get",
    "/users/",
    "X-API-Key",
    "return",
]


def YOUR_CONTEXT_PROVIDER(corpus: List[str]) -> List[str]:
    """TODO: 从 CORPUS 中选择并返回与此任务相关的文档子集。

    例如：返回 [] 模拟缺失上下文，或返回 [corpus[0]] 包含 API 文档。
    """
    # TODO: 选择并返回与任务相关的语料
    return corpus
    # return []


def make_user_prompt(question: str, context_docs: List[str]) -> str:
    """构建包含上下文及任务要求的用户提示词。"""
    if context_docs:
        context_block = "\n".join(f"- {d}" for d in context_docs)
    else:
        context_block = "(未提供上下文)"
    
    return (
        f"上下文信息（仅使用此处提供的信息）：\n{context_block}\n\n"
        f"任务目标：{question}\n\n"
        "具体要求：\n"
        "- 使用文档中注明的 Base URL 和端点 (endpoint)。\n"
        "- 发送文档中注明的认证请求头 (authentication header)。\n"
        "- 对于非 200 的响应应当抛出异常 (raise)。\n"
        "- 仅返回用户姓名字符串。\n\n"
        "输出格式：包含函数实现及必要导入的单个 Python 代码块（使用 ```python）。\n"
    )


def extract_code_block(text: str) -> str:
    """从文本中提取 Python 代码块。"""
    # 优先匹配 ```python ... ```
    m = re.findall(r"```python\n([\s\S]*?)```", text, flags=re.IGNORECASE)
    if m:
        return m[-1].strip()
    # 回退到匹配任何代码块
    m = re.findall(r"```\n([\s\S]*?)```", text)
    if m:
        return m[-1].strip()
    return text.strip()


def test_your_prompt(system_prompt: str, context_provider: Callable[[List[str]], List[str]]) -> bool:
    """运行多轮测试，如果输出包含所有必需的代码片段，则返回 True。"""
    context_docs = context_provider(CORPUS)
    user_prompt = make_user_prompt(QUESTION, context_docs)

    for idx in range(NUM_RUNS_TIMES):
        print(f"正在执行测试 {idx + 1} / {NUM_RUNS_TIMES}")
        response = chat(
            model="llama3.1:8b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            options={"temperature": 0.0},
        )
        output_text = response.message.content
        code = extract_code_block(output_text)
        
        # 检查是否包含所有必需的代码片段
        missing = [s for s in REQUIRED_SNIPPETS if s not in code]
        if not missing:
            print("-" * 20)
            print("模型生成的响应：")
            print(output_text)
            print("-" * 20)
            print("✨ 测试通过 (SUCCESS)")
            return True
        else:
            print("❌ 缺失必需的代码片段：")
            for s in missing:
                print(f"  - {s}")
            print("当前生成的代码：\n" + code)
            print("-" * 20)
    return False


if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT, YOUR_CONTEXT_PROVIDER)
