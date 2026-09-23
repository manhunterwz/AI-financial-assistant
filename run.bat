@echo off
echo ===================================================
echo     Starting AI Financial Assistant Services
echo ===================================================

if not exist .venv\Scripts\activate.bat (
    echo [ERROR] Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

echo Activating virtual environment...
call .venv\Scripts\activate

echo Starting FastAPI backend...
start cmd /k "title FastAPI Backend && call .venv\Scripts\activate && uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo Starting Streamlit frontend...
start cmd /k "title Streamlit Frontend && call .venv\Scripts\activate && streamlit run frontend\app.py --server.port 8501"

echo.
echo ===================================================
echo Services are running:
echo - FastAPI Backend: http://localhost:8000
echo - API Documentation: http://localhost:8000/docs
echo - Streamlit Frontend: http://localhost:8501
echo ===================================================
echo.
echo Keep these terminal windows open to run the services.
echo Close them to stop the services.
