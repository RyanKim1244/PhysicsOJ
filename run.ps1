Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PhysicsOJ - Physics Online Judge" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/2] 패키지 설치 중..." -ForegroundColor Yellow
pip install fastapi uvicorn sqlalchemy pydantic jinja2 python-multipart sympy numpy --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "설치 실패. Python이 설치되어 있는지 확인하세요." -ForegroundColor Red
    Read-Host "엔터를 누르세요"
    exit 1
}

Write-Host "[2/2] 서버 시작 중..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  브라우저에서 접속하세요:  http://localhost:8000" -ForegroundColor Green
Write-Host "  종료하려면 Ctrl+C" -ForegroundColor Gray
Write-Host ""
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
