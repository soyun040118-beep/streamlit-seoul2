# 자동 커밋 및 푸시 백그라운드 실행 스크립트
# 이 스크립트를 실행하면 파일 변경을 감지하여 자동으로 커밋하고 푸시합니다.

$scriptPath = Join-Path $PSScriptRoot "watch_and_commit.ps1"

Write-Host "자동 커밋 스크립트를 시작합니다..." -ForegroundColor Green
Write-Host "종료하려면 작업 관리자에서 PowerShell 프로세스를 종료하세요." -ForegroundColor Yellow

# 백그라운드에서 실행
Start-Process powershell -ArgumentList "-NoExit", "-File", "`"$scriptPath`"" -WindowStyle Minimized

Write-Host "자동 커밋이 백그라운드에서 실행 중입니다." -ForegroundColor Green

