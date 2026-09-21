import io
import os
import zipfile
import tarfile
from typing import Dict, Any, Tuple

ARCHIVE_MIME_TYPES = {
    "zip": "application/zip",
    "tar": "application/x-tar",
    "gz": "application/gzip",
    "tar.gz": "application/gzip"
}

SUPPORTED_ARCHIVE_FORMATS = list(ARCHIVE_MIME_TYPES.keys())


def convert_archive(
    input_bytes: bytes,
    filename: str,
    src_ext: str,
    target_ext: str,
    options: Dict[str, Any] = None
) -> Tuple[bytes, str, str]:
    """
    Handles compression (packaging input bytes into ZIP/TAR) and extraction.
    Returns: (output_bytes, mime_type, target_ext)
    """
    if options is None:
        options = {}

    src_clean = src_ext.lower().strip().replace(".", "")
    target_clean = target_ext.lower().strip().replace(".", "")

    if target_clean not in ARCHIVE_MIME_TYPES and target_clean not in ["txt", "png", "jpg"]:
        target_clean = "zip"

    # Extraction route: If source is ZIP and target is not an archive
    if src_clean == "zip" and target_clean not in ARCHIVE_MIME_TYPES:
        return _extract_zip(input_bytes, target_clean)

    # Packaging route: Compress payload into ZIP or TAR
    safe_name = os.path.basename(filename) if filename else "file"
    if not safe_name or safe_name == "file":
        safe_name = f"document.{src_clean}"

    if target_clean in ["tar", "gz", "tar.gz"]:
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w:gz") as tar:
            info = tarfile.TarInfo(name=safe_name)
            info.size = len(input_bytes)
            tar.addfile(info, io.BytesIO(input_bytes))
        return buf.getvalue(), ARCHIVE_MIME_TYPES["tar.gz"], "tar.gz"
    else:
        # ZIP Archive
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(safe_name, input_bytes)
        return buf.getvalue(), ARCHIVE_MIME_TYPES["zip"], "zip"


def _extract_zip(input_bytes: bytes, target_clean: str) -> Tuple[bytes, str, str]:
    """Extracts first file or concatenated text from ZIP archive."""
    try:
        with zipfile.ZipFile(io.BytesIO(input_bytes), "r") as zf:
            names = zf.namelist()
            if not names:
                raise ValueError("ZIP archive is empty.")
            # Read first file in archive
            first_name = names[0]
            content = zf.read(first_name)
            return content, "application/octet-stream", target_clean
    except Exception as e:
        raise ValueError(f"Failed to extract payload from ZIP archive: {e}")
