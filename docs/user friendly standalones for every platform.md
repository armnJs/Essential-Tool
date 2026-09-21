# Implementation Plan - Cross-Platform Launchers & macOS / Standalone Support

Provide double-click one-shot launchers for **macOS** (`.command`), **Windows** (`.bat`), and **Linux** (`.sh`), plus a universal Python runner (`launch.py`) and PyInstaller compilation script (`scripts/build_standalone.py`) to build standalone executable binaries (`.exe` on Windows, `.app` / binary on macOS, standalone binary on Linux).

## User Review Required

> [!NOTE]
> macOS double-clickable launchers are `.command` files. When opened from macOS Finder, macOS automatically runs `.command` files in Terminal.
> On Windows, users can double-click `run_win.bat`. On Linux, users can run `run_linux.sh`.

## Proposed Changes

### Root Directory Launchers & Utility

#### [NEW] [launch.py](file:///d:/Armaan/Essential%20tool/launch.py)
- Cross-platform launcher script in Python.
- Automatically checks for `venv` or Python dependencies.
- Spawns default browser (`http://127.0.0.1:8000`) after local FastAPI server warms up.
- Manages graceful server shutdown when user presses Ctrl+C.

#### [NEW] [run_mac.command](file:///d:/Armaan/Essential%20tool/run_mac.command)
- Native macOS double-clickable launcher script.
- Navigates to app root directory via `cd "$(dirname "$0")"`.
- Checks for `python3`, auto-sets virtual environment if needed, runs `launch.py`, opens Safari/Chrome.

#### [NEW] [run_win.bat](file:///d:/Armaan/Essential%20tool/run_win.bat)
- Windows batch script for double-click launching.
- Runs `python launch.py` with automatic dependency setup.

#### [NEW] [run_linux.sh](file:///d:/Armaan/Essential%20tool/run_linux.sh)
- Linux shell launcher script with `chmod +x` support and desktop launcher compatibility.

---

### Standalone Executable Packaging

#### [NEW] [scripts/build_standalone.py](file:///d:/Armaan/Essential%20tool/scripts/build_standalone.py)
- Automated PyInstaller build script.
- Packages `server.py`, `converters/`, and `static/` files into a single standalone binary:
  - **Windows**: `dist/OmniConvert.exe`
  - **macOS**: `dist/OmniConvert` / `dist/OmniConvert.app`
  - **Linux**: `dist/OmniConvert`
- Includes custom icon support (`static/favicon.ico`).

---

### Documentation Updates

#### [MODIFY] [README.md](file:///d:/Armaan/Essential%20tool/README.md)
- Update platform instructions with section for Windows, macOS, Linux double-click launching and PyInstaller executable compilation.

---

## Verification Plan

### Automated Tests
- Run `python -m unittest tests/test_converters.py` to confirm no core regression.
- Test `launch.py` with `--check-only` or subprocess invocation.

### Manual Verification
- Test `launch.py` execution on current machine.
- Verify shell script permissions and formatting for macOS (`run_mac.command`) and Linux (`run_linux.sh`).
- Test `scripts/build_standalone.py` to verify PyInstaller build output structure.
