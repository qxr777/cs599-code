# Action Item Extractor (Lab 2)

这是一个基于 FastAPI 和大语言模型（Ollama）的智能笔记行动项提取应用。它可以将自由格式的会议笔记或随笔转化为结构化的待办事项清单。

## 🌟 核心功能

- **智能提取**：支持基础启发式提取和基于 AI（Llama 3.1:8b）的深度语义提取。
- **笔记管理**：自动保存笔记历史，支持回溯与重新填充。
- **任务追踪**：实时标记行动项完成状态，并同步持久化到 SQLite 数据库。
- **现代架构**：使用 FastAPI 构建，Pydantic 模型进行类型校验，支持异步生命周期管理。

## 🛠️ 技术栈

- **后端**: Python 3.12, FastAPI, SQLAlchemy (SQLite)
- **AI 引擎**: Ollama (llama3.1:8b)
- **前端**: 原生 HTML5 / JavaScript (Vanilla JS)
- **依赖管理**: Poetry

## 🚀 快速开始

### 1. 环境准备

确保你已安装 Python 3.12 并在根目录下配置了虚拟环境：

```bash
# 激活环境
source .venv/bin/activate
```

### 2. 启动 AI 服务

确保 [Ollama](https://ollama.com/) 已安装并运行，并拉取所需模型：

```bash
ollama pull llama3.1:8b
```

### 3. 运行应用

在项目根目录下，运行以下命令启动后端服务器：

```bash
poetry run uvicorn lab_2.app.main:app --reload
```

访问地址：[http://127.0.0.1:8000](http://127.0.0.1:8000)

## 📡 API 端点说明

### 笔记接口
- `POST /notes`: 创建新笔记。
- `GET /notes`: 获取所有历史笔记。
- `GET /notes/{id}`: 获取特定笔记详情。

### 行动项提取接口
- `POST /action-items/extract`: 使用基础正则规则提取。
- `POST /action-items/extract-llm`: 使用 Ollama 大模型提取（推荐）。
- `GET /action-items`: 获取所有行动项。
- `POST /action-items/{id}/done`: 更新行动项完成状态。

## 🧪 运行测试

使用 `pytest` 运行单元测试，验证提取算法的准确性：

```bash
.venv/bin/pytest lab_2/tests/test_extract.py
```

## 📂 目录结构

```text
lab_2/
├── app/
│   ├── db.py          # 数据库连接与 CRUD 逻辑
│   ├── main.py        # 应用入口与生命周期配置
│   ├── schemas.py     # Pydantic 类型定义 (API 契约)
│   ├── routers/       # API 路由模块
│   └── services/      # 核心提取逻辑 (启发式 vs LLM)
├── frontend/          # 前端静态页面
├── tests/             # 单元测试套件
└── assignment.md      # 实验作业说明
```
