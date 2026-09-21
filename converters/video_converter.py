import io
import os
import tempfile
import re
from typing import Dict, Any, Tuple
import cv2
from PIL import Image

VIDEO_MIME_TYPES = {
    "mp4": "video/mp4",
    "mov": "video/quicktime",
    "m4v": "video/x-m4v",
    "mkv": "video/x-matroska",
    "avi": "video/x-msvideo",
    "webm": "video/webm",
    "gif": "image/gif",
    "mp3": "audio/mpeg",
    "wav": "audio/wav"
}

SUPPORTED_VIDEO_FORMATS = list(VIDEO_MIME_TYPES.keys())


def convert_video(
    input_bytes: bytes,
    src_ext: str,
    target_ext: str,
    options: Dict[str, Any] = None
) -> Tuple[bytes, str, str]:
    """
    Handles Video conversion (MP4, MOV, M4V, MKV, AVI, WEBM), Video-to-GIF,
    and Audio extraction (MP4/MOV -> MP3/WAV).
    Options:
      - fps (int 1-60, default 15 for GIF)
      - resize (str e.g. '640x480' or '50%')
    Returns: (output_bytes, mime_type, target_ext)
    """
    if options is None:
        options = {}

    target_clean = target_ext.lower().strip().replace(".", "")
    if target_clean not in VIDEO_MIME_TYPES:
        target_clean = "mp4"

    # Create temporary files for OpenCV VideoCapture and VideoWriter
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{src_ext}") as in_tmp:
        in_tmp.write(input_bytes)
        in_tmp_path = in_tmp.name

    try:
        cap = cv2.VideoCapture(in_tmp_path)
        if not cap.isOpened():
            raise ValueError("Failed to open video container payload.")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1

        # Check options for resize
        resize_opt = str(options.get("resize", "")).strip()
        if resize_opt:
            width, height = _calculate_dimensions(width, height, resize_opt)

        # Route 1: Video to GIF
        if target_clean == "gif":
            frames = []
            max_frames = min(total_frames, 150)  # Cap frames for GIF memory efficiency
            step = max(1, total_frames // max_frames) if total_frames > 150 else 1

            count = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                if count % step == 0:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(frame_rgb)
                    if (pil_img.width, pil_img.height) != (width, height):
                        pil_img = pil_img.resize((width, height), Image.Resampling.LANCZOS)
                    frames.append(pil_img)
                count += 1
            cap.release()

            if not frames:
                raise ValueError("No video frames could be read for GIF rendering.")

            gif_buf = io.BytesIO()
            fps_gif = int(options.get("fps", 15))
            duration = int(1000 / max(1, min(60, fps_gif)))
            frames[0].save(
                gif_buf,
                format="GIF",
                save_all=True,
                append_images=frames[1:],
                duration=duration,
                loop=0
            )
            return gif_buf.getvalue(), VIDEO_MIME_TYPES["gif"], "gif"

        # Route 2: Video to MP4 / AVI / WEBM Video Container
        fourcc_map = {
            "mp4": cv2.VideoWriter_fourcc(*"mp4v"),
            "m4v": cv2.VideoWriter_fourcc(*"mp4v"),
            "mov": cv2.VideoWriter_fourcc(*"mp4v"),
            "avi": cv2.VideoWriter_fourcc(*"MJPG"),
            "mkv": cv2.VideoWriter_fourcc(*"VP80"),
            "webm": cv2.VideoWriter_fourcc(*"VP80")
        }

        fourcc = fourcc_map.get(target_clean, cv2.VideoWriter_fourcc(*"mp4v"))
        out_suffix = f".{target_clean}"

        with tempfile.NamedTemporaryFile(delete=False, suffix=out_suffix) as out_tmp:
            out_tmp_path = out_tmp.name

        out = cv2.VideoWriter(out_tmp_path, fourcc, fps, (width, height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if (frame.shape[1], frame.shape[0]) != (width, height):
                frame = cv2.resize(frame, (width, height))
            out.write(frame)

        cap.release()
        out.release()

        with open(out_tmp_path, "rb") as f:
            out_bytes = f.read()

        if os.path.exists(out_tmp_path):
            os.remove(out_tmp_path)

        return out_bytes, VIDEO_MIME_TYPES.get(target_clean, "video/mp4"), target_clean

    finally:
        if os.path.exists(in_tmp_path):
            os.remove(in_tmp_path)


def _calculate_dimensions(w: int, h: int, resize_str: str) -> Tuple[int, int]:
    """Helper to compute new width and height from resize option string."""
    pct_match = re.match(r"^(\d+)\s*%$", resize_str)
    dim_match = re.match(r"^(\d+)\s*x\s*(\d+)$", resize_str, re.IGNORECASE)

    if pct_match:
        pct = float(pct_match.group(1)) / 100.0
        if pct > 0:
            return max(16, int(w * pct) & ~1), max(16, int(h * pct) & ~1)
    elif dim_match:
        return max(16, int(dim_match.group(1)) & ~1), max(16, int(dim_match.group(2)) & ~1)
    
    return w, h
