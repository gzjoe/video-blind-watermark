"""Embed Service - Watermark logic"""
import subprocess
import shutil
from pathlib import Path
from blind_watermark import WaterMark


def embed_watermark_to_video(
    input_video: str,
    output_video: str,
    wm_text: str,
    password_img: int = 1234,
    password_wm: int = 5678,
    work_dir: Path | None = None
) -> int:
    if work_dir is None:
        work_dir = Path("/tmp/wm_work")
    frames_dir = work_dir / "frames"
    frames_wm_dir = work_dir / "frames_wm"

    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    if frames_wm_dir.exists():
        shutil.rmtree(frames_wm_dir)
    frames_dir.mkdir(parents=True)
    frames_wm_dir.mkdir(parents=True)

    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", input_video, "-q:v", "2",
             str(frames_dir / "frame_%05d.png")],
            check=True, capture_output=True
        )

        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=r_frame_rate", "-of", "default=noprint_wrappers=1:nokey=1",
             input_video],
            capture_output=True, text=True, check=True
        )
        fps = probe.stdout.strip() or "25"

        bwm = WaterMark(password_img=password_img, password_wm=password_wm)
        frame_files = sorted(frames_dir.glob("*.png"))
        if not frame_files:
            raise RuntimeError("未提取到任何帧")

        wm_bit_len = None
        for frame in frame_files:
            bwm.read_img(str(frame))
            bwm.read_wm(wm_text, mode="str")
            out_path = frames_wm_dir / frame.name
            bwm.embed(str(out_path))
            if wm_bit_len is None:
                wm_bit_len = len(bwm.wm_bit)

        subprocess.run(
            ["ffmpeg", "-y", "-framerate", fps,
             "-i", str(frames_wm_dir / "frame_%05d.png"),
             "-i", input_video,
             "-map", "0:v:0", "-map", "1:a:0?",
             "-c:v", "libx264", "-crf", "23", "-preset", "medium",
             "-c:a", "copy", "-pix_fmt", "yuv420p",
             "-movflags", "+faststart",
             output_video],
            check=True, capture_output=True
        )

        return wm_bit_len or 0

    finally:
        shutil.rmtree(frames_dir, ignore_errors=True)
        shutil.rmtree(frames_wm_dir, ignore_errors=True)
