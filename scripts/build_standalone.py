#!/usr/bin/env python3
"""
OmniConvert PyInstaller Standalone Executable Builder
=====================================================
Compiles OmniConvert into a zero-dependency single-file standalone executable:
  - Windows: dist/OmniConvert.exe
  - macOS: dist/OmniConvert (or OmniConvert.app bundle)
  - Linux: dist/OmniConvert

Usage:
  python scripts/build_standalone.py
"""

import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.resolve()
STATIC_DIR = BASE_DIR / "static"
ICON_FILE = STATIC_DIR / "favicon.ico"

def check_pyinstaller():
    """Ensure pyinstaller is installed."""
    try:
        import PyInstaller
        print("✅ PyInstaller is installed.")
    except ImportError:
        print("📥 PyInstaller not found. Installing pyinstaller package...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_standalone():
    """Build PyInstaller single-file binary with data bundling."""
    check_pyinstaller()
    
    print("\n🔨 Building OmniConvert Standalone Executable...")
    print(f"   Target OS: {sys.platform}")
    print(f"   Source Root: {BASE_DIR}")
    
    # Path separator for --add-data (';' on Windows, ':' on macOS/Linux)
    sep = ";" if sys.platform == "win32" else ":"
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--name", "OmniConvert",
        f"--add-data={STATIC_DIR}{sep}static",
        f"--add-data={BASE_DIR / 'converters'}{sep}converters",
        f"--add-data={BASE_DIR / 'docs'}{sep}docs",
    ]
    
    if ICON_FILE.exists():
        cmd.append(f"--icon={ICON_FILE}")
        
    cmd.append(str(BASE_DIR / "launch.py"))
    
    print("\nExecuting PyInstaller command:")
    print(" ".join(cmd))
    
    subprocess.check_call(cmd, cwd=str(BASE_DIR))
    
    output_path = BASE_DIR / "dist"
    print("\n" + "=" * 60)
    print("🎉 BUILD SUCCESSFUL!")
    print(f"   Standalone Executable Location: {output_path}")
    if sys.platform == "win32":
        print(f"   Executable file: {output_path / 'OmniConvert.exe'}")
    else:
        print(f"   Executable binary: {output_path / 'OmniConvert'}")
    print("=" * 60)

if __name__ == "__main__":
    build_standalone()
