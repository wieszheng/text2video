# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/16 22:38
@Author   : wieszheng
@Software : PyCharm
"""

from typing import Optional
from pydantic import BaseModel, Field


class VideoGenerateParams(BaseModel):
    text: str = Field(
        default="一个阳光明媚的上午，小白兔正在林间小路上悠闲地散步。忽然，小松鼠急匆匆地跑来，身上的松果撒了一地。",
        min_length=1, max_length=5000, description="要转换为视频的文本内容")
    task_id: Optional[str] = Field(default=None, description="任务ID")

    voice_name: str = Field(default="zh-CN-XiaoxiaoNeural", description="语音名称")
    voice_rate: float = Field(default=1.0, description="语音速率")
    resolution: Optional[str] = Field(default="1920*1080", description="分辨率")
