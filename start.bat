@echo off
echo Starting Q-SYS Reflect API Explorer...
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo.
    echo Please download and install Python from:
    echo https://www.python.org/downloads/
    echo.
    echo During install, make sure to tick "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

:: Change to the folder where this bat file is located
cd /d "%~dp0"

:: Open browser after 2 seconds
start "" timeout /t 2 /nobreak >nul & start "" "http://localhost:8080/index.html"

:: Start the proxy server
echo Proxy server running at http://localhost:8080
echo Browser will open automatically...
echo Press Ctrl+C to stop.
echo.
python server.py

pause
