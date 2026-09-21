# Implementation Plan - Format Expansion including iOS / Apple Native Formats

Expand **OmniConvert**'s conversion engine to support **iOS & Apple Native Formats** alongside **Video**, **Audio**, **Images**, **Data**, and **Documents**.

## User Review Required

> [!IMPORTANT]
> **iOS & Apple Native Formats to be Added**:
> 1. 🍎 **iOS / Apple Images & Icons**:
>    - `HEIC` / `HEIF` (iPhone camera photo format) $\rightarrow$ `JPG`, `PNG`, `WEBP`, `PDF`.
>    - `ICNS` (Apple App Icon format) $\rightarrow$ `PNG`, `ICO`, `JPG`.
> 2. 🎬 **iOS Video & Media**:
>    - `MOV` / `M4V` (Apple QuickTime & iTunes Video) $\rightarrow$ `MP4`, `WEBM`, `GIF`, `MP3` (audio extract).
> 3. 🎵 **iOS Audio**:
>    - `M4A` / `CAF` (Apple Core Audio Format) $\rightarrow$ `MP3`, `WAV`.
> 4. ⚙️ **iOS Data & Configuration**:
>    - `PLIST` (Apple Property List format - XML & Binary plist via `plistlib`) $\rightarrow$ `JSON`, `YAML`, `XML`, `CSV`.
>    - `VCF` (iOS vCard Contact cards) $\rightarrow$ `CSV`, `JSON`, `TXT`.
>    - `WEBLOC` (Apple Safari link shortcut) $\rightarrow$ `TXT`, `URL`, `HTML`.
> 5. 📑 **Apple iWork Bundle Formats**:
>    - `PAGES`, `NUMBERS`, `KEY` (Apple Pages, Numbers, Keynote document bundles) $\rightarrow$ `TXT`, `CSV`, `ZIP`, `HTML`.

---

## Proposed Changes

### 1. New Video & iOS Media Converter Engine

#### [NEW] [converters/video_converter.py](file:///d:/Armaan/Essential%20tool/converters/video_converter.py)
- Video frame decoding and format conversion for `MP4`, `MOV` (iOS QuickTime), `M4V`, `MKV`, `AVI`, `WEBM`, `GIF`, and `MP3`/`WAV` audio extraction.

---

### 2. Expanded Existing Converters with iOS Support

#### [MODIFY] [converters/image_converter.py](file:///d:/Armaan/Essential%20tool/converters/image_converter.py)
- Add `HEIC`/`HEIF` (via Pillow / fallback decoder), `ICNS` (Apple Icons), `PPM`, `PGM`, `PBM`, `TGA`, `EPS`, `DDS`.

#### [MODIFY] [converters/audio_converter.py](file:///d:/Armaan/Essential%20tool/converters/audio_converter.py)
- Add `M4A` (Apple Audio), `CAF` (Core Audio Format), `FLAC`, `AAC`, `OGG`, `AIFF`.

#### [MODIFY] [converters/data_converter.py](file:///d:/Armaan/Essential%20tool/converters/data_converter.py)
- Add `PLIST` (Apple Property List via Python standard `plistlib`), `VCF` (vCard contacts), `TOML`, `NDJSON`, `INI`, `PARQUET`.

#### [MODIFY] [converters/doc_converter.py](file:///d:/Armaan/Essential%20tool/converters/doc_converter.py)
- Add `PAGES`, `NUMBERS`, `KEY`, `WEBLOC`, `RTF`, `EPUB`.

#### [MODIFY] [converters/registry.py](file:///d:/Armaan/Essential%20tool/converters/registry.py)
- Register iOS & Media formats in `CONVERSION_TARGETS`.

---

### 3. Web UI & Test Suite Updates

#### [MODIFY] [static/index.html](file:///d:/Armaan/Essential%20tool/static/index.html) & [static/js/app.js](file:///d:/Armaan/Essential%20tool/static/js/app.js)
- Add iOS format badges, file limits, video options, and format pills.

#### [MODIFY] [tests/test_converters.py](file:///d:/Armaan/Essential%20tool/tests/test_converters.py)
- Add unit tests for `PLIST` (Apple Property List), `VCF`, `MOV`, `HEIC`, `M4A`, `TOML`, and `PARQUET`.

## Verification Plan

### Automated Tests
- Run `python -m unittest tests/test_converters.py` to verify 100% pass rate.
