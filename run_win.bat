@echo off
TITLE OmniConvert Universal Engine v2.0
CLS
ECHO ======================================================================
ECHO           🚀 Launching OmniConvert Engine v2.0 for Windows
ECHO           Created by Armaan (armnJs) • 100%% Local ^& Offline
ECHO ======================================================================
ECHO.

:: Change directory to script folder
cd /d "%~dp0"

:: Check for python installation
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO ❌ Error: Python is not installed or not in PATH.
    ECHO    Please install Python 3.9+ from python.org and check "Add Python to PATH".
    PAUSE
    EXIT /B 1
)

:: Run universal python launcher
python launch.py

PAUSE
