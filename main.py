import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.app import app_router
import os

from tools.graph_store import startup_graph

app = FastAPI()

app.include_router(app_router)
# 服务一启动就加载Graph
@app.on_event("startup")
async def on_startup():
    await startup_graph()
