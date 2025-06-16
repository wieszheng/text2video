根据你的项目结构和代码内容，这是一个基于 FastAPI 构建的文本转视频服务系统。以下是一个推荐的 [README.md](file://D:\Workcode\python\text2video\README.md) 文件模板：

---

# Text-to-Video API

一个使用 FastAPI 构建的文本转视频服务，支持通过文字生成语音、图像并最终合成视频。

## 📁 项目目录结构

```
app/
├── api/              # API 路由
│   ├── video.py      # 视频生成接口
│   └── voice.py      # 语音获取接口
├── schemas/          # 请求/响应数据模型
│   ├── video.py
│   └── voice.py
└── services/         # 核心业务逻辑
    ├── video.py      # 视频生成逻辑
    └── voice.py      # 语音生成逻辑
```


## ⚙️ 技术栈

- **FastAPI**：用于构建 RESTful API
- **Edge TTS**：用于文本转语音
- **Pollinations AI**：用于文本生成图片
- **MoviePy**：用于处理视频与字幕合成
- **Pydantic**：用于数据校验
- **Loguru**：用于日志记录

## 🧩 功能概述

### 获取语音列表

```http
GET /api/voice/voices
```


返回 Edge-TTS 支持的所有语音种类。

### 文本生成视频

```http
POST /api/video/generate
```


请求体参数如下：

| 字段名        | 类型     | 默认值                   | 描述             |
|---------------|----------|---------------------------|------------------|
| [text](file://D:\Workcode\python\text2video\app\schemas\video.py#L14-L16)        | `str`    | 自动填充示例文本          | 需要转换的文本   |
| [task_id](file://D:\Workcode\python\text2video\app\schemas\video.py#L17-L17)     | `str`    | 自动生成                  | 任务 ID          |
| [voice_name](file://D:\Workcode\python\text2video\app\schemas\video.py#L19-L19)  | `str`    | `"zh-CN-XiaoxiaoNeural"`  | 使用的语音名称   |
| [voice_rate](file://D:\Workcode\python\text2video\app\schemas\video.py#L20-L20)  | `float`  | `1.0`                     | 语速             |
| [resolution](file://D:\Workcode\python\text2video\app\schemas\video.py#L21-L21)  | `str`    | `"1920*1080"`             | 视频分辨率       |

输出结果包含：
- `video_path`: 合成后的视频文件路径。
- `duration`: 视频总时长。

## 🔧 安装与运行

确保已安装 Python 3.12 及以上版本，并执行：

```bash
uv venv
uv pip install -e .

```


访问 `http://localhost:8000/docs` 查看交互式 API 文档。

## 📝 使用说明

1. 获取可用语音列表：

   ```bash
   curl http://localhost:8000/api/voice/voices
   ```


2. 生成视频：

   ```bash
   curl -X POST http://localhost:8000/api/video/generate \
        -H "Content-Type: application/json" \
        -d '{
            "text": "春天来了，万物复苏。",
            "voice_name": "zh-CN-YunxiNeural",
            "voice_rate": 1.2,
            "resolution": "1280*720"
        }'
   ```

你可以在 README.md 中添加一个 **预览视图**（Preview）章节，展示生成视频的效果或系统界面截图。由于目前没有上传图片，我将提供一个通用模板，你可以根据实际效果补充内容。

以下是更新后的 [README.md](file://D:\Workcode\python\text2video\README.md) 预览视图部分：

---

## 🖼️ 预览视图

### 输出结果
- 自动生成图像（基于 [Pollinations AI](https://image.pollinations.ai/)）
- 使用 Edge TTS 生成语音并同步字幕
- 合成最终视频，包含：
  - 背景图片平移动画
  - 字幕自动换行与排版
  - 视频时长自适应音频长度

<video width="640" height="360" controls>
  <source src="/docs/generated-video-1750083906912.mp4" type="video/mp4">
  您的浏览器不支持视频播放。
</video>

## 🤝 贡献指南

欢迎提交 Pull Request 和 Issue！请遵循 PEP8 编码规范，保持模块化设计风格。

## 📄 许可证

MIT License

---