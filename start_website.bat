@echo off
title Equiderma AI Clinical Advisor Launcher
cls
echo ============================================================
echo         EQUIDERMA AI CLINICAL ADVISOR LAUNCHER
echo ============================================================
echo.
echo [*] Checking Flask Backend (Port 9999)...
start "Equiderma AI - Flask Backend (Port 9999)" cmd /k "python run_backend.py"

echo [*] Waiting for Backend to initialize...
timeout /t 3 /nobreak >nul

echo [*] Launching Streamlit Clinical Website (Port 8501)...
start "Equiderma AI - Web Dashboard" cmd /k "python -m streamlit run \"text panel.py\""

echo [*] Opening your browser to http://localhost:8501 ...
timeout /t 2 /nobreak >nul
start http://localhost:8501

echo.
echo ============================================================
echo   Equiderma AI is running!
echo   Website URL:  http://localhost:8501
echo   Backend API:  http://localhost:9999
echo ============================================================
pause
