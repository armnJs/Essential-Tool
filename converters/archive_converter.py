import io
import os
import zipfile
import tarfile

def convert_archive(input_bytes: bytes, src_ext: str, target_ext: str, filename: str = "file", options: dict = None) -> tuple[bytes, str, str]:
    """
    Handle archive creation and extraction.
    Returns (output_bytes, mime_type, target_ext).
    """
    if options is None:
        options = {}

    src = src_ext.lower().replace(".", "")
    target = target_ext.lower().replace(".", "")

    # Convert single/multiple file into ZIP archive
    if target == "zip":
        out_buf = io.BytesIO()
        with zipfile.ZipFile(out_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(filename, input_bytes)
        return out_buf.getvalue(), "application/zip", "zip"

    # Convert single file into TAR / TAR.GZ archive
    if target in ["tar", "gz", "tgz"]:
        out_buf = io.BytesIO()
        mode = "w:gz" if target in ["gz", "tgz"] else "w"
        with tarfile.open(fileobj=out_buf, mode=mode) as tf:
            ti = tarfile.TarInfo(name=filename)
            ti.size = len(input_bytes)
            tf.addfile(ti, io.BytesIO(input_bytes))
        mime = "application/gzip" if "gz" in target else "application/x-tar"
        return out_buf.getvalue(), mime, target

    # Unpack ZIP archive into first extracted file or merged text
    if src == "zip":
        with zipfile.ZipFile(io.BytesIO(input_bytes), 'r') as zf:
            names = zf.namelist()
            if names:
                first_file = zf.read(names[0])
                return first_file, "application/octet-stream", target

    raise ValueError(f"Unsupported archive conversion from .{src} to .{target}")
