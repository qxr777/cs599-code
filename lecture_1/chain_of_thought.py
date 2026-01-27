import os
import re
from dotenv import load_dotenv
from ollama import chat

# 加载环境变量（如 API Keys）
load_dotenv()

# 每个提示词测试的运行次数
NUM_RUNS_TIMES = 5

# TODO: 在此处填入你的系统提示词！
YOUR_SYSTEM_PROMPT = ""


USER_PROMPT = """
请解决这个问题，并在最后一行给出最终答案，格式为 "Answer: <数字>"。

计算 3^{12345} (mod 100) 的值是多少？
"""


# 预期结果（仅包含最终数值答案）
EXPECTED_OUTPUT = "Answer: 43"


def extract_final_answer(text: str) -> str:
    """从详细的推理链中提取最后一行 'Answer: ...'。

    - 寻找最后一行匹配 'Answer:'（忽略大小写）的内容。
    - 将包含数字的答案归一化为 'Answer: <数字>'。
    - 如果未匹配到数字，则返回原始匹配内容。
    """
    matches = re.findall(r"(?mi)^\s*answer\s*:\s*(.+)\s*$", text)
    if matches:
        value = matches[-1].strip()
        # 尝试匹配数字（支持整数和小数）以进行格式归一化
        num_match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
        if num_match:
            return f"Answer: {num_match.group(0)}"
        return f"Answer: {value}"
    return text.strip()


def test_your_prompt(system_prompt: str) -> bool:
    """运行多轮测试，如果任意一轮结果匹配预期输出则返回 True。

    成功匹配时打印 "测试通过 (SUCCESS)"。
    """
    for idx in range(NUM_RUNS_TIMES):
        print(f"正在执行测试 {idx + 1} / {NUM_RUNS_TIMES}")
        response = chat(
            model="mistral-nemo:12b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 0.3},
        )
        output_text = response.message.content
        final_answer = extract_final_answer(output_text)
        
        if final_answer.strip() == EXPECTED_OUTPUT.strip():
            print("✨ 测试通过 (SUCCESS)")
            return True
        else:
            print(f"❌ 结果不匹配")
            print(f"预期回答: {EXPECTED_OUTPUT}")
            print(f"模型回答: {final_answer}")
            print("-" * 20)
    return False


if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)
