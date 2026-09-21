# Implementation Plan - Fresh Clean Rebuild of OmniConvert

Rebuild **OmniConvert** completely from scratch based on the documentation blueprint in `docs/` using 100% fresh, clean, modern code (no legacy code reuse).

## User Review Required

> [!IMPORTANT]
> **Fresh Clean Codebase Guarantee**:
> 1. All existing code in `server.py`, `converters/`, and `static/` will be replaced with brand new, highly optimized, production-grade clean code written from scratch.
> 2. Zero legacy bloat, zero watermarks, zero floating window overlays, zero complex multi-spec build scripts.
> 3. Clean decoupled structure:
>    - **FastAPI Server** (`server.py`)
>    - **Converter Handlers** (`converters/image_converter.py`, `doc_converter.py`, `data_converter.py`, `audio_converter.py`, `archive_converter.py`, `registry.py`)
>    - **Minimalist SPA Frontend** (`static/index.html`, `static/css/style.css`, `static/js/app.js`, `static/404.html`)

## Proposed Changes

### Backend Core Engine

#### [NEW] [server.py](file:///d:/Armaan/Essential%20tool/server.py)
- Fresh FastAPI server exposing `/api/health`, `/api/formats`, `/api/convert`.
- Static asset serving (`/static`) and clean 404 route handling (`/404`).

#### [NEW] [converters/registry.py](file:///d:/Armaan/Essential%20tool/converters/registry.py)
- Clean format catalog and target matrix dispatcher.

#### [NEW] [converters/image_converter.py](file:///d:/Armaan/Essential%20tool/converters/image_converter.py)
- High-speed Pillow-based raster image converter (PNG, JPG, WEBP, GIF, BMP, ICO, TIFF) with quality compression, resize, and grayscale controls.

#### [NEW] [converters/doc_converter.py](file:///d:/Armaan/Essential%20tool/converters/doc_converter.py)
- Document processing engine for PDF generation (ReportLab), Word DOCX (`python-docx`), TXT, Markdown, HTML, CSV/XLSX (`pandas`), and Jupyter Notebook (`.ipynb`).

#### [NEW] [converters/data_converter.py](file:///d:/Armaan/Essential%20tool/converters/data_converter.py)
- Data transformation engine for JSON, YAML, XML, CSV, TSV, Base64, and SQL `INSERT` generation.

#### [NEW] [converters/audio_converter.py](file:///d:/Armaan/Essential%20tool/converters/audio_converter.py)
- Audio generator handling WAV/MP3 streams and synthetic speech (TTS) generation.

#### [NEW] [converters/archive_converter.py](file:///d:/Armaan/Essential%20tool/converters/archive_converter.py)
- Compressed archive pack/unpack engine for ZIP and TAR formats.

---

### Frontend SPA Layer

#### [NEW] [static/index.html](file:///d:/Armaan/Essential%20tool/static/index.html)
- Clean single-page application layout: modern header, category tabs, file drag-and-drop dropzone with native file explorer `<label>`, dynamic target format pills, options card, conversion progress bar, and instant download card.

#### [NEW] [static/css/style.css](file:///d:/Armaan/Essential%20tool/static/css/style.css)
- Premium dark/light theme design system using CSS custom properties, Google Fonts (Outfit & Inter), glassmorphism cards, smooth animations, and responsive layout.

#### [NEW] [static/js/app.js](file:///d:/Armaan/Essential%20tool/static/js/app.js)
- Modular ES6 JavaScript controller: file selection, format lookup, dynamic options rendering, multipart upload handling, progress updates, and blob download management.

#### [NEW] [static/404.html](file:///d:/Armaan/Essential%20tool/static/404.html)
- Interactive HTML5 canvas error page with floating particle physics and quick navigation reset.

---

### Tests & Configuration

#### [NEW] [test_converters.py](file:///d:/Armaan/Essential%20tool/test_converters.py)
- Clean unit test script verifying PNG->JPG, JSON->CSV/SQL, TXT->PDF, File->ZIP, and Notebook->PDF/DOCX conversions.

#### [NEW] [requirements.txt](file:///d:/Armaan/Essential%20tool/requirements.txt)
- Essential dependencies: `fastapi`, `uvicorn`, `python-multipart`, `Pillow`, `pypdf`, `python-docx`, `reportlab`, `pandas`, `openpyxl`, `markdown`, `pyyaml`, `beautifulsoup4`.

## Verification Plan

### Automated Tests
- Run `python test_converters.py` to verify 100% clean passes across all converter engines.

### Manual Verification
- Launch `python server.py`.
- Access `http://127.0.0.1:8000` in browser.
- Perform drag-and-drop conversions for Image, Document, Data, Audio, and Archive files.
- Verify download links and test invalid route `/invalid-page` for custom 404 page rendering.
