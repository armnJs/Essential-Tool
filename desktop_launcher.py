"""
OmniConvert Standalone Desktop Launcher
Starts local FastAPI server on 127.0.0.1:8000 and automatically opens the browser.
"""

import os
import sys
import time
import webbrowser
import threading
from pathlib import Path
import uvicorn

# Add root directory to sys.path
root_dir = str(Path(__file__).resolve().parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from server import app


def open_browser():
    """Wait for server to boot then open default web browser."""
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:8000")


def main():
    print("==================================================")
    print("  OmniConvert Universal File Converter Launcher  ")
    print("==================================================")
    print("[*] Starting local server at http://127.0.0.1:8000...")

    # Start browser in background thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Start uvicorn server
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")


if __name__ == "__main__":
    main()
