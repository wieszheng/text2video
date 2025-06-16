# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/16 21:34
@Author   : wieszheng
@Software : PyCharm
"""
import uuid
from typing import List, Tuple

import edge_tts
from edge_tts import SubMaker
from edge_tts.typing import Voice
from loguru import logger


def convert_rate_to_percent(rate: float) -> str:
    if rate == 1.0:
        return "+0%"
    percent = round((rate - 1.0) * 100)
    if percent > 0:
        return f"+{percent}%"
    else:
        return f"{percent}%"


async def generate_voice(text: str, voice_name: str, voice_rate: float = 1, audio_file: str = None,
                         subtitle_file: str = None) -> Tuple[str, str]:
    """
    生成语音和字幕
    :param text: 文本内容
    :param voice_name: 语音名称
    :param voice_rate: 语音速率
    :param audio_file: 语音文件路径
    :param subtitle_file: 字幕文件路径
    :return:
    """
    if audio_file is None:
        audio_file = f"temp_{uuid.uuid4()}.mp3"
    if subtitle_file is None:
        subtitle_file = f"temp_{uuid.uuid4()}.srt"

    # 生成语音
    rate_str = convert_rate_to_percent(voice_rate)
    logger.info(f"开始生成语音, voice name: {voice_name}")
    communicate = edge_tts.Communicate(text, voice_name, rate=rate_str)
    sub_maker = SubMaker()

    with open(audio_file, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                logger.debug(f"句子: {chunk}")
                sub_maker.feed(chunk)

    with open(subtitle_file, "w", encoding="utf-8") as file:
        file.write(sub_maker.get_srt())

    logger.info(f"已完成，输出文件: {audio_file}")

    return audio_file, subtitle_file


async def get_all_voices() -> List[Voice]:
    """
    获取音色列表
    :return:
    """
    res = await edge_tts.list_voices()
    logger.debug(f"获取到 {len(res)} 个音色")
    return res
