import os
import io
from typing import Dict, Any, List, Tuple

from converters.image_converter import convert_image, SUPPORTED_IMAGE_FORMATS, IMAGE_MIME_TYPES
from converters.doc_converter import convert_document, SUPPORTED_DOC_FORMATS, DOC_MIME_TYPES
from converters.data_converter import convert_data, SUPPORTED_DATA_FORMATS, DATA_MIME_TYPES
from converters.audio_converter import convert_audio_or_tts, SUPPORTED_AUDIO_FORMATS, AUDIO_MIME_TYPES
from converters.archive_converter import convert_archive, SUPPORTED_ARCHIVE_FORMATS, ARCHIVE_MIME_TYPES
from converters.video_converter import convert_video, SUPPORTED_VIDEO_FORMATS, VIDEO_MIME_TYPES

# Master Conversion Matrix / Target Map
CONVERSION_TARGETS: Dict[str, List[str]] = {
    # Video & iOS Video Formats
    "mp4": ["mkv", "avi", "webm", "mov", "gif", "mp3", "wav", "zip"],
    "mov": ["mp4", "mkv", "avi", "webm", "gif", "mp3", "wav", "zip"],
    "m4v": ["mp4", "mov", "webm", "gif", "mp3", "zip"],
    "mkv": ["mp4", "avi", "webm", "gif", "mp3", "zip"],
    "avi": ["mp4", "mkv", "webm", "gif", "mp3", "zip"],
    "webm": ["mp4", "mkv", "avi", "gif", "mp3", "zip"],

    # Image & iOS Image Formats
    "png": ["jpg", "webp", "gif", "bmp", "ico", "icns", "tiff", "pdf", "zip"],
    "jpg": ["png", "webp", "gif", "bmp", "ico", "icns", "tiff", "pdf", "zip"],
    "jpeg": ["png", "webp", "gif", "bmp", "ico", "icns", "tiff", "pdf", "zip"],
    "webp": ["png", "jpg", "gif", "bmp", "ico", "tiff", "pdf", "zip"],
    "gif": ["png", "jpg", "webp", "bmp", "ico", "mp4", "pdf", "zip"],
    "bmp": ["png", "jpg", "webp", "gif", "ico", "pdf", "zip"],
    "ico": ["png", "jpg", "webp", "bmp", "pdf", "zip"],
    "tiff": ["png", "jpg", "webp", "pdf", "zip"],
    "heic": ["jpg", "png", "webp", "pdf", "zip"],
    "heif": ["jpg", "png", "webp", "pdf", "zip"],
    "icns": ["png", "ico", "jpg", "zip"],
    "ppm": ["png", "jpg", "bmp", "zip"],
    "pgm": ["png", "jpg", "bmp", "zip"],
    "pbm": ["png", "jpg", "bmp", "zip"],
    "tga": ["png", "jpg", "bmp", "zip"],
    "eps": ["png", "pdf", "svg", "zip"],
    "dds": ["png", "jpg", "zip"],

    # Document & Apple iWork Formats
    "pdf": ["docx", "txt", "html", "md", "zip"],
    "docx": ["pdf", "txt", "html", "md", "zip"],
    "txt": ["pdf", "docx", "html", "md", "csv", "json", "mp3", "wav", "zip"],
    "md": ["pdf", "docx", "html", "txt", "mp3", "wav", "zip"],
    "html": ["pdf", "docx", "txt", "md", "zip"],
    "pages": ["pdf", "docx", "txt", "zip"],
    "numbers": ["xlsx", "csv", "json", "pdf", "zip"],
    "key": ["pdf", "txt", "zip"],
    "webloc": ["txt", "html", "zip"],
    "rtf": ["docx", "pdf", "txt", "zip"],
    "epub": ["txt", "pdf", "html", "zip"],

    # Spreadsheet Formats
    "xlsx": ["csv", "tsv", "html", "json", "xml", "sql", "md", "txt", "parquet", "zip"],
    "xls": ["csv", "tsv", "html", "json", "xml", "sql", "md", "txt", "zip"],
    "csv": ["xlsx", "tsv", "json", "yaml", "xml", "sql", "vcf", "ndjson", "parquet", "html", "md", "txt", "zip"],
    "tsv": ["xlsx", "csv", "json", "yaml", "xml", "sql", "ndjson", "parquet", "html", "md", "txt", "zip"],

    # Jupyter Notebook
    "ipynb": ["py", "html", "md", "pdf", "docx", "txt", "zip"],

    # Data & iOS Data Formats
    "json": ["yaml", "xml", "csv", "tsv", "sql", "plist", "toml", "ndjson", "parquet", "base64", "txt", "zip"],
    "yaml": ["json", "xml", "csv", "tsv", "sql", "plist", "toml", "base64", "txt", "zip"],
    "yml": ["json", "xml", "csv", "tsv", "sql", "plist", "toml", "base64", "txt", "zip"],
    "xml": ["json", "yaml", "csv", "tsv", "sql", "plist", "txt", "zip"],
    "plist": ["json", "yaml", "xml", "csv", "txt", "zip"],
    "vcf": ["csv", "json", "txt", "zip"],
    "toml": ["json", "yaml", "xml", "txt", "zip"],
    "ndjson": ["json", "csv", "tsv", "parquet", "zip"],
    "parquet": ["csv", "json", "tsv", "ndjson", "zip"],
    "ini": ["json", "yaml", "txt", "zip"],
    "sql": ["json", "csv", "txt", "zip"],
    "base64": ["json", "txt", "zip"],

    # Audio & iOS Audio Formats
    "wav": ["mp3", "m4a", "flac", "ogg", "aac", "zip"],
    "mp3": ["wav", "m4a", "flac", "ogg", "aac", "zip"],
    "m4a": ["mp3", "wav", "aac", "flac", "zip"],
    "caf": ["wav", "mp3", "m4a", "zip"],
    "aac": ["mp3", "wav", "m4a", "zip"],
    "flac": ["wav", "mp3", "m4a", "zip"],
    "ogg": ["mp3", "wav", "m4a", "zip"],

    # Archives
    "zip": ["tar.gz", "txt", "png", "pdf"]
}

DEFAULT_FALLBACK_TARGETS = ["zip", "txt", "base64"]


def get_allowed_targets(src_ext: str) -> List[str]:
    """Returns list of supported target format extensions for a given source extension."""
    clean_src = src_ext.lower().strip().replace(".", "")
    return CONVERSION_TARGETS.get(clean_src, DEFAULT_FALLBACK_TARGETS)


def process_conversion(
    input_bytes: bytes,
    filename: str,
    target_format: str,
    options: Dict[str, Any] = None
) -> Tuple[bytes, str, str]:
    """
    Main conversion registry dispatcher.
    Routes input stream to domain converters based on format rules.
    Returns: (output_bytes, mime_type, final_filename)
    """
    if options is None:
        options = {}

    if not input_bytes:
        raise ValueError("Conversion payload is empty (0 bytes).")

    base_name, raw_ext = os.path.splitext(filename)
    src_ext = raw_ext.replace(".", "").lower().strip() or "txt"
    if not base_name:
        base_name = "converted_file"

    target_clean = target_format.lower().strip().replace(".", "")
    if target_clean == "jpeg":
        target_clean = "jpg"

    # Rule 1: Archives & Compression Route
    if target_clean in ["zip", "tar", "gz", "tar.gz"] or src_ext == "zip":
        out_bytes, mime, out_ext = convert_archive(input_bytes, filename, src_ext, target_clean, options)
        out_filename = f"{base_name}.{out_ext}"
        return out_bytes, mime, out_filename

    # Rule 2: Video Processing Route (MP4, MOV, M4V, MKV, AVI, WEBM, GIF)
    if src_ext in SUPPORTED_VIDEO_FORMATS or target_clean in ["mp4", "mkv", "avi", "webm", "m4v"]:
        if src_ext not in ["png", "jpg", "jpeg", "txt", "json", "pdf", "docx"]:
            out_bytes, mime, out_ext = convert_video(input_bytes, src_ext, target_clean, options)
            out_filename = f"{base_name}.{out_ext}"
            return out_bytes, mime, out_filename

    # Rule 3: Image Processing Route
    if src_ext in SUPPORTED_IMAGE_FORMATS and target_clean in SUPPORTED_IMAGE_FORMATS:
        out_bytes, mime, out_ext = convert_image(input_bytes, src_ext, target_clean, options)
        out_filename = f"{base_name}.{out_ext}"
        return out_bytes, mime, out_filename

    # Rule 4: Image to PDF Route
    if src_ext in SUPPORTED_IMAGE_FORMATS and target_clean == "pdf":
        out_bytes, mime, out_ext = convert_image(input_bytes, src_ext, "pdf", options)
        out_filename = f"{base_name}.pdf"
        return out_bytes, "application/pdf", out_filename

    # Rule 5: Text to Audio / Speech (TTS) Route
    if target_clean in ["mp3", "wav", "m4a"] and src_ext in ["txt", "md", "html", "doc", "docx", "pdf"]:
        out_bytes, mime, out_ext = convert_audio_or_tts(input_bytes, src_ext, target_clean, options)
        out_filename = f"{base_name}.{out_ext}"
        return out_bytes, mime, out_filename

    # Rule 6: Audio Processing Route
    if src_ext in SUPPORTED_AUDIO_FORMATS and target_clean in SUPPORTED_AUDIO_FORMATS:
        out_bytes, mime, out_ext = convert_audio_or_tts(input_bytes, src_ext, target_clean, options)
        out_filename = f"{base_name}.{out_ext}"
        return out_bytes, mime, out_filename

    # Rule 7: Document & Spreadsheet Route
    if (src_ext in SUPPORTED_DOC_FORMATS or target_clean in SUPPORTED_DOC_FORMATS) and src_ext not in SUPPORTED_DATA_FORMATS:
        out_bytes, mime, out_ext = convert_document(input_bytes, src_ext, target_clean, options)
        out_filename = f"{base_name}.{out_ext}"
        return out_bytes, mime, out_filename

    # Rule 8: Structured Data Route
    if src_ext in SUPPORTED_DATA_FORMATS or target_clean in SUPPORTED_DATA_FORMATS:
        out_bytes, mime, out_ext = convert_data(input_bytes, src_ext, target_clean, options)
        out_filename = f"{base_name}.{out_ext}"
        return out_bytes, mime, out_filename

    # Default Fallback Document Processing
    out_bytes, mime, out_ext = convert_document(input_bytes, src_ext, target_clean, options)
    out_filename = f"{base_name}.{out_ext}"
    return out_bytes, mime, out_filename
