# OmniConvert — Full Test Suite
**Target System:** OmniConvert (FastAPI + Vanilla JS file conversion app)
**Scope:** Functional, API, Security, Load/Performance, Edge Case, and UI testing
**Format:** Executable test cases for automated agent runs (e.g., Antigravity)

---

## 0. How to Execute This Suite

1. Start the server: `uvicorn server:app --reload` (or the app's documented entrypoint).
2. Confirm `GET /api/health` returns `200` with `{"status": "ok", ...}` before running anything else.
3. Run test blocks in order — **Section 1 → 2 → 3 → 4 → 5 → 6**. Security and load tests should be run against a **non-production / disposable** instance.
4. Each test case has: `ID`, `Precondition`, `Steps`, `Expected Result`, `Pass/Fail`, `Priority` (P0 = blocker, P1 = high, P2 = medium, P3 = low).
5. Log actual results and deviations in a results file alongside this suite; do not overwrite this file with results.
6. For any test that references a "malicious" or "adversarial" payload, generate the payload locally as part of the test step — do not fetch it from an external/untrusted URL.

---

## 1. API Contract Tests

| ID | Test Name | Steps | Expected Result | Priority |
|---|---|---|---|---|
| API-01 | Health check | `GET /api/health` | `200`, JSON body with `status: ok` and `app` field | P0 |
| API-02 | Formats — valid extension | `GET /api/formats?src=png` | `200`, JSON array of valid target formats (e.g. jpg, webp, pdf) | P0 |
| API-03 | Formats — unknown extension | `GET /api/formats?src=xyz123` | `200` with empty array, or `4xx` with clear error — not `500` | P1 |
| API-04 | Formats — missing `src` param | `GET /api/formats` (no query) | `4xx` with descriptive error, not `500` | P1 |
| API-05 | Formats — case sensitivity | `GET /api/formats?src=PNG` vs `?src=png` | Both return identical results (normalized) | P2 |
| API-06 | Formats — extension with leading dot | `GET /api/formats?src=.png` | Handled gracefully, same result as `png` | P2 |
| API-07 | Convert — happy path (image) | `POST /api/convert` with valid PNG, `target_format=jpg`, no options | `200`, `StreamingResponse`, correct `Content-Type: image/jpeg`, valid `Content-Disposition` filename | P0 |
| API-08 | Convert — missing `file` field | `POST /api/convert` with `target_format` only | `4xx` (422/400), no stack trace leaked | P0 |
| API-09 | Convert — missing `target_format` | `POST /api/convert` with `file` only | `4xx` with clear validation error | P0 |
| API-10 | Convert — invalid `target_format` for source type | Upload `.png`, `target_format=mp3` | `4xx` "unsupported conversion" — not `500` | P0 |
| API-11 | Convert — malformed `options` JSON | `options="{not valid json"` | `4xx` graceful error, or falls back to defaults (define expected behavior and assert it) | P1 |
| API-12 | Convert — options with unexpected keys | `options={"quality":85,"random_key":"x"}` | Extra keys ignored, conversion still succeeds | P2 |
| API-13 | Convert — response headers correctness | Inspect response for any successful conversion | `Content-Disposition: attachment; filename="..."` present and matches target extension; correct MIME type per format | P1 |
| API-14 | Convert — empty file upload (0 bytes) | Upload a 0-byte file with valid extension | `4xx` graceful "empty file" error, not `500`/crash | P1 |
| API-15 | 404 — API route not found | `GET /api/does-not-exist` | `404`, JSON `{"error": "API route not found"}` | P1 |
| API-16 | 404 — Web route not found | `GET /this-page-does-not-exist` | `404`, serves `static/404.html`, status code `404` | P1 |
| API-17 | CORS headers | Inspect `OPTIONS`/`GET` response headers from a cross-origin request | CORS policy is explicit and scoped (not wide-open `*` in production config) — flag if `*` combined with credentials | P1 |
| API-18 | Unsupported HTTP verb | `DELETE /api/convert`, `PUT /api/formats` | `405 Method Not Allowed`, not `500` | P2 |

---

## 2. Functional Conversion Tests (per module)

### 2.1 Image Converter (`image_converter.py`)
| ID | Test Name | Steps | Expected Result | Priority |
|---|---|---|---|---|
| IMG-01 | PNG → JPG | Convert sample PNG to JPG | Valid JPG output, visually correct, opens in image viewer | P0 |
| IMG-02 | JPG → PNG | Convert sample JPG to PNG | Valid PNG, alpha channel handled (opaque) | P0 |
| IMG-03 | PNG → WEBP | Convert with default options | Valid WEBP output | P1 |
| IMG-04 | PNG (transparent) → JPG | Use a PNG with alpha channel | JPG has transparent areas correctly flattened (white/defined background), no crash | P1 |
| IMG-05 | Any → GIF (single frame) | Convert static image to GIF | Valid single-frame GIF | P2 |
| IMG-06 | SVG → PNG | Convert vector SVG to raster PNG | Correct rasterization at reasonable default resolution | P1 |
| IMG-07 | BMP ↔ ICO ↔ TIFF ↔ AVIF | Round-trip each pair | All conversions succeed and are visually valid | P2 |
| IMG-08 | Quality option — JPG compression | `options={"quality": 10}` vs `{"quality": 100}` | Output file size differs proportionally; low-quality file is visibly smaller/more compressed | P2 |
| IMG-09 | Quality option — out-of-range | `options={"quality": 500}` and `{"quality": -5}` | Clamped to valid range or `4xx` — not a crash | P1 |
| IMG-10 | Resize option | `options={"width": 100, "height": 100}` | Output dimensions match request | P1 |
| IMG-11 | Resize — extreme dimensions | `options={"width": 100000, "height": 100000}` | Rejected with `4xx` (resource-limit guard) rather than attempting allocation | **P0 (security-adjacent)** |
| IMG-12 | Grayscale filter | `options={"grayscale": true}` | Output image has no color channels/saturation | P2 |
| IMG-13 | Corrupted image upload | Upload a `.png`-named file with random garbage bytes | `4xx` "invalid image data" — no server crash, no stack trace to client | P0 |
| IMG-14 | Animated GIF → static format | Convert multi-frame GIF to PNG | First frame extracted correctly, no crash on multi-frame source | P2 |

### 2.2 Document Converter (`doc_converter.py`)
| ID | Test Name | Steps | Expected Result | Priority |
|---|---|---|---|---|
| DOC-01 | TXT → PDF | Convert plain text file | Valid PDF, text content preserved, readable | P0 |
| DOC-02 | MD → HTML | Convert Markdown with headers, lists, links, code blocks | Correct HTML structure, no injected script from MD content | P0 |
| DOC-03 | MD → PDF | Convert Markdown to PDF | Formatting (bold, headers) rendered correctly | P1 |
| DOC-04 | DOCX → TXT | Extract plain text from Word doc | Text extracted, formatting stripped cleanly | P1 |
| DOC-05 | TXT → DOCX | Convert plain text to Word doc | Valid, openable .docx | P1 |
| DOC-06 | CSV → XLSX | Convert CSV with headers to Excel | Correct columns/rows, header row detected | P0 |
| DOC-07 | XLSX → CSV | Convert multi-sheet Excel (only first sheet expected) to CSV | Correct sheet exported, documented behavior for multi-sheet source | P1 |
| DOC-08 | Jupyter Notebook (.ipynb) → PY | Convert notebook with code + markdown cells | Code cells extracted in order; markdown cells commented or separated clearly | P1 |
| DOC-09 | Jupyter Notebook (.ipynb) → HTML | Convert notebook with outputs (text, image, error cells) | Rendered HTML preserves cell order and output types | P1 |
| DOC-10 | Jupyter Notebook (.ipynb) → PDF | Convert notebook with plots/images embedded | PDF renders without crashing on embedded base64 images | P2 |
| DOC-11 | HTML → MD | Convert HTML with nested tags, tables | Reasonable MD approximation, no crash on malformed HTML (missing closing tags) | P2 |
| DOC-12 | Empty/blank document | Convert a document with zero content | Graceful output (empty but valid target file) or clear `4xx` | P2 |
| DOC-13 | Very large text document (e.g. 50MB txt) | Convert to PDF/DOCX | Completes without timeout/OOM, or is rejected with a clear size-limit error | P1 |
| DOC-14 | Malformed DOCX upload | Rename a corrupted ZIP as `.docx` and upload | `4xx` graceful error via `python-docx` exception handling, no crash | P0 |
| DOC-15 | Malformed XLSX upload | Rename corrupted file as `.xlsx` | `4xx` graceful error via `openpyxl`, no crash | P0 |

### 2.3 Data Converter (`data_converter.py`)
| ID | Test Name | Steps | Expected Result | Priority |
|---|---|---|---|---|
| DATA-01 | JSON → YAML | Convert nested JSON object/array | Structurally equivalent YAML | P0 |
| DATA-02 | YAML → JSON | Convert YAML with anchors/aliases | Correct JSON, anchors resolved (or clear error if unsupported) | P1 |
| DATA-03 | JSON → XML | Convert JSON with nested arrays | Valid XML, arrays handled with repeated/indexed tags | P1 |
| DATA-04 | XML → JSON | Convert XML with attributes and nested elements | Attributes and text content both represented | P1 |
| DATA-05 | CSV → JSON | Convert CSV with headers | Array of objects keyed by header row | P0 |
| DATA-06 | JSON → CSV | Convert flat JSON array of objects | Correct CSV with header row from keys | P0 |
| DATA-07 | CSV → TSV | Convert comma-delimited to tab-delimited | Correct delimiter conversion, quoted fields with commas handled | P1 |
| DATA-08 | JSON → SQL (INSERT) | `options={"table_name": "users"}` | Valid `INSERT INTO users (...) VALUES (...)` statements, values properly escaped/parameterized in the generated SQL text | **P0 (security-adjacent — see SEC-06)** |
| DATA-09 | Any → Base64 / Base64 → Any | Round-trip a binary file through Base64 encode/decode | Byte-for-byte identical after round trip | P1 |
| DATA-10 | Malformed JSON upload | Upload JSON with trailing comma / unquoted keys | `4xx` graceful parse error, no crash | P0 |
| DATA-11 | Malformed YAML (tab indentation) | Upload YAML using tabs instead of spaces | `4xx` graceful parse error | P2 |
| DATA-12 | Deeply nested JSON | JSON nested 1000+ levels deep | Rejected gracefully or handled without stack overflow / crash | **P0 (security-adjacent — see SEC-05)** |
| DATA-13 | Unicode / emoji content | JSON/CSV containing emoji, RTL text, CJK characters | Preserved correctly through conversion, correct encoding declared in output | P1 |

### 2.4 Audio Converter (`audio_converter.py`)
| ID | Test Name | Steps | Expected Result | Priority |
|---|---|---|---|---|
| AUD-01 | Text → WAV (TTS) | `options={"text": "Hello world", "language": "en"}` | Valid playable WAV file generated | P0 |
| AUD-02 | Text → MP3 (TTS) | Same as above, `target_format=mp3` | Valid playable MP3 | P0 |
| AUD-03 | TTS — empty text | `options={"text": ""}` | `4xx` clear error, not a crash or empty/corrupt audio file | P1 |
| AUD-04 | TTS — very long text (10,000+ chars) | Large text block | Completes within a bounded time or rejected with size-limit error | P1 |
| AUD-05 | TTS — unsupported language code | `options={"language": "zz"}` | `4xx` graceful fallback/error, not crash | P2 |
| AUD-06 | WAV header/format correctness | Inspect generated WAV via `struct`/`wave` module reader | Correct RIFF header, sample rate, channel count as documented | P2 |
| AUD-07 | TTS — special characters/injection-looking text | `options={"text": "<script>alert(1)</script>"}` | Treated as literal text to synthesize, not executed/interpreted anywhere downstream | P1 |

### 2.5 Archive Converter (`archive_converter.py`)
| ID | Test Name | Steps | Expected Result | Priority |
|---|---|---|---|---|
| ARC-01 | Files → ZIP | Package multiple files into ZIP | Valid ZIP, all files present with correct content | P0 |
| ARC-02 | Files → TAR | Package multiple files into TAR | Valid TAR, all files present | P0 |
| ARC-03 | Single file → ZIP | Package one file | Valid ZIP with single entry | P1 |
| ARC-04 | Empty file set | Attempt archive creation with zero input files | `4xx` clear error, not a crash or empty corrupt archive | P1 |
| ARC-05 | Filenames with special characters | Archive files named with spaces, unicode, `#`, `&` | Names preserved correctly in archive entries | P2 |
| ARC-06 | Large number of files (e.g. 1000) | Archive many small files at once | Completes without timeout, or gracefully rejected with a documented limit | P2 |

---

## 3. Security Test Cases

> Run against an isolated/non-production instance. Do not run destructive payloads against shared infrastructure.

| ID | Test Name | Steps | Expected Result | Priority |
|---|---|---|---|---|
| SEC-01 | Path traversal via filename | Upload file with name `../../etc/passwd.png` or `..\\..\\windows\\system32\\config.png` | Filename is sanitized server-side; no file written/read outside intended temp/output directory | **P0** |
| SEC-02 | Content-Disposition header injection | Upload file with name containing `"; injected-header: value\r\nX-Injected: 1` or CR/LF chars | Filename sanitized before being placed into the `Content-Disposition` header; no header injection/response splitting | **P0** |
| SEC-03 | MIME type spoofing | Upload an executable/script (e.g. `.exe`, `.sh`, `.php`) renamed with an allowed extension (e.g. `.png`) | Server validates actual content/magic bytes, not just extension, before processing; rejects or safely fails on mismatch | **P0** |
| SEC-04 | Zip bomb upload | Craft a small ZIP that decompresses to gigabytes (e.g. nested/highly-compressible layers) and submit for archive conversion or extraction | Server enforces a decompression size/ratio limit; does not exhaust memory/disk | **P0** |
| SEC-05 | JSON/YAML billion-laughs / deep nesting | Submit YAML with alias-based exponential expansion, or JSON nested thousands of levels | Server has parser limits (depth/size) and rejects gracefully; no memory exhaustion or crash | **P0** |
| SEC-06 | SQL injection via `table_name` option | `options={"table_name": "users; DROP TABLE users;--"}` for JSON→SQL conversion | `table_name` is validated/whitelisted (alphanumeric+underscore only) or safely escaped as an identifier; malicious string does not produce executable multi-statement SQL in output without at least being clearly still just inert generated text (never executed server-side) | **P0** |
| SEC-07 | XXE (XML External Entity) injection | Submit XML→JSON conversion with a DOCTYPE defining an external entity pointing to a local file (`file:///etc/passwd`) or an internal network URL | `xml.etree.ElementTree` (or parser used) has external entity resolution disabled; no file disclosure, no SSRF | **P0** |
| SEC-08 | XML billion laughs (entity expansion DoS) | XML with nested internal entity definitions expanding exponentially | Parser rejects or limits expansion; no crash/hang | **P0** |
| SEC-09 | Decompression bomb via image (PIL "pixel bomb") | Upload a small image file with an enormous declared resolution (e.g. crafted PNG header claiming 50000x50000px) | `Pillow`'s `Image.MAX_IMAGE_PIXELS` guard is active (or equivalent); request rejected before attempting full decompression | **P0** |
| SEC-10 | Oversized file upload | Upload a file exceeding any documented/expected size limit (e.g. multi-GB) | Server enforces a max upload size (via FastAPI/Starlette config or reverse proxy) and rejects with `413`, not by hanging or crashing | **P0** |
| SEC-11 | Script injection in Markdown → HTML | Convert MD containing `<script>alert(1)</script>` and `<img src=x onerror=alert(1)>` embedded in raw HTML within the MD source | Output HTML either escapes/strips executable script content or is clearly documented as untrusted (should not be served as if safe to embed in a trusted context) | **P0** |
| SEC-12 | Formula injection in CSV/XLSX output | Convert JSON/data containing a cell value starting with `=`, `+`, `-`, `@` (e.g. `=cmd|'/c calc'!A1`) into CSV/XLSX | Output cell is sanitized/prefixed so spreadsheet software does not auto-execute a formula on open (CSV/Excel formula injection defense) | **P0** |
| SEC-13 | Symlink/junction entries inside uploaded archive | Upload a ZIP/TAR containing a symlink pointing outside the extraction directory, then request conversion involving extraction | Symlinks are stripped or resolution is confined to the extraction sandbox; no arbitrary file read/write outside temp dir | **P0** |
| SEC-14 | Null byte in filename | Upload file named `evil.php\x00.png` | Null byte stripped/rejected; cannot bypass extension validation | **P0** |
| SEC-15 | Double extension bypass | Upload `malicious.php.png` or `shell.png.exe` | Server validates true target based on content/allowed extension logic consistently, doesn't misroute processing | P1 |
| SEC-16 | Extension/target_format mismatch abuse | Upload a `.json` file but declare it as source `.png` in the form, request `target_format=jpg` | Server validates actual content type against the claimed extension before invoking the image pipeline; fails safely | **P0** |
| SEC-17 | Path traversal via `target_format` param | `target_format=../../etc/passwd` or `target_format=../../../tmp/evil` | Value is validated against an allowlist of known formats; rejected with `4xx` | **P0** |
| SEC-18 | Options JSON prototype pollution style keys | `options={"__proto__": {"polluted": true}}` (relevant if any part of the pipeline touches JS/Node tooling, or as a general malformed-input robustness check) | No unexpected object mutation/behavior change; input ignored or rejected | P2 |
| SEC-19 | Reflected/stored XSS via filename shown in UI | Upload file named `<img src=x onerror=alert(1)>.png`, observe how frontend renders the filename in status/result panels | Frontend escapes filename before DOM insertion (no `innerHTML` of raw filename); no script execution | **P0** |
| SEC-20 | CORS misconfiguration exploitation | From a malicious third-party origin, attempt authenticated/credentialed `fetch()` to `/api/convert` or `/api/formats` | CORS policy blocks disallowed origins; wildcard `*` is never combined with `Access-Control-Allow-Credentials: true` | **P0** |
| SEC-21 | Rate limiting / abuse resistance | Fire 100+ rapid sequential conversion requests from one client | Server either rate-limits, queues, or degrades gracefully — does not crash or become globally unresponsive for other users | P1 |
| SEC-22 | Temp file cleanup after conversion (and after failure) | Trigger several successful and several failed conversions; inspect server temp directory afterward | No orphaned temp files accumulate (checked both on success and on exception paths) — a leak here is a disk-exhaustion DoS vector over time | P1 |
| SEC-23 | Stack trace / internal path disclosure on error | Trigger a variety of conversion failures (corrupt file, bad options, unsupported combo) | API error responses never leak Python tracebacks, internal file paths, or library version info to the client | **P0** |
| SEC-24 | Content-Type sniffing on download | Inspect response headers on a converted-file download | `X-Content-Type-Options: nosniff` present, correct explicit `Content-Type` set (not left as `application/octet-stream` unnecessarily, and never allows a browser to render an uploaded/converted file as HTML) | P1 |
| SEC-25 | Multipart form field abuse — multiple `file` parts | Submit a multipart request with two different `file` fields | Server deterministically picks one and documents/handles it — not undefined/crashing behavior | P2 |
| SEC-26 | LocalStorage data exposure (frontend) | Inspect what the frontend persists to `localStorage` (theme, history, etc.) | No sensitive data (file contents, tokens) ever written to `localStorage` | P2 |
| SEC-27 | Static file directory traversal | `GET /static/../server.py` or URL-encoded equivalent `%2e%2e%2f` | Blocked by the static file handler; cannot read files outside `static/` | **P0** |
| SEC-28 | HTTP security headers audit | Inspect all response headers on `/`, `/api/*` | Presence of reasonable headers: `X-Frame-Options`/`frame-ancestors`, `X-Content-Type-Options`, a CSP if applicable | P2 |

---

## 4. Load & Performance Test Cases

| ID | Test Name | Steps | Expected Result | Priority |
|---|---|---|---|---|
| LOAD-01 | Concurrent conversions — moderate | Fire 20 concurrent `POST /api/convert` requests (mixed formats) via a load tool (e.g. `locust`, `k6`, `ab`) | All complete successfully; no request errors; response times stay within an acceptable bound (define SLA, e.g. <5s for small files) | P0 |
| LOAD-02 | Concurrent conversions — high | Ramp to 100–200 concurrent requests | Server degrades gracefully (queuing/slower responses) rather than crashing or returning 500s en masse | P1 |
| LOAD-03 | Sustained load (soak test) | Run moderate concurrent load continuously for 30+ minutes | No memory leak (monitor RSS over time), no growing temp-file count, no gradual response-time degradation | P1 |
| LOAD-04 | Large single-file conversion — image | Convert a very large (e.g. 4000x4000+, 20MB+) image | Completes within acceptable time, memory usage bounded, doesn't block other requests indefinitely (async/threaded properly) | P1 |
| LOAD-05 | Large single-file conversion — document | Convert a large multi-hundred-page equivalent text/doc file | Completes or fails gracefully with a size-limit message; no server hang | P1 |
| LOAD-06 | Large single-file conversion — data | Convert a large CSV/JSON (e.g. 500k+ rows) | Completes within bound or rejected with clear size-limit error; memory usage doesn't scale catastrophically | P1 |
| LOAD-07 | Streaming response behavior under load | Monitor whether `StreamingResponse` actually streams (doesn't buffer entire output in memory before sending) for a large output file | Memory footprint during response stays roughly constant relative to output size, not spiking to hold entire buffer needlessly (note: some buffering is expected if conversion is fully in-memory — flag if this becomes a scaling bottleneck) | P2 |
| LOAD-08 | `/api/formats` under load | Hammer `GET /api/formats?src=png` with high request rate (read-only, lightweight endpoint) | High throughput, low latency, no degradation of `/api/convert` availability | P2 |
| LOAD-09 | Mixed workload | Simulate realistic mixed traffic: 40% image, 30% document, 20% data, 10% audio conversions concurrently | System remains stable; per-category error rate stays near 0% | P1 |
| LOAD-10 | Recovery after overload | Push server past its breaking point (e.g. 500+ concurrent large-file requests), then stop | Server recovers to normal responsiveness afterward without requiring a manual restart | P2 |
| LOAD-11 | Worker/thread starvation check | Submit several long-running conversions (e.g. large TTS or large document renders) simultaneously | Short/simple conversion requests submitted in parallel are not starved indefinitely by long-running ones | P2 |

---

## 5. Edge Case Tests

| ID | Test Name | Steps | Expected Result | Priority |
|---|---|---|---|---|
| EDGE-01 | Convert to the same format as source | Upload `.png`, `target_format=png` | Handled gracefully — either a no-op copy or explicit rejection, but not a crash | P2 |
| EDGE-02 | File with no extension | Upload a file named `data` (no extension) | `4xx` clear "cannot determine source format" error | P1 |
| EDGE-03 | File with multiple dots in name | Upload `report.final.v2.docx` | Extension correctly parsed as `.docx`, not `.v2` | P2 |
| EDGE-04 | Uppercase extension | Upload `IMAGE.PNG`, request conversion | Handled case-insensitively, same as `.png` | P1 |
| EDGE-05 | Extremely long filename | Upload file with a 255+ character filename | Handled gracefully — truncated or rejected with clear error, no crash | P2 |
| EDGE-06 | Unicode filename | Upload file named `图片-café-🎉.png` | Filename preserved/sanitized correctly in the download `Content-Disposition`; no mojibake or crash | P1 |
| EDGE-07 | Options omitted entirely | `POST /api/convert` with no `options` field at all | Defaults applied correctly, conversion succeeds | P1 |
| EDGE-08 | Options as empty JSON object | `options={}` | Defaults applied, same as omitted | P2 |
| EDGE-09 | Concurrent identical requests | Submit the exact same conversion request twice at once (same file, same params) | Both succeed independently with correct isolated results (no shared-state cross-contamination between requests) | P1 |
| EDGE-10 | Network interruption mid-upload (frontend) | Start a large file upload, kill network mid-transfer | Frontend shows a clear error/retry state, doesn't hang indefinitely or show a false "success" | P2 |
| EDGE-11 | Browser back/forward during conversion | Trigger conversion, navigate away and back before it completes | No JS errors; in-flight request either completes cleanly in background or is safely abandoned | P3 |
| EDGE-12 | Drag-and-drop multiple files at once | Drag 2+ files into a single-file dropzone | Clear behavior defined: either rejects multi-file drop with a message, or documented multi-file handling — not silent failure | P2 |
| EDGE-13 | Drag-and-drop a folder | Drag an entire folder into the dropzone | Graceful rejection with a clear message, no crash | P3 |
| EDGE-14 | Theme toggle persistence | Toggle dark/light mode, reload page | Theme persists via `localStorage` correctly on reload | P3 |
| EDGE-15 | Options panel — switching target format mid-selection | Select target format A (options render), switch to target format B before converting | Options panel updates to format-B-relevant fields; stale format-A options are not silently sent | P2 |
| EDGE-16 | Repeated conversion of the same uploaded file | Upload once, convert to format A, then (without re-uploading) convert same file to format B | Both conversions use the correct original source file, no state bleed from the first conversion's output | P1 |
| EDGE-17 | Convert immediately after page load with no file selected | Click "Convert Now" with no file in the dropzone | Frontend blocks the action locally with a clear message; does not send an empty/invalid request to the API | P1 |
| EDGE-18 | Slow client connection simulation | Throttle network to 3G-equivalent speed, perform a conversion | UI shows appropriate loading/progress state throughout, times out gracefully if it exceeds a reasonable bound | P2 |
| EDGE-19 | JS disabled | Load the app with JavaScript disabled | Reasonable fallback message shown (app is inherently JS-dependent — verify it fails cleanly, not blank/broken) | P3 |
| EDGE-20 | 404 page particle simulation performance | Load `/404`, interact with canvas particle physics (click reset repeatedly) | No memory leak or frame-rate collapse from repeated interaction | P3 |

---

## 6. UI / Frontend Functional Tests

| ID | Test Name | Steps | Expected Result | Priority |
|---|---|---|---|---|
| UI-01 | Dropzone click-to-browse | Click dropzone (not drag) | Native file picker opens | P1 |
| UI-02 | Dropzone visual feedback on drag-over | Drag a file over the dropzone without dropping | Dropzone shows active/hover visual state | P2 |
| UI-03 | Format pills render correctly | Select a source file, observe target format selector | Pills match the `/api/formats` response for that source extension | P0 |
| UI-04 | Conversion progress indicator | Start a conversion | Clear in-progress state is shown until completion or failure | P1 |
| UI-05 | Download trigger after conversion | Complete a conversion | Blob download triggers automatically or via a clearly visible button; correct output filename | P0 |
| UI-06 | Error state display | Force a conversion failure (e.g. invalid combo) | User-facing error message is clear and non-technical (no raw stack trace shown in UI) | P0 |
| UI-07 | Responsive layout | Resize viewport to mobile width | Layout adapts without breaking (dropzone, pills, buttons remain usable) | P2 |
| UI-08 | Dark/light mode visual correctness | Toggle theme | All UI elements (including glassmorphic panels) render correctly in both modes, no unreadable low-contrast text | P2 |

---

## Appendix A — Suggested Test Data Set

- `sample.png` (small, valid, with alpha channel)
- `sample_large.png` (large resolution, for resize/limit tests)
- `corrupt.png` (valid extension, garbage bytes)
- `sample.docx`, `corrupt.docx`
- `sample.xlsx`, `corrupt.xlsx`
- `sample.csv` (with quoted fields, commas-in-values, unicode)
- `sample.json` (nested), `deeply_nested.json` (crafted for SEC-05/DATA-12)
- `sample.yaml`, `billion_laughs.yaml` (crafted for SEC-05)
- `sample.xml`, `xxe_payload.xml` (crafted for SEC-07), `entity_bomb.xml` (crafted for SEC-08)
- `sample.ipynb` (with code, markdown, and image-output cells)
- `zip_bomb.zip` (crafted for SEC-04)
- `symlink_traversal.zip` (crafted for SEC-13)
- `formula_injection.json` (`=cmd|'/c calc'!A1` style values, for SEC-12)
- `traversal_filename.png` (named `../../etc/passwd.png`, for SEC-01)
- `xss_filename.png` (named `<img src=x onerror=alert(1)>.png`, for SEC-19)

## Appendix B — Priority Legend

- **P0** — Must pass before any release; blocker if failing (includes all critical security items).
- **P1** — High priority; should pass before release, may ship with a tracked known issue if unavoidable.
- **P2** — Medium priority; polish/robustness, track for next iteration if failing.
- **P3** — Low priority; nice-to-have, cosmetic or rare-path coverage.
