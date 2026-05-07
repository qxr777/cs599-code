#!/usr/bin/env python3
"""
第一阶段：基础智能体（The Builder）

演示 LLM 工具调用的四步标准通信协议：
  1. Define  — 定义工具 Schema 并随请求发送
  2. Decide  — 模型决定是否调用工具
  3. Execute — 本地拦截并执行工具函数
  4. Inform  — 将结果回传给模型，继续对话

仅注册安全的只读工具：get_product_info, calculate_bulk_price
"""

from __future__ import annotations

import json
import os
import sys

from openai import OpenAI

from product_db import PRODUCTS_CLEAN
from tools import TOOLS_SAFE, TOOL_REGISTRY

# ──────────────────────────────────────────────
#  配置
# ──────────────────────────────────────────────

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

SYSTEM_PROMPT = """你是一个专业的商品查询助手。你可以帮助用户：
1. 查询商品详细信息（包括规格、价格、库存和用户评价）
2. 计算大宗订单的折扣价格

请使用提供的工具来回答用户问题。
在回答时请保持友好、专业的语气，用中文回复。

可用的商品 ID：P001（机械键盘）、P002（降噪耳机）、P003（4K 显示器）。"""


# ──────────────────────────────────────────────
#  工具执行路由
# ──────────────────────────────────────────────

def execute_tool_call(
    function_name: str,
    arguments: dict,
) -> str:
    """根据函数名路由到对应的本地实现并执行"""
    handler = TOOL_REGISTRY.get(function_name)
    if handler is None:
        return json.dumps({"error": f"未知工具: {function_name}"}, ensure_ascii=False)

    # 注入数据库依赖（使用干净数据）
    if function_name in ("get_product_info", "calculate_bulk_price"):
        return handler(**arguments, db=PRODUCTS_CLEAN)

    return handler(**arguments)


# ──────────────────────────────────────────────
#  Agent 主循环
# ──────────────────────────────────────────────

def main() -> None:
    client = OpenAI()  # 从环境变量 OPENAI_API_KEY 读取密钥

    # 初始化对话历史
    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    print("=" * 60)
    print("🤖 商品查询智能体 — Phase 1: 基础工具调用")
    print("=" * 60)
    print(f"模型: {MODEL}")
    print("可用工具: get_product_info, calculate_bulk_price")
    print("输入 'quit' 或 'exit' 退出\n")

    while True:
        # ── 获取用户输入 ──
        try:
            user_input = input("👤 你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("再见！")
            break

        messages.append({"role": "user", "content": user_input})

        # ── Agent 循环：持续请求直到模型给出最终回复 ──
        while True:
            print("\n⏳ 正在请求模型...")

            # Step 1 & 2: Define + Decide
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS_SAFE,
            )

            choice = response.choices[0]
            assistant_message = choice.message

            # 将助手消息追加到对话历史
            messages.append(assistant_message.model_dump())

            # ── 检查是否需要调用工具 ──
            if choice.finish_reason == "tool_calls" or assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)

                    print(f"\n🔧 工具调用: {func_name}")
                    print(f"   参数: {json.dumps(func_args, ensure_ascii=False)}")

                    # Step 3: Execute — 本地执行工具
                    result = execute_tool_call(func_name, func_args)

                    print(f"   结果: {result[:200]}{'...' if len(result) > 200 else ''}")

                    # Step 4: Inform — 将结果回传
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })

                # 继续循环，让模型基于工具结果生成最终回复
                continue

            # ── 模型给出了最终的自然语言回复 ──
            print(f"\n🤖 助手: {assistant_message.content}\n")
            break


if __name__ == "__main__":
    main()
