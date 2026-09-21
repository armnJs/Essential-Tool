import os
import json
import io
import urllib.parse
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Response
from fastapi.responses import StreamingResponse, FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from converters.registry import get_allowed_targets, process_conversion
from converters.watermark import get_provenance_info, OWNER_NAME, encode_zero_width_watermark

app = FastAPI(
    title="OmniConvert Engine",
    description="Universal, local self-hosted file conversion web application",
    version="2.0.0"
)

# CORS middleware with custom Provenance header
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom Provenance Header middleware
@app.middleware("http")
async def add_provenance_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-OmniConvert-Provenance"] = OWNER_NAME
    return response

# Static & Docs directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/docs", StaticFiles(directory=DOCS_DIR), name="docs")

# Unlimited local file processing (no file size restrictions for local server)


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serves the main single-page application frontend."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>OmniConvert Server Running</h1><p>static/index.html not found.</p>")


@app.get("/favicon.ico")
@app.get("/static/favicon.ico")
async def get_favicon():
    """Serves custom website favicon ico."""
    favicon_path = os.path.join(STATIC_DIR, "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path, media_type="image/x-icon")
    return Response(status_code=204)


@app.get("/api/provenance")
async def get_provenance():
    """Returns cryptographic provenance metadata verifying authorship."""
    return get_provenance_info()


@app.get("/api/health")
async def health_check():
    """Health status check endpoint."""
    return {
        "status": "ok",
        "app": "OmniConvert Universal Converter Engine",
        "author": OWNER_NAME,
        "version": "2.0.0",
        "supported_engines": ["image", "document", "data", "audio_tts", "archive"]
    }



@app.get("/api/formats")
async def get_formats(src: str = "txt"):
    """Returns allowed target conversion formats for a given source extension."""
    clean_src = src.lower().strip().replace(".", "")
    allowed = get_allowed_targets(clean_src)
    return {
        "src_format": clean_src,
        "allowed_targets": allowed
    }


@app.post("/api/convert")
async def convert_file(
    file: UploadFile = File(...),
    target_format: str = Form(...),
    options: str = Form(default="{}")
):
    """
    Primary conversion endpoint.
    Receives file binary payload, target_format, and options JSON string.
    Returns binary file stream as attachment.
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file payload provided in request.")

    target_clean = target_format.lower().strip().replace(".", "")
    if not target_clean:
        raise HTTPException(status_code=400, detail="Missing target_format parameter.")

    # Parse options JSON string
    options_dict = {}
    if options:
        try:
            options_dict = json.loads(options)
        except Exception:
            options_dict = {}

    # Read binary payload
    try:
        input_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read upload file stream: {e}")

    if len(input_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes).")

    # Execute conversion dispatcher
    try:
        out_bytes, mime_type, out_filename = process_conversion(
            input_bytes=input_bytes,
            filename=file.filename,
            target_format=target_clean,
            options=options_dict
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal conversion engine error: {e}")

    # Encode output filename for RFC 5987 compliance in Content-Disposition header
    encoded_filename = urllib.parse.quote(out_filename)

    return StreamingResponse(
        io.BytesIO(out_bytes),
        media_type=mime_type,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: Exception):
    """Custom 404 page for web requests and JSON error for API requests."""
    if request.url.path.startswith("/api/"):
        return JSONResponse(status_code=404, content={"error": "API route not found"})
    
    page_404 = os.path.join(STATIC_DIR, "404.html")
    if os.path.exists(page_404):
        return FileResponse(page_404, status_code=404)
    return HTMLResponse("<h1>404 - Page Not Found</h1>", status_code=404)


if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
