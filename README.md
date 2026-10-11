# Video Blind Watermark Web System

给上传的视频每一帧嵌入自定义盲水印（Invisible Watermark），并支持从截图中提取水印信息。

盲水印肉眼不可见，可用于版权溯源、用户追踪、设备绑定等场景。

## 功能特性

- **逐帧盲水印嵌入**：使用 FFmpeg 拆帧 + `blind-watermark` 库为每一帧嵌入自定义文本
- **自定义水印内容**：支持日期、用户名、设备 ID、订单号等任意文本
- **截图提取**：从视频截图中提取水印（高清截图成功率较高）
- **Web 界面**：简单的上传、查询、提取页面
- **异步处理**：后台任务处理，避免阻塞请求
- **Docker 支持**：一键启动，无需手动安装依赖

## 技术栈

| 组件 | 说明 |
|------|------|
| FastAPI | Web 框架 |
| FFmpeg | 视频拆帧与合成 |
| blind-watermark | 盲水印算法（guofei9987） |
| SQLite | 任务与参数记录 |
| Docker | 容器化部署 |

## 快速开始（Docker）

```bash
# 克隆仓库
git clone https://github.com/gzjoe/video-blind-watermark.git
cd video-blind-watermark

# 构建并启动
docker compose up --build

# 访问
# http://localhost:8000
```

## 本地安装（非 Docker）

### 系统依赖

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install -y ffmpeg python3-pip

# macOS
brew install ffmpeg
```

### Python 依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

浏览器打开 http://localhost:8000

## API 说明

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/videos` | 上传视频并嵌入水印（表单：`file` + `watermark_text`） |
| `GET` | `/api/videos/{task_id}` | 查询任务状态 |
| `GET` | `/api/videos/{task_id}/download` | 下载处理后的水印视频 |
| `POST` | `/api/extract` | 上传截图提取水印（表单：`file` + `task_id` 或 `wm_bit_len`） |

### 示例：上传视频

```bash
curl -X POST http://localhost:8000/api/videos \
  -F "file=@example.mp4" \
  -F "watermark_text=2026-10-11|user123|DEV-abc"
```

### 示例：提取水印

```bash
curl -X POST http://localhost:8000/api/extract \
  -F "file=@screenshot.png" \
  -F "task_id=你的任务ID"
```

## 项目结构

```
video-blind-watermark/
├── app/
│   ├── main.py          # FastAPI 主程序
│   ├── watermark.py     # 水印嵌入/提取逻辑
│   └── database.py      # SQLite 任务记录
├── static/
│   └── index.html       # 前端页面
├── uploads/             # 临时上传目录（运行时创建）
├── outputs/             # 输出视频目录（运行时创建）
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── LICENSE
└── README.md
```

## 注意事项

1. **处理速度**  
   逐帧嵌入计算量较大，长视频可能需要数分钟。建议使用异步队列（当前使用 FastAPI BackgroundTasks）。

2. **截图提取可靠性**  
   - 高清截图（PNG 或高质量 JPEG）：成功率较高  
   - 轻度压缩：多数情况可提取  
   - 重度压缩 / 社交平台转发：经常失败

3. **水印容量**  
   普通 1080p 帧大约可嵌入几十到一两百字符，建议控制在 100 字符以内。

4. **密码管理**  
   当前使用固定密码（`1234` / `5678`）。生产环境建议按任务随机生成并安全存储。

5. **资源占用**  
   处理过程中会临时占用磁盘空间（拆帧），处理完成后自动清理。

## 开发与贡献

欢迎提交 Issue 和 Pull Request。

## License

[MIT](LICENSE)
