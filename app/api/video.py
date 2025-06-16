# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/16 21:31
@Author   : wieszheng
@Software : PyCharm
"""
from pathlib import Path

from fastapi import APIRouter

from app.schemas.video import VideoGenerateParams
from app.services.video import generate_video


router = APIRouter()


@router.post("/generate")
async def generate_video_endpoint(
        body: VideoGenerateParams
):
    video_file, video_duration = await generate_video(body)
    path = Path(video_file)
    parts = path.parts
    index = parts.index("tasks")

    return {"video_path": f"/tasks/{parts[index + 1]}/video.mp4", "duration": video_duration}
