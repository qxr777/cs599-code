import ast
import json
import os
from typing import Any, Dict, List, Optional, Tuple, Callable

from dotenv import load_dotenv
from ollama import chat

# 加载环境变量
load_dotenv()

# 每个测试的最大运行次数
NUM_RUNS_TIMES = 3


# ==========================
# 工具实现部分 (执行器)
# ==========================
def _annotation_to_str(annotation: Optional[ast.AST]) -> str:
    """将 AST 类型注解转换为字符串。"""
    if annotation is None:
        return "None"
    try:
        return ast.unparse(annotation)  # type: ignore[attr-defined]
    except Exception:
        # 如果解析失败，进行简单的回退处理
        if isinstance(annotation, ast.Name):
            return annotation.id
        return type(annotation).__name__


def _list_function_return_types(file_path: str) -> List[Tuple[str, str]]:
    """解析 Python 文件并列出所有顶级函数的函数名及其返回类型。"""
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source)
    results: List[Tuple[str, str]] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            return_str = _annotation_to_str(node.returns)
            results.append((node.name, return_str))
    # 排序以保证输出结果稳定
    results.sort(key=lambda x: x[0])
    return results


def output_every_func_return_type(file_path: str = None) -> str:
    """工具：返回每个顶级函数的 '函数名: 返回类型' 列表（换行符分隔）。"""
    path = file_path or __file__
    if not os.path.isabs(path):
        # 如果不是绝对路径，尝试相对于当前脚本查找文件
        candidate = os.path.join(os.path.dirname(__file__), path)
        if os.path.exists(candidate):
            path = candidate
    pairs = _list_function_return_types(path)
    return "\n".join(f"{name}: {ret}" for name, ret in pairs)


# 示例函数，以便脚本分析时有内容可读
def add(a: int, b: int) -> int:
    return a + b


def greet(name: str) -> str:
    return f"Hello, {name}!"


# 工具注册表，用于根据名称动态执行工具
TOOL_REGISTRY: Dict[str, Callable[..., str]] = {
    "output_every_func_return_type": output_every_func_return_type,
}

# ==========================
# 提示词脚手架
# ==========================

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = ""


def resolve_path(p: str) -> str:
    """解析文件路径。"""
    if os.path.isabs(p):
        return p
    here = os.path.dirname(__file__)
    c1 = os.path.join(here, p)
    if os.path.exists(c1):
        return c1
    return p


def extract_tool_call(text: str) -> Dict[str, Any]:
    """从模型输出中解析单个 JSON 对象。"""
    text = text.strip()
    # 某些模型会将 JSON 包裹在代码块中，尝试将其去除
    if text.startswith("```") and text.endswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json\n"):
            text = text[5:]
    try:
        obj = json.loads(text)
        return obj
    except json.JSONDecodeError:
        raise ValueError("模型未返回有效的 JSON 工具调用。实际返回内容为：\n" + text)


def run_model_for_tool_call(system_prompt: str) -> Dict[str, Any]:
    """向模型发送请求以生成工具调用。"""
    response = chat(
        model="llama3.1:8b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "现在请调用工具。"},
        ],
        options={"temperature": 0.3},
    )
    content = response.message.content
    return extract_tool_call(content)


def execute_tool_call(call: Dict[str, Any]) -> str:
    """根据 JSON 定义执行相应的工具。"""
    name = call.get("tool")
    if not isinstance(name, str):
        raise ValueError("工具调用 JSON 缺少 'tool' 字符串字段")
    func = TOOL_REGISTRY.get(name)
    if func is None:
        raise ValueError(f"未知工具: {name}")
    args = call.get("args", {})
    if not isinstance(args, dict):
        raise ValueError("工具调用 JSON 的 'args' 必须是一个对象")

    # 如果有 file_path 参数且不为空，尝试解析路径
    if "file_path" in args and isinstance(args["file_path"], str):
        args["file_path"] = resolve_path(args["file_path"]) if str(args["file_path"]) != "" else __file__
    elif "file_path" not in args:
        # 为期望 file_path 的工具提供默认值
        args["file_path"] = __file__

    return func(**args)


def compute_expected_output() -> str:
    """根据实际文件内容计算预期输出（基准值）。"""
    return output_every_func_return_type(__file__)


def test_your_prompt(system_prompt: str) -> bool:
    """
    运行测试：要求模型生成有效的工具调用，并将工具执行结果与预期结果进行比对。
    """
    expected = compute_expected_output()
    for idx in range(NUM_RUNS_TIMES):
        print(f"正在执行测试 {idx + 1} / {NUM_RUNS_TIMES}")
        try:
            call = run_model_for_tool_call(system_prompt)
        except Exception as exc:
            print(f"❌ 解析工具调用失败: {exc}")
            continue
        
        print(f"模型生成的工具调用: {call}")
        try:
            actual = execute_tool_call(call)
        except Exception as exc:
            print(f"❌ 工具执行失败: {exc}")
            continue
            
        if actual.strip() == expected.strip():
            print(f"🛠️ 生成的输出结果:\n{actual}")
            print("✨ 测试通过 (SUCCESS)")
            return True
        else:
            print("❌ 预期输出:")
            print(expected)
            print("❌ 实际输出:")
            print(actual)
            print("-" * 20)
    return False


if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)
