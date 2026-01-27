import os
from dotenv import load_dotenv
from ollama import chat

# 加载环境变量
load_dotenv()

# 测试运行的最大次数
NUM_RUNS_TIMES = 5

# TODO: 在此处填入你的系统提示词！
YOUR_SYSTEM_PROMPT = ""

USER_PROMPT = """
反转以下单词的字母顺序。只输出反转后的单词，不要包含其他文字：

httpstatus
"""


# 预期输出结果
EXPECTED_OUTPUT = "sutatsptth"

def test_your_prompt(system_prompt: str) -> bool:
    """运行提示词测试最多 NUM_RUNS_TIMES 次，如果结果匹配预期则返回 True。

    匹配成功时打印 "✨ 测试通过 (SUCCESS)"。
    """
    for idx in range(NUM_RUNS_TIMES):
        print(f"正在执行测试 {idx + 1} / {NUM_RUNS_TIMES}")
        response = chat(
            model="deepseek-r1:8b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 0.5},
        )
        output_text = response.message.content.strip()
        # 移除 <think> 块（针对 reasoning 模型）
        import re
        output_text = re.sub(r'<think>[\s\S]*?</think>', '', output_text).strip()
        
        if output_text.strip() == EXPECTED_OUTPUT.strip():
            print("✨ 测试通过 (SUCCESS)")
            return True
        else:
            print(f"DEBUG: 完整回复: {response.message.content}")
            print(f"❌ 预期回答: {EXPECTED_OUTPUT}")
            print(f"❌ 实际回答: {output_text}")
            print("-" * 20)
    return False

if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)