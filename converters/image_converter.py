import io
import os
from PIL import Image, ImageOps

# Security Guard: Limit max image pixels to prevent decompression pixel bomb attacks
Image.MAX_IMAGE_PIXELS = 50_000_000

SUPPORTED_IMAGE_FORMATS = {
    "png": "PNG",
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "webp": "WEBP",
    "bmp": "BMP",
    "gif": "GIF",
    "ico": "ICO",
    "tiff": "TIFF",
    "tif": "TIFF"
}

def convert_image(input_bytes: bytes, src_ext: str, target_ext: str, options: dict = None) -> tuple[bytes, str]:
    """
    Convert an image from src_ext to target_ext using Pillow.
    Returns (output_bytes, mime_type).
    """
    if options is None:
        options = {}

    src_ext = src_ext.lower().replace(".", "")
    target_ext = target_ext.lower().replace(".", "")

    if target_ext not in SUPPORTED_IMAGE_FORMATS:
        raise ValueError(f"Unsupported target image format: {target_ext}")

    pil_format = SUPPORTED_IMAGE_FORMATS[target_ext]
    
    img = Image.open(io.BytesIO(input_bytes))

    # Apply optional image transformations
    if options.get("grayscale"):
        img = ImageOps.grayscale(img)
    
    if options.get("rotate"):
        try:
            angle = float(options.get("rotate"))
            img = img.rotate(-angle, expand=True)
        except Exception:
            pass

    if options.get("resize_width") or options.get("resize_height") or options.get("width") or options.get("height"):
        try:
            w = int(options.get("resize_width") or options.get("width", img.width))
            h = int(options.get("resize_height") or options.get("height", img.height))
            if w > 10000 or h > 10000:
                raise ValueError("Requested image dimensions exceed maximum allowed size (10000x10000).")
            img = img.resize((w, h), Image.Resampling.LANCZOS)
        except ValueError:
            raise
        except Exception:
            pass

    # Handle transparent channel for formats that don't support RGBA (like JPEG)
    if pil_format == "JPEG":
        if img.mode in ("RGBA", "LA", "P"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "RGBA":
                background.paste(img, mask=img.split()[3])
            else:
                background.paste(img.convert("RGBA"), mask=img.convert("RGBA").split()[3])
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

    output = io.BytesIO()
    save_kwargs = {}

    if pil_format in ("JPEG", "WEBP"):
        quality = int(options.get("quality", 85))
        save_kwargs["quality"] = quality

    if pil_format == "ICO":
        # ICO needs small size max 256x256
        if img.width > 256 or img.height > 256:
            img = img.resize((256, 256), Image.Resampling.LANCZOS)
        img.save(output, format="ICO", sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
    else:
        img.save(output, format=pil_format, **save_kwargs)

    mimetypes = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "webp": "image/webp",
        "bmp": "image/bmp",
        "gif": "image/gif",
        "ico": "image/x-icon",
        "tiff": "image/tiff"
    }

    return output.getvalue(), mimetypes.get(target_ext, f"image/{target_ext}")
