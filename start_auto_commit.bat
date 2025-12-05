@echo off
REM 자동 커밋 및 푸시 배치 파일
REM 실행 정책 문제 없이 실행 가능

cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "watch_and_commit.ps1"

