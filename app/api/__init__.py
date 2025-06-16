# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/16 21:32
@Author   : wieszheng
@Software : PyCharm
"""

from fastapi import APIRouter
from app.api import voice, video

api_router = APIRouter(prefix="/api")
api_router.include_router(voice.router, prefix="/voice", tags=["voice"])
api_router.include_router(video.router, prefix="/video", tags=["video"])
