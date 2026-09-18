# Implementation Plan - OmniConvert (Universal Minimalist File Converter)

Build a full-featured, free, minimalist universal file converter web application ("OmniConvert") supporting comprehensive file format conversions (Documents, Images, Audio, Data, Code, Archives) with a client-side + Python backend processing engine, sleek minimalist aesthetic, and custom 404 error page.

## User Review Required

> [!IMPORTANT]
> **Key Architecture Decision**:
> 1. **Dual Engine Converter System**: The app will utilize a Python backend (FastAPI + Pillow, PyPDF, python-docx, reportlab, pandas, markdown, pydub, jszip-compat) paired with browser client-side JS converters for instant performance.
> 2. **Supported Formats**:
>    - **Documents**: PDF, DOCX, TXT, MD, HTML, CSV, XLSX, EPUB, RTF, JSON, XML
>    - **Images**: PNG, JPG/JPEG, WEBP, GIF, SVG, BMP, TIFF, ICO, AVIF
>    - **Audio/Media**: WAV, MP3, OGG, Audio Extraction, TTS (Text-to-Speech)
>    - **Data & Code**: JSON, XML, YAML, CSV, TSV, HTML, Markdown, Base64, SQL, Python dict
>    - **Archives**: ZIP, TAR, GZ, 7Z
> 3. **Custom 404 Page**: Interactive minimalist canvas page with file particle animations, search reset, and smooth route handling.

## Open Questions

> [!NOTE]
> No blocking open questions. We will proceed with setting up FastAPI + lightweight Python libraries + vanilla modern frontend so no heavy external command dependencies (like full binary installs of FFmpeg or Pandoc) are strictly required to start converting!

## Proposed Changes

### Backend Components

#### [NEW] [server.py](file:///d:/Armaan/Essential%20tool/server.py)
- FastAPI web server exposing `/api/convert`, `/api/formats`, `/api/preview`, `/api/health`.
- Converter manager engine registering handlers for Document, Image, Audio, Data, Code, and Archive transformations.
- Static file serving for UI and custom 404 route handling.

#### [NEW] [converters/](file:///d:/Armaan/Essential%20tool/converters/)
- `image_converter.py`: Handling PNG, JPG, WEBP, GIF, SVG, BMP, ICO, TIFF, AVIF cross-conversions, resizing, quality, compression.
- `doc_converter.py`: Handling PDF to images, images to PDF, TXT/MD/HTML to PDF/DOCX, CSV/XLSX/JSON/XML data sheet conversions.
- `data_converter.py`: Formatter & transformer for JSON, YAML, XML, CSV, TSV, Markdown, Base64, SQL, EPUB/TXT.
- `audio_converter.py`: Native Python audio waveform encoder (WAV, MP3 stream generation, synthetic TTS generation).
- `archive_converter.py`: Multi-file ZIP/TAR archive pack and unpack logic.

#### [NEW] [requirements.txt](file:///d:/Armaan/Essential%20tool/requirements.txt)
- Python packages: `fastapi`, `uvicorn`, `python-multipart`, `Pillow`, `pypdf`, `python-docx`, `reportlab`, `pandas`, `openpyxl`, `markdown`, `pyyaml`, `beautifulsoup4`.

---

### Frontend Components

#### [NEW] [static/index.html](file:///d:/Armaan/Essential%20tool/static/index.html)
- Main application shell featuring minimalist hero header, drag-and-drop dropzone, smart format selector with category filter pills, options panel (quality, page ranges, formatting), conversion progress bar, output preview, batch conversion list, and dark/light minimalist theme switcher.

#### [NEW] [static/css/style.css](file:///d:/Armaan/Essential%20tool/static/css/style.css)
- Custom design system with modern typography (Inter / Outfit), glassmorphic card elements, subtle gradient borders, dark mode default, micro-interactions, responsive grid layout.

#### [NEW] [static/js/app.js](file:///d:/Armaan/Essential%20tool/static/js/app.js)
- Core client logic: drag-and-drop handling, MIME/extension detection, format pairing engine, client-side preview rendering, async batch upload to API, download manager, and localStorage history.

#### [NEW] [static/404.html](file:///d:/Armaan/Essential%20tool/static/404.html)
- Custom minimalist 404 page with canvas particle gravity simulation (floating lost file fragments), sleek error typography, and immediate navigation back to file converter.

## Verification Plan

### Automated Tests
- Server API test script (`test_converters.py`) verifying file conversion matrix across Document, Image, Data, and Archive formats.
- Route test for `GET /404` and fallback 404 handler.

### Manual Verification
- Start FastAPI dev server (`python server.py` / `uvicorn`).
- Perform file drag-and-drop conversions (e.g. PNG -> WEBP, PDF -> Images, JSON -> CSV/YAML, TXT -> PDF, Files -> ZIP).
- Test custom 404 page by accessing non-existent URL routes.
