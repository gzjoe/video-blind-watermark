"""Embed Service - FastAPI main"""
import uuid
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db, create_task, update_task, get_task
from .watermark import embed_watermark_to_video

app = FastAPI(title="Video Blind Watermark - Embed Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"
STATIC_DIR = BASE_DIR / "static"

UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

DEFAULT_PASSWORD_IMG = 1234
DEFAULT_PASSWORD_WM = 5678


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


def process_video_task(task_id: str, input_path: str, output_path: str, wm_text: str):
    try:
        update_task_sync(task_id, "processing")
        wm_bit_len = embed_watermark_to_video(
            input_video=input_path,
            output_video=output_path,
            wm_text=wm_text,
            password_img=DEFAULT_PASSWORD_IMG,
            password_wm=DEFAULT_PASSWORD_WM,
        )
        update_task_sync(task_id, "completed", output_path=output_path, wm_bit_len=wm_bit_len)
    except Exception as e:
        update_task_sync(task_id, "failed", error_message=str(e))
    finally:
        Path(input_path).unlink(missing_ok=True)


def update_task_sync(task_id: str, status: str, output_path: str = None,
                     wm_bit_len: int = None, error_message: str = None):
    import asyncio
    asyncio.run(update_task(task_id, status, output_path, wm_bit_len, error_message))


@app.post("/api/videos")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    watermark_text: str = Form(...),
):
    if not file.filename:
        raise HTTPException(400, "未选择文件")

    task_id = str(uuid.uuid4())
    ext = Path(file.filename).suffix.lower() or ".mp4"
    input_path = UPLOADS_DIR / f"{task_id}{ext}"
    output_path = OUTPUTS_DIR / f"{task_id}_wm.mp4"

    with input_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    await create_task(
        task_id=task_id,
        original_filename=file.filename,
        watermark_text=watermark_text,
        password_img=DEFAULT_PASSWORD_IMG,
        password_wm=DEFAULT_PASSWORD_WM,
    )

    background_tasks.add_task(
        process_video_task,
        task_id,
        str(input_path),
        str(output_path),
        watermark_text,
    )

    return {"task_id": task_id, "message": "任务已提交，正在处理中"}


@app.get("/api/videos/{task_id}")
async def get_video_status(task_id: str):
    task = await get_task(task_id)
    if not task:
        raise HTTPException(404, "任务不存在")
    # 返回提取所需参数（供独立提取服务使用）
    return {
        "task_id": task["id"],
        "status": task["status"],
        "original_filename": task["original_filename"],
        "watermark_text": task["watermark_text"],
        "password_img": task["password_img"],
        "password_wm": task["password_wm"],
        "wm_bit_len": task["wm_bit_len"],
        "error_message": task["error_message"],
        "created_at": task["created_at"],
    }


@app.get("/api/videos/{task_id}/download")
async def download_video(task_id: str):
    task = await get_task(task_id)
    if not task or task["status"] != "completed":
        raise HTTPException(400, "视频尚未处理完成")
    output_path = Path(task["output_path"])
    if not output_path.exists():
        raise HTTPException(404, "输出文件不存在")
    return FileResponse(
        output_path,
        filename=f"watermarked_{task['original_filename']}",
        media_type="video/mp4",
    )


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
