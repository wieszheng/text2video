# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
@Version  : Python 3.12
@Time     : 2025/6/16 21:38
@Author   : wieszheng
@Software : PyCharm
"""
import os
import sys
import time

import urllib.parse

import requests
from PIL import ImageFont

from moviepy import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
from moviepy.video.tools import subtitles
from moviepy.video.tools.subtitles import SubtitlesClip

from app.schemas.video import VideoGenerateParams
from app.services.voice import generate_voice
from loguru import logger

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


def task_dir(sub_dir: str = "") -> str:
    d = os.path.join(ROOT, "tasks")
    if sub_dir:
        d = os.path.join(d, sub_dir)

    os.makedirs(d, exist_ok=True)

    return d


def merge_subtitles(subtitles):
    """
    合并单字字幕为完整句子，并添加标点符号和英文空格
    """
    if not subtitles:
        return []

    merged = []
    current_text = ""
    start_time = subtitles[0][0][0]
    end_time = subtitles[0][0][1]

    # 定义标点符号规则
    punctuation_rules = {
        '。': 0.5,  # 句号：较长停顿
        '，': 0.3,  # 逗号：中等停顿
        '、': 0.2,  # 顿号：较短停顿
        '？': 0.5,  # 问号：较长停顿
        '！': 0.5,  # 感叹号：较长停顿
        '；': 0.4,  # 分号：较长停顿
        '：': 0.3,  # 冒号：中等停顿
    }

    def is_english_char(char):
        """判断是否为英文字符"""
        return ord('a') <= ord(char.lower()) <= ord('z')

    def is_chinese_char(char):
        """判断是否为中文字符"""
        return '\u4e00' <= char <= '\u9fff'

    def should_add_space(prev_char, current_char):
        """判断是否需要在两个字符之间添加空格"""
        if not prev_char or not current_char:
            return False
        # 如果前一个字符是英文，当前字符也是英文，添加空格
        if is_english_char(prev_char) and is_english_char(current_char):
            return True
        # 如果前一个字符是中文，当前字符是英文，添加空格
        if is_chinese_char(prev_char) and is_english_char(current_char):
            return True
        # 如果前一个字符是英文，当前字符是中文，添加空格
        if is_english_char(prev_char) and is_chinese_char(current_char):
            return True
        return False

    for i, ((ta, tb), text) in enumerate(subtitles):
        # 检查是否需要添加空格
        if current_text and should_add_space(current_text[-1], text[0]):
            current_text += " "
        current_text += text

        # 检查是否需要添加标点符号
        should_add_punctuation = False
        punctuation = None

        # 如果是最后一个字幕
        if i == len(subtitles) - 1:
            should_add_punctuation = True
            punctuation = '。'
        else:
            # 检查与下一个字幕的时间间隔
            time_gap = subtitles[i + 1][0][0] - tb

            # 根据时间间隔选择合适的标点符号
            for p, threshold in punctuation_rules.items():
                if time_gap >= threshold:
                    should_add_punctuation = True
                    punctuation = p
                    break

        # 添加标点符号
        if should_add_punctuation and punctuation:
            current_text += punctuation

        # 如果是最后一个字幕，或者是下一个字幕的开始时间与当前字幕的结束时间有间隔
        if i == len(subtitles) - 1 or subtitles[i + 1][0][0] - tb > 0.1:
            merged.append(((start_time, tb), current_text))
            if i < len(subtitles) - 1:
                start_time = subtitles[i + 1][0][0]
                current_text = ""

    return merged


async def generate_video(body: VideoGenerateParams):
    task_id = body.task_id or str(int(time.time()))
    task_dir_path = task_dir(task_id)

    image_file = os.path.join(task_dir_path, "image.png")
    audio_file = os.path.join(task_dir_path, "audio.mp3")
    subtitle_file = os.path.join(task_dir_path, "subtitle.srt")

    params = {
        "width": 1280,
        "height": 720,
        "seed": 389182035,
        "model": "flux",
        "nologo": True,
        "enhance": True,
        # "transparent": "true", # Optional - generates transparent background (gptimage model only)
        # "referrer": "MyPythonApp" # Optional
    }

    encoded_prompt = urllib.parse.quote(body.text)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
    res = requests.get(url, params=params, timeout=300)
    res.raise_for_status()
    with open(image_file, "wb") as f:
        f.write(res.content)

    audio_file, subtitle_file = await generate_voice(
        body.text,
        body.voice_name,
        body.voice_rate,
        audio_file,
        subtitle_file
    )
    # 获取字幕的总时长
    subs = subtitles.file_to_subtitles(subtitle_file, encoding="utf-8")
    # 合并单字字幕
    merged_subs = merge_subtitles(subs)
    subtitle_duration = max([tb for ((ta, tb), txt) in merged_subs])
    logger.debug(f"subtitle_duration: {subtitle_duration}")

    image_clip = ImageClip(image_file)
    origin_image_w, origin_image_h = image_clip.size  # 获取放大后的图片尺寸
    image_scale = 1.2
    image_clip = image_clip.resized((origin_image_w * image_scale, origin_image_h * image_scale))
    # 确保图片视频时长至少和字幕一样长
    image_clip = image_clip.with_duration(subtitle_duration)

    width_diff = origin_image_w * (image_scale - 1)
    clips = []

    def debug_position(t):
        # print(f"当前时间 t = {t}", subtitle_duration, width_diff, width_diff / subtitle_duration * t)
        return (-width_diff / subtitle_duration * t, 'center')

    image_clip = image_clip.with_position(debug_position)
    audio_clip = AudioFileClip(audio_file)
    image_clip = image_clip.with_audio(audio_clip)

    font_path = os.path.join(ROOT, "fonts", "MicrosoftYaHeiNormal.ttc")
    if not os.path.exists(font_path):
        logger.warning("Font file not found, using default font")
    # 添加字幕
    if os.path.exists(subtitle_file):
        logger.info(f"Loading subtitle file: {subtitle_file}")

        def create_text_clip(subtitle_item):
            phrase = subtitle_item[1]
            # 计算字幕最大宽度，留出左右边距
            max_width = origin_image_w * 0.85  # 使用85%的视频宽度，留出边距
            # wrapped_txt, txt_height = wrap_text(
            #     phrase, font=font_path, max_width=max_width, fontsize=30
            # )


            # 创建字幕剪辑
            _clip = TextClip(
                text=phrase,
                font=font_path,
                font_size=30,
                color="white",
                stroke_color="black",
                stroke_width=2
            )

            duration = subtitle_item[0][1] - subtitle_item[0][0]
            _clip = _clip.with_start(subtitle_item[0][0])
            _clip = _clip.with_end(subtitle_item[0][1])
            _clip = _clip.with_duration(duration)

            # 计算字幕位置，确保在视频底部且不会超出边界
            bottom_margin = 40  # 底部边距
            max_height = origin_image_h * 0.8

            # 如果字幕高度超过最大高度，调整字体大小
            if _clip.h > max_height:
                scale_factor = max_height / _clip.h
                new_fontsize = int(30 * scale_factor)
                _clip = TextClip(
                    text=phrase,
                    font_size=new_fontsize,
                    color="white",
                    stroke_color="black",
                    stroke_width=2
                )

            # 计算字幕位置
            y_position = origin_image_h - _clip.h - bottom_margin
            _clip = _clip.with_position(("center", y_position))

            return _clip

        text_clips = []
        for item in merged_subs:  # 使用合并后的字幕
            clip = create_text_clip(subtitle_item=item)
            text_clips.append(clip)
        video_clip = CompositeVideoClip([image_clip, *text_clips], (origin_image_w, origin_image_h))
        clips.append(video_clip)

    logger.info("Merging all clips")
    final_clip = concatenate_videoclips(clips)
    video_file = os.path.join(task_dir_path, "video.mp4")
    logger.info(f"Writing video to {video_file}")
    final_clip.write_videofile(video_file, fps=24, codec='libx264', audio_codec='aac')

    return video_file, final_clip.duration


if __name__ == '__main__':
    print(ROOT)