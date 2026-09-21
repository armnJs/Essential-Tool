#!/usr/bin/env bash
# ==============================================================================
# OmniConvert Linux Native Launcher
# Run this script from terminal or double-click in GUI desktop environments.
# Author: Armaan (armnJs)
# ==============================================================================

cd "$(dirname "$0")" || exit 1

clear
echo "======================================================================"
echo "          🚀 Launching OmniConvert Engine v2.0 for Linux"
echo "          Created by Armaan (armnJs) • 100% Local & Offline"
echo "======================================================================"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "   Please install python3 and python3-venv using your system package manager."
    echo "   (e.g., sudo apt install python3 python3-venv)"
    read -n 1 -s -r -p "Press any key to exit..."
    exit 1
fi

python3 launch.py
