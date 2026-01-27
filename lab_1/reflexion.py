import os
import re
from typing import Callable, List, Tuple
from dotenv import load_dotenv
from ollama import chat

# 加载环境变量
load_dotenv()

# 每轮运行的次数
NUM_RUNS_TIMES = 1

# --- 提示词配置 ---

SYSTEM_PROMPT = """你是一个编程助手。
请仅输出一个包含 Python 代码块的响应，定义函数 is_valid_password(password: str) -> bool。
不要输出任何开场白、解释或注释。保持实现精简。"""

# 反思提示词：指导 LLM 如何改进失败的代码
YOUR_REFLEXION_PROMPT = """你是一个代码审查和改进专家。
你将收到一段未通过测试的 Python 代码以及失败的测试用例详细信息。

你的任务：
1. 分析失败原因
2. 输出改进后的**完整函数定义**

关键要求：
- 只输出一个 Python 代码块，包含完整的 is_valid_password 函数定义
- 不要输出测试代码、示例用法或其他内容
- 密码必须同时满足所有条件（使用 AND 逻辑，不是 OR）
- 特殊字符必须显式检查（不能遗漏）
- 不要添加任何解释文字或注释"""


# 用于评估生成代码的基准测试集
SPECIALS = set("!@#$%^&*()-_")
TEST_CASES: List[Tuple[str, bool]] = [
    ("Password1!", True),       # 合法
    ("password1!", False),      # 缺失大写字母
    ("Password!", False),       # 缺失数字
    ("Password1", False),       # 缺失特殊字符
]


def extract_code_block(text: str) -> str:
    """提取 Markdown 中的 Python 代码块。"""
    m = re.findall(r"```python\n([\s\S]*?)```", text, flags=re.IGNORECASE)
    if m:
        return m[-1].strip()
    m = re.findall(r"```\n([\s\S]*?)```", text)
    if m:
        return m[-1].strip()
    return text.strip()


def load_function_from_code(code_str: str) -> Callable[[str], bool]:
    """通过 exec 从字符串动态加载函数。"""
    namespace: dict = {}
    exec(code_str, namespace)  # noqa: S102 (在练习中执行模型生成的受控代码)
    func = namespace.get("is_valid_password")
    if not callable(func):
        raise ValueError("在生成的代码中未找到可调用的 is_valid_password 函数")
    return func


def evaluate_function(func: Callable[[str], bool]) -> Tuple[bool, List[str]]:
    """根据预定义的测试用例评估函数。"""
    failures: List[str] = []
    for pw, expected in TEST_CASES:
        try:
            result = bool(func(pw))
        except Exception as exc:
            failures.append(f"输入: {pw} → 抛出异常: {exc}")
            continue

        if result != expected:
            # 根据基准规则计算诊断信息
            reasons = []
            if len(pw) < 8:
                reasons.append("长度 < 8")
            if not any(c.islower() for c in pw):
                reasons.append("缺失小写字母")
            if not any(c.isupper() for c in pw):
                reasons.append("缺失大写字母")
            if not any(c.isdigit() for c in pw):
                reasons.append("缺失数字")
            if not any(c in SPECIALS for c in pw):
                reasons.append("缺失特殊字符")
            if any(c.isspace() for c in pw):
                reasons.append("包含空格")

            failures.append(
                f"输入: {pw} → 预期 {expected}, 实际 {result}。失败原因: {', '.join(reasons) or '未知'}"
            )

    return (len(failures) == 0, failures)


def generate_initial_function(system_prompt: str) -> str:
    """生成初始版本的函数。"""
    response = chat(
        model="llama3.1:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "现在请提供实现。"},
        ],
        options={"temperature": 0.2},
    )
    return extract_code_block(response.message.content)


def your_build_reflexion_context(prev_code: str, failures: List[str]) -> str:
    """使用先前的代码和失败案例构建反思环节的用户消息。"""
    return f"""先前的实现：

```python
{prev_code}
```

测试失败案例：
{chr(10).join(f"- {f}" for f in failures)}

请修复该实现以通过所有测试。"""


def apply_reflexion(
    reflexion_prompt: str,
    build_context: Callable[[str, List[str]], str],
    prev_code: str,
    failures: List[str],
) -> str:
    """执行反思步骤，获取改进后的代码。"""
    reflection_context = build_context(prev_code, failures)
    print(f"📡 反思上下文 (REFLECTION CONTEXT):\n{reflection_context}")
    response = chat(
        model="llama3.1:8b",
        messages=[
            {"role": "system", "content": reflexion_prompt},
            {"role": "user", "content": reflection_context},
        ],
        options={"temperature": 0.2},
    )
    return extract_code_block(response.message.content)


def run_reflexion_flow(
    system_prompt: str,
    reflexion_prompt: str,
    build_context: Callable[[str, List[str]], str],
) -> bool:
    """运行 Self-Reflexion 流程：初始生成 -> 评估 -> 反思优化 -> 最终评估。"""
    
    # 1) 生成初始函数
    print("🚀 正在生成初始代码...")
    initial_code = generate_initial_function(system_prompt)
    print("初始代码：\n" + initial_code)
    
    try:
        func = load_function_from_code(initial_code)
        passed, failures = evaluate_function(func)
    except Exception as e:
        passed, failures = False, [f"代码无法运行: {e}"]

    if passed:
        print("✨ 成功（初始实现已通过所有测试）")
        return True
    else:
        print(f"❌ 失败（初始实现未通过部分测试）：{failures}")

    # 2) 执行单次反思迭代
    print("\n🔄 正在执行反思优化流程...")
    improved_code = apply_reflexion(reflexion_prompt, build_context, initial_code, failures)
    print("\n改进后的代码：\n" + improved_code)
    
    try:
        improved_func = load_function_from_code(improved_code)
        passed2, failures2 = evaluate_function(improved_func)
    except Exception as e:
        passed2, failures2 = False, [f"改进后的代码仍无法运行: {e}"]

    if passed2:
        print("✨ 最终测试通过 (SUCCESS)")
        return True

    print("⚠️ 反思后测试仍未通过：")
    for f in failures2:
        print("- " + f)
    return False


if __name__ == "__main__":
    run_reflexion_flow(SYSTEM_PROMPT, YOUR_REFLEXION_PROMPT, your_build_reflexion_context)
