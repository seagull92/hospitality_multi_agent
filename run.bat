@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo   Hospitality Multi-Agent System Setup ^& Runner
echo ===================================================

:: 1. Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b
)

:: 2. Setup Virtual Environment
if not exist "venv\" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
)

:: 3. Activate and install dependencies
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Installing required packages...
pip install -r requirements.txt -q

:: 4. Check for API Key
set API_KEY_FILE=.env

if not exist "%API_KEY_FILE%" (
    copy .env.example %API_KEY_FILE% >nul
)

:: Read the first line to check if it's still the default
set /p API_KEY_LINE=<%API_KEY_FILE%
echo %API_KEY_LINE% | findstr /C:"your_google_api_key_here" >nul

if %errorlevel% == 0 (
    echo.
    echo ====================================================================
    echo IMPORTANT: You need a Google Gemini API Key to run this project.
    echo AI Agents cannot generate this for you due to Google's security.
    echo.
    echo Please go to: https://aistudio.google.com/app/apikey
    echo Sign in and click "Create API key".
    echo ====================================================================
    echo.
    set /p USER_API_KEY="Paste your API key here and press ENTER: "
    
    :: Save it to the .env file
    echo GOOGLE_API_KEY=!USER_API_KEY!> %API_KEY_FILE%
    echo [INFO] API Key saved to .env file.
)

:: 5. Run the project
echo.
echo [INFO] Starting the Multi-Agent System...
echo ===================================================
python main.py

echo.
pause
