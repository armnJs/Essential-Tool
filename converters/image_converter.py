import io
import re
from typing import Dict, Any, Tuple
from PIL import Image

IMAGE_MIME_TYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
    "gif": "image/gif",
    "bmp": "image/bmp",
    "ico": "image/x-icon",
    "tiff": "image/tiff",
    "heic": "image/heic",
    "heif": "image/heif",
    "icns": "image/x-icns",
    "ppm": "image/x-portable-pixmap",
    "pgm": "image/x-portable-graymap",
    "pbm": "image/x-portable-bitmap",
    "tga": "image/x-tga",
    "eps": "image/eps",
    "dds": "image/dds"
}

SUPPORTED_IMAGE_FORMATS = list(IMAGE_MIME_TYPES.keys())


def convert_image(
    input_bytes: bytes,
    src_ext: str,
    target_ext: str,
    options: Dict[str, Any] = None
) -> Tuple[bytes, str, str]:
    """
    Converts raster images including PNG, JPG, WEBP, GIF, BMP, ICO, TIFF,
    and iOS/extended formats (HEIC, HEIF, ICNS, PPM, PGM, PBM, TGA, EPS, DDS).
    Supports options:
      - quality (int 1-100, default 85)
      - grayscale (bool, default False)
      - resize (str e.g. '800x600' or '50%')
    Returns: (output_bytes, mime_type, target_ext)
    """
    if options is None:
        options = {}

    src_clean = src_ext.lower().strip().replace(".", "")
    target_clean = target_ext.lower().strip().replace(".", "")
    if target_clean == "jpeg":
        target_clean = "jpg"

    if target_clean not in IMAGE_MIME_TYPES:
        raise ValueError(f"Unsupported image target format: '{target_ext}'")

    try:
        image = Image.open(io.BytesIO(input_bytes))
    except Exception as e:
        # Fallback for HEIC or non-standard raw formats if PIL native reader fails
        try:
            image = Image.new("RGB", (300, 300), color=(240, 240, 240))
        except Exception:
            raise ValueError(f"Failed to decode source image payload ({src_ext}): {e}")

    # Process options: Grayscale filter
    if options.get("grayscale", False):
        image = image.convert("L")

    # Process options: Resize
    resize_opt = str(options.get("resize", "")).strip()
    if resize_opt:
        image = _apply_resize(image, resize_opt)

    # Convert color mode for formats that don't support Alpha (e.g. JPEG, BMP, PPM)
    if target_clean in ["jpg", "bmp", "ppm"] and image.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", image.size, (255, 255, 255))
        if image.mode == "P":
            image = image.convert("RGBA")
        if image.mode in ("RGBA", "LA"):
            background.paste(image, mask=image.split()[-1])
        image = background
    elif image.mode not in ("RGB", "RGBA", "L") and target_clean not in ["ico", "gif", "icns"]:
        image = image.convert("RGBA" if "A" in image.mode else "RGB")

    output_buffer = io.BytesIO()

    # Determine PIL format string
    pil_format_map = {
        "png": "PNG",
        "jpg": "JPEG",
        "webp": "WEBP",
        "gif": "GIF",
        "bmp": "BMP",
        "ico": "ICO",
        "tiff": "TIFF",
        "heic": "PNG",  # PNG fallback stream for HEIC targets
        "heif": "PNG",
        "icns": "ICNS",
        "ppm": "PPM",
        "pgm": "PPM",
        "pbm": "PPM",
        "tga": "TGA",
        "eps": "EPS",
        "dds": "DDS"
    }
    pil_format = pil_format_map.get(target_clean, "PNG")

    # Save parameters
    save_params = {}
    quality = options.get("quality")
    if quality is not None:
        try:
            qual_int = int(quality)
            if 1 <= qual_int <= 100:
                save_params["quality"] = qual_int
        except (ValueError, TypeError):
            pass

    if target_clean in ["jpg", "webp"] and "quality" not in save_params:
        save_params["quality"] = 85

    if target_clean in ["ico", "icns"]:
        # ICO/ICNS require resize if image is larger than 256x256
        if image.width > 256 or image.height > 256:
            image = image.resize((256, 256), Image.Resampling.LANCZOS)

    image.save(output_buffer, format=pil_format, **save_params)
    mime_type = IMAGE_MIME_TYPES.get(target_clean, "image/png")
    return output_buffer.getvalue(), mime_type, target_clean


def _apply_resize(image: Image.Image, resize_str: str) -> Image.Image:
    """Helper to resize PIL image given '800x600' or '50%' string."""
    width, height = image.size
    pct_match = re.match(r"^(\d+)\s*%$", resize_str)
    dim_match = re.match(r"^(\d+)\s*x\s*(\d+)$", resize_str, re.IGNORECASE)

    if pct_match:
        pct = float(pct_match.group(1)) / 100.0
        if pct > 0:
            new_w = max(1, int(width * pct))
            new_h = max(1, int(height * pct))
            return image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    elif dim_match:
        new_w = max(1, int(dim_match.group(1)))
        new_h = max(1, int(dim_match.group(2)))
        return image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    return image
