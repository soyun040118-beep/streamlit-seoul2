@echo off
REM 빠른 커밋 및 푸시 배치 파일
REM 파일을 저장한 후 이 파일을 더블클릭하면 자동으로 커밋 및 푸시됩니다

cd /d "%~dp0"
git add .
git commit -m "auto: 파일 변경사항 자동 커밋"
git push origin main

pause

