from __future__ import annotations

import os
import re
from typing import List
import json
from typing import Any
from ollama import chat
from dotenv import load_dotenv

load_dotenv()

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def extract_action_items_llm(text: str) -> List[str]:
    """使用 LLM (Ollama) 从文本中提取行动项。"""
    if not text.strip():
        return []
        
    system_prompt = """你是一个专业的行动项提取专家。你的任务是分析用户提供的笔记文本，并提取出所有需要执行的任务或行动项。

要求：
1. 提取结果必须简洁明了。
2. 必须以 JSON 格式返回，格式如下：{"items": ["行动项1", "行动项2", ...]}。
3. 如果没有发现任何行动项，请返回 {"items": []}。
4. 仅输出 JSON，不要有任何额外的解释或开场白。"""

    try:
        response = chat(
            model="llama3.1:8b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"请从以下文本中提取行动项：\n\n{text}"},
            ],
            format="json",
            options={"temperature": 0.2},
        )
        
        # 解析 JSON 响应
        result = json.loads(response.message.content)
        items = result.get("items", [])
        
        if not isinstance(items, list):
            # 如果模型返回的不是列表，尝试转换为列表
            return [str(items)] if items else []
            
        return [str(item).strip() for item in items if str(item).strip()]
        
    except Exception as e:
        print(f"❌ LLM 提取失败: {e}")
        # 如果 LLM 失败，回退到原始的启发式方法
        return extract_action_items(text)


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters
