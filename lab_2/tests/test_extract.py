import os
import pytest
from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


@pytest.mark.skipif(not os.getenv("OLLAMA_HOST") and not os.path.exists("/usr/local/bin/ollama"), reason="Ollama not found")
def test_extract_action_items_llm():
    # 场景 1: 项目符号和混合格式
    text1 = """
    - Finish the report
    TODO: call the client
    * [ ] update the meeting minutes
    """
    items1 = extract_action_items_llm(text1)
    # LLM 应该能识别出这三个任务
    assert any("report" in item.lower() for item in items1)
    assert any("client" in item.lower() for item in items1)
    assert any("minutes" in item.lower() for item in items1)

    # 场景 2: 自然语言笔记
    text2 = "We need to fix the bug in login page and then design the new dashboard tomorrow."
    items2 = extract_action_items_llm(text2)
    # LLM 可能会将其翻译为中文（因为 Prompt 是中文的）
    assert any(("fix" in item.lower() or "修复" in item) for item in items2)
    assert any(("design" in item.lower() or "设计" in item) for item in items2)

    # 场景 3: 无效输入
    assert extract_action_items_llm("") == []

    assert extract_action_items_llm("The weather is nice today.") == []
