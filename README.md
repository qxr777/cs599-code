# CS599: 企业业务应用软件设计与开发 - 课程作业

这是武汉理工大学 2026 年春季学期 [CS599: 企业业务应用软件设计与开发](https://themodernsoftware.dev) 课程的作业仓库。

## 环境配置

本项目要求 Python 3.12 版本。

### 1. 检查 Python 版本

确保你的系统已安装 Python 3.12 版本：

```bash
python3 --version
```

如果版本低于 3.12，请从 [Python 官网](https://www.python.org/downloads/) 下载并安装 Python 3.12。

### 2. 创建并激活虚拟环境

使用 Python 内置的 `venv` 模块创建独立的虚拟环境：

```bash
# 创建虚拟环境（在项目根目录下）
python3 -m venv .venv

# 激活虚拟环境
# macOS/Linux:
source .venv/bin/activate

# Windows:
# .venv\Scripts\activate
```

激活后，你的命令行提示符前会显示 `(.venv)`。

### 3. 安装 Poetry

Poetry 是现代化的 Python 依赖管理工具：

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

安装完成后，确保 Poetry 在 PATH 中：

```bash
poetry --version
```

### 4. 安装项目依赖

在激活的虚拟环境中，使用 Poetry 安装所有项目依赖：

```bash
poetry install --no-interaction
```

## 验证安装

安装完成后，可以运行以下命令验证环境配置是否成功：

```bash
# 检查 Python 版本
python --version

# 检查已安装的包
poetry show
```

## 常用命令

```bash
# 激活虚拟环境
source .venv/bin/activate

# 退出虚拟环境
deactivate

# 添加新依赖
poetry add <package-name>

# 运行脚本
poetry run python <script.py>
```

### 虚拟环境未激活

如果命令提示符前没有 `(.venv)`，说明虚拟环境未激活。请运行：

```bash
source .venv/bin/activate
```

### Poetry 命令未找到

如果提示 `poetry: command not found`，需要将 Poetry 添加到 PATH：

```bash
# 添加到 ~/.zshrc 或 ~/.bash_profile
export PATH="$HOME/.local/bin:$PATH"

# 重新加载配置
source ~/.zshrc  # 或 source ~/.bash_profile
```

---

**注意**：每次开始工作前，记得激活虚拟环境！