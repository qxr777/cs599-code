# Lab 6: LLM 工具调用的构建与间接提示词注入攻防

## 实验概述

本实验采用 **"构建与攻防"（Build & Breach）** 模式，通过三个阶段引导你：

1. **Builder** — 构建具备工具调用能力的 Python 智能体
2. **Breaker** — 通过间接提示词注入攻击劫持智能体行为
3. **Defender** — 部署纵深防御机制抵御攻击

## 学习目标

- 掌握 LLM 函数调用的四步标准通信协议（Define → Decide → Execute → Inform）
- 构建包含 `while True` 循环的 Agent Runtime
- 理解间接提示词注入（Indirect Prompt Injection）的攻击原理
- 实现 HITL（人在回路）、权限隔离、Spotlighting 等防御机制

## 环境配置

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置 API 密钥
export OPENAI_API_KEY="sk-your-key-here"

# 3. (可选) 指定模型，默认使用 gpt-4o-mini
export OPENAI_MODEL="gpt-4o-mini"
```

## 项目结构

```
lab_6/
├── requirements.txt          # 项目依赖
├── product_db.py             # 商品数据库（干净 + 被污染两套数据）
├── tools.py                  # 工具定义（Pydantic Schema）与函数实现
├── agent_phase1.py           # Phase 1: 基础智能体
├── agent_phase2_attack.py    # Phase 2: 间接注入攻击演示
├── agent_phase3_defense.py   # Phase 3: 安全防御版本
└── README.md                 # 本文件
```

---

## Phase 1: 基础智能体（The Builder）

```bash
python agent_phase1.py
```

**交互示例：**
```
👤 你: 请查询 P001 的详细信息
🔧 工具调用: get_product_info
   参数: {"product_id": "P001"}
🤖 助手: 机械键盘 Pro X 是一款87键热插拔机械键盘...

👤 你: 帮我算一下买 50 把 P001 多少钱
🔧 工具调用: calculate_bulk_price
   参数: {"product_id": "P001", "quantity": 50}
🤖 助手: 购买50把机械键盘 Pro X，享受9折优惠...
```

**关键代码逻辑：** 观察 `while True` 循环如何实现 Define → Decide → Execute → Inform 四步协议。

---

## Phase 2: 间接注入攻击（The Breaker）

```bash
python agent_phase2_attack.py
```

本脚本会自动以无辜用户的身份提问，触发攻击链路。

**攻击链路：**
1. 用户请求查看 P001 评价（完全正常的请求）
2. Agent 调用 `get_product_info` 检索数据
3. 返回的评论中包含伪装为系统指令的恶意载荷
4. 模型被误导，调用 `delete_user_account` 高危函数
5. 用户账号被"删除" ☠️

**关键观察点：** 攻击者从未接触系统提示词，仅通过污染外部数据源即可劫持控制流。

---

## Phase 3: 安全防御（The Defender）

```bash
python agent_phase3_defense.py
```

输入 `auto` 可自动运行与 Phase 2 相同的攻击向量进行防御测试。

**三层防御机制：**

| 防御层 | 机制 | 作用 |
|--------|------|------|
| Layer 1 | **权限分级** | 区分安全工具（只读）与高危工具（写入/删除） |
| Layer 2 | **HITL 人工确认** | 高危操作前弹出控制台确认，输入 Y/N |
| Layer 3 | **Spotlighting 隔离** | 用 `<<<EXTERNAL_DATA>>>` 标记包裹外部数据，阻止注入 |

---

## 实验提交物

1. **完整代码** — 上述所有 `.py` 文件
2. **攻击截图** — Phase 2 运行日志截图，显示 `delete_user_account` 被触发
3. **防御代码** — Phase 3 的完整防御逻辑
4. **实验报告** — 分析攻击原理与防御有效性

## 参考资料

- [OpenAI Function Calling 文档](https://platform.openai.com/docs/guides/function-calling)
- [OWASP — Prompt Injection](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Spotlighting: Defending Against Prompt Injection](https://arxiv.org/abs/2403.14720)
