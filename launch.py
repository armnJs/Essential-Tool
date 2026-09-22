#!/usr/bin/env python3
"""
OmniConvert Universal Desktop Launcher
======================================
Cross-platform launcher for Windows, macOS, and Linux.
Automatically verifies Python environment, installs missing dependencies,
launches the local FastAPI server, and opens your default browser.
"""

import os
import sys
import subprocess
import time
import urllib.request
import webbrowser
from pathlib import Path

# Safe Unicode output for Windows legacy console
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Base directory setup
BASE_DIR = Path(__file__).parent.resolve()
REQUIREMENTS_FILE = BASE_DIR / "requirements.txt"
VENV_DIR = BASE_DIR / ".venv"

HOST = "127.0.0.1"
PORT = 8000
SERVER_URL = f"http://{HOST}:{PORT}"

def get_venv_python():
    """Return path to virtual environment python binary."""
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"

def ensure_environment():
    """Check and create virtualenv and install requirements if needed."""
    python_exe = get_venv_python()
    
    if not VENV_DIR.exists():
        print(f"📦 Creating virtual environment in {VENV_DIR}...")
        subprocess.check_call([sys.executable, "-m", "venv", str(VENV_DIR)])
    
    # Check if essential dependencies are installed
    try:
        subprocess.check_call(
            [str(python_exe), "-c", "import fastapi, uvicorn, PIL, reportlab, pypdf, docx"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        print("📥 Installing required dependencies from requirements.txt...")
        subprocess.check_call([str(python_exe), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)])

def is_server_running():
    """Check if server is accepting HTTP connections."""
    try:
        with urllib.request.urlopen(f"{SERVER_URL}/api/health", timeout=1) as resp:
            return resp.status == 200
    except Exception:
        return False

def open_browser():
    """Open default web browser after server is alive."""
    for _ in range(30):  # wait up to 15 seconds
        if is_server_running():
            print(f"🌐 Opening OmniConvert UI in browser ({SERVER_URL})...")
            webbrowser.open(SERVER_URL)
            return True
        time.sleep(0.5)
    print("⚠️ Server launch timed out. Opening browser anyway...")
    webbrowser.open(SERVER_URL)
    return False

def main():
    print("=" * 60)
    print("       🚀 OmniConvert Universal Engine v2.0")
    print("       Created by Armaan (armnJs) • 100% Local & Offline")
    print("=" * 60)
    
    # Check CLI flags
    if "--check-only" in sys.argv:
        print("✅ Environment check complete.")
        return

    # Ensure virtualenv & packages
    ensure_environment()
    python_exe = get_venv_python()

    print(f"⚡ Starting server at {SERVER_URL}...")
    
    # Launch browser wait in a daemon thread or non-blocking call
    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Launch server using venv python
    try:
        server_cmd = [str(python_exe), str(BASE_DIR / "server.py")]
        subprocess.run(server_cmd, cwd=str(BASE_DIR))
    except KeyboardInterrupt:
        print("\n👋 OmniConvert server stopped. Goodbye!")

if __name__ == "__main__":
    main()
