import os
import re
from collections import Counter
from dotenv import load_dotenv
from ollama import chat

# 加载环境变量
load_dotenv()

# 执行测试的次数（用于多数投票）
NUM_RUNS_TIMES = 5

# TODO: 完善此提示词！尽量让所有运行结果的正确率接近 100%。
YOUR_SYSTEM_PROMPT = """你是一个精通数学问题的专家。请逐步解决应用题。

解题流程：
1. 识别所有给出的数字及其含义。
2. 确定问题究竟在问什么。
3. 建立正确的数学解题思路。
4. 逐步进行计算。
5. 验证你的答案是否合理。
6. 在最后一行仅输出 "Answer: <数字>"。

关键规则：
- 在给出最终答案前，清晰地展示你的推理过程。
- 算术计算必须极其精确。
- 最后一行必须严格遵守格式："Answer: <数字>"。
- "Answer:" 行之后不得有任何文字。
- 答案必须是一个单一的数字。
- 反复检查你的计算过程。"""

USER_PROMPT = """
请解决这个问题，并在最后一行给出最终答案，格式为 "Answer: <数字>"。

亨利在 60 英里的自行车骑行中停了两次。他第一次停是在骑了 20 英里后。
他的第二次停是在骑行结束前 15 英里处。他在第一次停和第二次停之间骑了多少英里？
"""

# 预期输出答案
EXPECTED_OUTPUT = "Answer: 25"


def extract_final_answer(text: str) -> str:
    """从详细的推理链中提取最后一行 'Answer: ...'。

    - 寻找最后一行以 'Answer:' 开头（忽略大小写）的内容。
    - 将包含数字的回答归一化为 'Answer: <数字>'。
    - 如果未检测到数字，则回退到返回匹配到的原始内容。
    """
    matches = re.findall(r"(?mi)^\s*answer\s*:\s*(.+)\s*$", text)
    if matches:
        value = matches[-1].strip()
        # 提取数字（支持整数和小数）
        num_match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
        if num_match:
            return f"Answer: {num_match.group(0)}"
        return f"Answer: {value}"
    return text.strip()


def test_your_prompt(system_prompt: str) -> bool:
    """运行提示词 NUM_RUNS_TIMES 次，对提取出的 'Answer: ...' 行进行多数投票。

    如果多数票通过的答案等于预期输出，则打印 "✨ 测试通过 (SUCCESS)"。
    """
    answers: list[str] = []
    for idx in range(NUM_RUNS_TIMES):
        print(f"正在执行测试 {idx + 1} / {NUM_RUNS_TIMES}")
        response = chat(
            # model="llama3.1:8b",
            model="qwen2.5:latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 1},  # 高温度以增加多样性，便于采样投票
        )
        output_text = response.message.content
        final_answer = extract_final_answer(output_text)
        print(f"第 {idx + 1} 次运行答案: {final_answer}")
        answers.append(final_answer.strip())

    if not answers:
        print("未产生任何答案。")
        return False

    # 多数投票逻辑
    counts = Counter(answers)
    majority_answer, majority_count = counts.most_common(1)[0]
    print(f"多数投票结果: {majority_answer} ({majority_count}/{len(answers)})")

    if majority_answer.strip() == EXPECTED_OUTPUT.strip():
        print("✨ 测试通过 (SUCCESS)")
        return True

    # 如果多数派结果不匹配，打印分布情况辅助调试
    print(f"❌ 预期结果: {EXPECTED_OUTPUT}")
    print("答案分布情况:")
    for answer, count in counts.most_common():
        print(f"  {answer}: {count}")
    return False


if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)
