# 파일 변경 감지 및 자동 커밋 스크립트 (PowerShell)
# 사용법: .\watch_and_commit.ps1

$repoPath = $PSScriptRoot
$lastCommit = Get-Date

Write-Host "파일 변경 감지 시작... (Ctrl+C로 종료)" -ForegroundColor Green
Write-Host "저장소 경로: $repoPath" -ForegroundColor Yellow

while ($true) {
    try {
        # Git 상태 확인
        Push-Location $repoPath
        $status = git status --porcelain
        
        if ($status) {
            $now = Get-Date
            $timeSinceLastCommit = ($now - $lastCommit).TotalSeconds
            
            # 마지막 커밋 후 5초 이상 지났을 때만 커밋 (너무 자주 커밋하는 것 방지)
            if ($timeSinceLastCommit -ge 5) {
                Write-Host "`n변경사항 감지됨: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Cyan
                
                # 변경된 파일 목록
                $changedFiles = ($status -split "`n" | Where-Object { $_ -match '\S' } | ForEach-Object { ($_ -split '\s+')[-1] })
                Write-Host "변경된 파일: $($changedFiles -join ', ')" -ForegroundColor Yellow
                
                # Git add
                git add .
                
                # 커밋 메시지 생성
                $fileList = $changedFiles -join ', '
                if ($fileList.Length -gt 50) {
                    $fileList = $fileList.Substring(0, 50) + "..."
                }
                $commitMsg = "auto: 파일 변경사항 자동 커밋 - $fileList"
                
                # 커밋
                git commit -m $commitMsg
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "커밋 완료: $commitMsg" -ForegroundColor Green
                    
                    # 푸시
                    git push origin main
                    
                    if ($LASTEXITCODE -eq 0) {
                        Write-Host "푸시 완료!" -ForegroundColor Green
                        $lastCommit = Get-Date
                    } else {
                        Write-Host "푸시 실패" -ForegroundColor Red
                    }
                } else {
                    Write-Host "커밋할 변경사항이 없거나 오류 발생" -ForegroundColor Yellow
                }
            }
        }
        
        Pop-Location
        Start-Sleep -Seconds 3  # 3초마다 확인
    }
    catch {
        Write-Host "오류 발생: $_" -ForegroundColor Red
        Start-Sleep -Seconds 5
    }
}

