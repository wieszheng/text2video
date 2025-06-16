# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/16 21:34
@Author   : wieszheng
@Software : PyCharm
"""

from fastapi import APIRouter

from app.services.voice import get_all_voices

router = APIRouter()


@router.get("/voices")
async def list_voices():
    """
    获取所有支持的语音列表
    """
    return await get_all_voices()
