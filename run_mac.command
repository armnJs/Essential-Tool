#!/usr/bin/env bash
# ==============================================================================
# OmniConvert macOS Native Double-Click Launcher
# Double-click this file from macOS Finder to launch OmniConvert in Terminal.
# Author: Armaan (armnJs)
# ==============================================================================

# Change working directory to the directory containing this script
cd "$(dirname "$0")" || exit 1

clear
echo "======================================================================"
echo "          🚀 Launching OmniConvert Engine v2.0 for macOS"
echo "          Created by Armaan (armnJs) • 100% Local & Offline"
echo "======================================================================"
echo ""

# Ensure python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH."
    echo "   Please install Python 3 using Homebrew (brew install python3) or from python.org."
    read -n 1 -s -r -p "Press any key to exit..."
    exit 1
fi

# Run the universal python launcher
python3 launch.py
