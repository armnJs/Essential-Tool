# ⚡ OmniConvert - Universal Minimalist File Converter

[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)

OmniConvert is a universal, minimalist file format converter designed for high-speed file transformations across **Documents, Images, Data Formats, Audio, Archives, and Jupyter Notebooks**.

---

## 🚀 1-Click Quickstart (No Terminal Required!)

### 🪟 Windows Users:
1. Download or clone this repository.
2. Double-click **[`OmniConvert.exe`](OmniConvert.exe)** (or **[`OmniConvert.bat`](OmniConvert.bat)**) directly in the main folder.
3. The local server boots up automatically and launches your browser to **`http://127.0.0.1:8000`**!

### 🍏 macOS Users:
- Double-click **[`run_mac.command`](run_mac.command)** in the root folder.

### 🐧 Linux Users:
- Execute **[`./run_linux.sh`](run_linux.sh)** in terminal or double-click to launch.

---

## 🎯 How to Use (3 Simple Steps)

1. **Select or Drag File**: Drag any file into the dropzone or click **Browse Files**.
2. **Choose Target Format**: Click the format pill you want to convert your file to (e.g. `WEBP`, `PDF`, `DOCX`, `CSV`, `SQL`, `MP3`, `ZIP`).
3. **Click Convert**: Click **"Convert Now"** to download your output file instantly!

---

## 🛠️ Supported File Formats Matrix

| Category | Supported Formats |
| --- | --- |
| 📄 **Documents** | PDF, DOCX, TXT, MD, HTML, CSV, XLSX, Jupyter Notebook (`.ipynb`) |
| 🖼️ **Images** | PNG, JPG/JPEG, WEBP, GIF, SVG, BMP, ICO, TIFF |
| 📊 **Data & Code** | JSON, YAML, XML, CSV, TSV, SQL Queries, Base64, Python (`.py`) |
| 🎵 **Audio & Speech** | WAV, MP3, Synthetic Speech (Text-to-Speech) |
| 📦 **Archives** | ZIP, TAR, GZ |

---

## ☁️ Cloud Deployment (Render, Vercel, Docker, Railway)

OmniConvert comes with production deployment blueprints:
- **Render**: Connect repo to [Render.com](https://render.com) (uses `render.yaml` automatically).
- **Docker**: `docker build -t omniconvert .` ➔ `docker run -d -p 8000:8000 omniconvert`.
- **Vercel**: `vercel` (uses `vercel.json` and `api/index.py` with Mangum serverless adapter).

See [`docs/DEPLOYMENT_GUIDE.md`](docs/DEPLOYMENT_GUIDE.md) for full cloud hosting setup.

---

## 📄 License
Released under the open-source [MIT License](LICENSE).
