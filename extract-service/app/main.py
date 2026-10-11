"""Extract Service - Lightweight watermark extraction component"""
import uuid
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from blind_watermark import WaterMark

app = FastAPI(title="Video Blind Watermark - Extract Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)


def extract_watermark_from_image(
    image_path: str,
    password_img: int,
    password_wm: int,
    wm_bit_len: int
) -> str:
    if wm_bit_len <= 0:
        raise ValueError("wm_bit_len 必须大于 0")

    bwm = WaterMark(password_img=password_img, password_wm=password_wm)
    result = bwm.extract(image_path, wm_shape=wm_bit_len, mode="str")
    return result or ""


@app.get("/")
async def index():
    return {
        "service": "extract",
        "description": "独立的盲水印提取组件",
        "usage": "POST /api/extract with file, password_img, password_wm, wm_bit_len"
    }


@app.post("/api/extract")
async def extract_from_screenshot(
    file: UploadFile = File(...),
    password_img: int = Form(...),
    password_wm: int = Form(...),
    wm_bit_len: int = Form(...),
):
    """
    从截图提取盲水印。
    需要提供嵌入时使用的 password_img、password_wm 和 wm_bit_len。
    """
    if not file.filename:
        raise HTTPException(400, "未上传图片")

    if wm_bit_len <= 0:
        raise HTTPException(400, "wm_bit_len 必须大于 0")

    temp_path = UPLOADS_DIR / f"extract_{uuid.uuid4()}.png"
    with temp_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        result = extract_watermark_from_image(
            str(temp_path),
            password_img=password_img,
            password_wm=password_wm,
            wm_bit_len=wm_bit_len,
        )
        return {"watermark": result}
    except Exception as e:
        raise HTTPException(500, f"提取失败: {str(e)}")
    finally:
        temp_path.unlink(missing_ok=True)


@app.get("/health")
async def health():
    return {"status": "ok"}
