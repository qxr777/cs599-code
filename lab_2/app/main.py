from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager

from .db import init_db
from .routers import action_items, notes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时：初始化数据库
    init_db()
    yield
    # 关闭时：可以在这里做清理工作

app = FastAPI(
    title="Action Item Extractor",
    description="一个基于 LLM 的行动项提取应用 (Lab 2)",
    lifespan=lifespan
)

# 挂载静态文件
frontend_dir = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = frontend_dir / "index.html"
    return html_path.read_text(encoding="utf-8")

# 引入路由
app.include_router(notes.router)
app.include_router(action_items.router)