# Video Blind Watermark System

视频盲水印系统，拆分为两个独立组件，支持分开部署：

1. **Embed Service（嵌入服务）**：独立 Web 系统，负责上传视频并给每一帧嵌入自定义盲水印
2. **Extract Service（提取组件）**：轻量组件，部署在另一台 Ubuntu 上，从截图中提取水印

## 架构

```
┌─────────────────────┐         ┌────────────────────┐
│   Embed Service     │         │   Extract Service   │
│   (Web 系统)         │         │   (Ubuntu 组件)      │
│                     │         │                     │
│  - 上传视频          │  参数   │  - 接收截图          │
│  - 逐帧嵌入盲水印     │ ──────> │  - 提取水印          │
│  - 返回提取参数       │         │  - 返回水印内容      │
│  - 下载水印视频       │         │                     │
└─────────────────────┘         └────────────────────┘
     端口 8000                       端口 8001
```

两个服务通过**约定的密码参数**（`password_img`、`password_wm`、`wm_bit_len`）协作，无需共享数据库。

## 快速开始

### 1. 启动嵌入服务（Embed Service）

```bash
cd embed-service
docker compose up --build
```

访问 http://localhost:8000

### 2. 启动提取服务（Extract Service）

在另一台 Ubuntu 上：

```bash
cd extract-service
docker compose up --build
```

服务监听 http://localhost:8001

## 使用流程

1. 在 **Embed Service** 上传视频并填写水印文本
2. 查询任务状态，获取提取参数：
   - `password_img`
   - `password_wm`
   - `wm_bit_len`
3. 下载水印视频
4. 在 **Extract Service** 上传视频截图，并提交上述三个参数，即可提取水印

### 提取示例

```bash
curl -X POST http://EXTRACT_SERVER:8001/api/extract \
  -F "file=@screenshot.png" \
  -F "password_img=1234" \
  -F "password_wm=5678" \
  -F "wm_bit_len=XXX"
```

## 目录结构

```
.
├── embed-service/          # 嵌入服务（独立 Web 系统）
│   ├── app/
│   ├── static/
│   ├── Dockerfile
│   └── docker-compose.yml
├── extract-service/        # 提取组件（独立部署）
│   ├── app/
│   ├── Dockerfile
│   └── docker-compose.yml
├── LICENSE
└── README.md
```

## 注意事项

1. **密码一致性**：两个服务必须使用相同的 `password_img` 和 `password_wm`（当前默认均为 1234 / 5678）
2. **wm_bit_len**：由嵌入服务生成并返回，提取时必须准确提供
3. **截图质量**：高清截图成功率较高，重度压缩可能失败
4. **处理速度**：逐帧嵌入较慢，长视频需等待

## License

[MIT](LICENSE)
