# Video Blind Watermark Web System

给上传的视频每一帧嵌入自定义盲水印，并支持从截图中提取水印信息。

## 功能

- 上传视频 + 自定义水印文本（日期、用户名、设备ID等）
- 异步处理：FFmpeg 拆帧 → 逐帧嵌入盲水印 → 合成视频
- 从截图提取水印
- 简单 Web 界面

## 技术栈

- FastAPI
- FFmpeg
- blind-watermark (guofei9987)
- SQLite（记录任务与水印参数）

## 安装

```bash
# 安装系统依赖
# Ubuntu/Debian
sudo apt update && sudo apt install -y ffmpeg python3-pip

# 安装 Python 依赖
pip install -r requirements.txt
```

## 运行

```bash
cd video-blind-watermark
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

浏览器打开 http://localhost:8000

## API

- `POST /api/videos` - 上传视频并嵌入水印
- `GET /api/videos/{task_id}` - 查询处理状态
- `GET /api/videos/{task_id}/download` - 下载水印视频
- `POST /api/extract` - 上传截图提取水印

## 注意事项

1. **处理速度**：逐帧嵌入较慢，长视频需要耐心等待。
2. **截图提取**：高清截图成功率较高，重度压缩（微信转发等）可能失败。
3. **容量**：自定义文本建议控制在 100 字符以内。
4. **密码**：系统统一使用密码，提取时自动匹配。

## 项目结构

```
video-blind-watermark/
├── app/
│   ├── main.py          # FastAPI 主程序
│   ├── watermark.py     # 水印嵌入/提取逻辑
│   └── database.py      # 简单任务记录
├── static/
│   └── index.html       # 前端页面
├── uploads/             # 临时上传目录
├── outputs/             # 输出视频目录
├── requirements.txt
└── README.md
```
