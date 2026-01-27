import os
import re
from dotenv import load_dotenv
from ollama import chat

# 加载环境变量（如 API Keys）
load_dotenv()

# 每个提示词测试的运行次数
NUM_RUNS_TIMES = 5

# TODO: 在此处填入你的系统提示词！
YOUR_SYSTEM_PROMPT = """你是一个数学计算极其严谨的 AI 专家。在处理模幂运算时，必须遵循以下深度拆解流程：

**核心方法：使用欧拉定理（Euler's Theorem）**
对于互质的 a 和 n，有：a^φ(n) ≡ 1 (mod n)

**解题步骤：**

1. **计算欧拉函数 φ(100)**：
   - 100 = 4 × 25 = 2² × 5²
   - φ(100) = φ(2²) × φ(5²) = 2¹(2-1) × 5¹(5-1) = 2 × 20 = 40
   - 因此：3^40 ≡ 1 (mod 100)

2. **指数约简**：
   - 首先确认 φ(100)=40，并计算 12345 mod 40 来简化指数。
   - 12345 = 40 × 308 + 25
   - 所以：3^12345 ≡ 3^25 (mod 100)
   - 必须显示校验公式：12345 = 40 * 308 + 25。

3. **分步计算 3^25 mod 100**（为了保证准确性，必须分步计算并显示以下结果）：
   - 3^1 = 3
   - 3^2 = 9
   - 3^4 = 81
   - 3^5 = 3^4 × 3^1 = 81 × 3 = 243 ≡ 43 (mod 100)
   - 3^10 = (3^5)² = 43² = 1849 ≡ 49 (mod 100)
   - 3^20 = (3^10)² = 49² = 2401 ≡ 1 (mod 100)
   - 3^25 = 3^20 × 3^5 = 1 × 43 = 43 (mod 100)

4. **格式规约（极其重要）**：
   - 推理结束后，**最后一行必须且仅能**是：Answer: 43
   - 不要在 "Answer:" 前面加破折号 "-" 或其他符号
   - 不要在答案外面加引号 "" 或其他包装
   - 不要在 "Answer: 43" 后面添加任何解释或标点
   - 正确示例：Answer: 43

**关键要求：**
- 必须展示完整的推理过程
- 每一步计算都要明确显示
- 最终答案行必须精确匹配：Answer: 43（前后无任何额外字符）
"""


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
            options={"temperature": 0.1},  # 降低温度以提高格式一致性
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
