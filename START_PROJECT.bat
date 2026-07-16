@echo off
echo ========================================
echo    Enterprise RAG - Starting Up
echo ========================================

echo [1/2] Activating virtual environment...
call venv\Scripts\activate.bat 2>nul
if errorlevel 1 (
    echo Virtual env not found, trying .venv...
    call .venv\Scripts\activate.bat 2>nul
)

echo [2/2] Starting FastAPI backend (port 8000)...
start cmd /k "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo ========================================
echo  Backend:  http://localhost:8000
echo  API Docs: http://localhost:8000/docs
echo  Frontend: Open app/frontend/index.html
echo ========================================
pause
