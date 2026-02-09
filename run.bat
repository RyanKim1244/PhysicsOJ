@echo off
chcp 65001 >nul
echo ========================================
echo   PhysicsOJ - Physics Online Judge
echo ========================================
echo.

echo [1/2] 패키지 설치 중...
pip install fastapi uvicorn sqlalchemy pydantic jinja2 python-multipart sympy numpy --quiet
if %errorlevel% neq 0 (
    echo 설치 실패. Python이 설치되어 있는지 확인하세요.
    pause
    exit /b 1
)

echo [2/2] 서버 시작 중...
echo.
echo  브라우저에서 접속하세요:  http://localhost:8000
echo  종료하려면 Ctrl+C
echo.
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
