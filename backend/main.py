"""一步 · AI 求职成长陪伴产品 · 后端服务"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from database import init_db
from routers.user import router as user_router
from routers.chat import router as chat_router
from routers.content import router as content_router
from routers.depth import router as depth_router
from routers.holland import router as holland_router
from routers.radar import router as radar_router
from routers.roadmap import router as roadmap_router
from routers.milestones import router as milestones_router
from routers.anxiety import router as anxiety_router
from routers.tasks import router as tasks_router
from routers.cases import router as cases_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="一步 Career Companion API",
    description="AI 求职成长陪伴产品后端服务",
    version="5.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册所有 API 路由
app.include_router(user_router)
app.include_router(chat_router)
app.include_router(content_router)
app.include_router(depth_router)
app.include_router(holland_router)
app.include_router(radar_router)
app.include_router(roadmap_router)
app.include_router(milestones_router)
app.include_router(anxiety_router)
app.include_router(tasks_router)
app.include_router(cases_router)

# 健康检查
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "career-companion", "version": "5.0.0"}

# Web Demo - 不使用 mount，改用 exception_handler 作为 404 fallback
# mount 会覆盖所有 API 路由，所以必须在 API 路由之后用 exception 方式处理
from fastapi.responses import FileResponse, HTMLResponse
from starlette.exceptions import HTTPException
from fastapi import Request

WEB_DEMO_DIR = os.path.join(os.path.dirname(__file__), "..", "web-demo")
STATIC_MEDIA = {".html":"text/html",".css":"text/css",".js":"application/javascript",".json":"application/json",".png":"image/png",".jpg":"image/jpeg",".svg":"image/svg+xml",".ico":"image/x-icon"}

@app.exception_handler(404)
async def fallback_to_web_demo(request: Request, exc: HTTPException):
    """When an API route returns 404, serve web-demo static files as fallback."""
    # Only serve static files for non-API GET requests
    if request.method == "GET" and not request.url.path.startswith("/api/"):
        filepath = request.url.path.lstrip("/") or "index.html"
        full_path = os.path.join(WEB_DEMO_DIR, filepath)
        
        if os.path.isdir(full_path):
            full_path = os.path.join(full_path, "index.html")
        
        if os.path.isfile(full_path):
            ext = os.path.splitext(full_path)[1].lower()
            return FileResponse(full_path, media_type=STATIC_MEDIA.get(ext))
        
        # SPA fallback: serve index.html
        index_path = os.path.join(WEB_DEMO_DIR, "index.html")
        if os.path.isfile(index_path):
            return FileResponse(index_path)
    
    # For API 404s, return standard 404
    return HTMLResponse(status_code=404, content='{"detail":"Not Found"}')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
