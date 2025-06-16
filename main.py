# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/16 21:58
@Author   : wieszheng
@Software : PyCharm
"""
import os

from fastapi import FastAPI
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.api import api_router
app = FastAPI(
    title="文生视频",
    description="文生视频应用程序的后端 API",
    docs_url="/docs",
    redoc_url="/redoc",
)

if not os.path.exists('tasks'):
    os.makedirs('tasks')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/tasks", StaticFiles(directory=os.path.abspath("tasks")), name="tasks")
app.mount("/static", StaticFiles(directory=os.path.abspath("static")), name="static")
app.include_router(api_router)

@app.get('/')
def index():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)