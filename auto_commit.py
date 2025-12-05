"""
자동 커밋 및 푸시 스크립트
파일 변경을 감지하여 자동으로 커밋하고 푸시합니다.
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """명령어를 실행하고 결과를 반환합니다."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def auto_commit_and_push():
    """변경사항을 자동으로 커밋하고 푸시합니다."""
    # 현재 스크립트의 디렉토리
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Git 상태 확인
    success, stdout, stderr = run_command("git status --porcelain")
    if not success:
        print(f"Git 상태 확인 실패: {stderr}")
        return False
    
    # 변경사항이 없으면 종료
    if not stdout.strip():
        print("변경사항이 없습니다.")
        return True
    
    # 변경된 파일 목록 확인
    changed_files = [line.split()[-1] for line in stdout.strip().split('\n') if line]
    print(f"변경된 파일: {', '.join(changed_files)}")
    
    # 모든 변경사항 추가
    success, stdout, stderr = run_command("git add .")
    if not success:
        print(f"Git add 실패: {stderr}")
        return False
    
    # 커밋 메시지 생성
    commit_message = f"auto: 파일 변경사항 자동 커밋 - {', '.join(changed_files[:3])}"
    if len(changed_files) > 3:
        commit_message += f" 외 {len(changed_files) - 3}개 파일"
    
    # 커밋
    success, stdout, stderr = run_command(f'git commit -m "{commit_message}"')
    if not success:
        if "nothing to commit" in stderr.lower():
            print("커밋할 변경사항이 없습니다.")
            return True
        print(f"Git commit 실패: {stderr}")
        return False
    
    print(f"커밋 완료: {commit_message}")
    
    # 푸시
    success, stdout, stderr = run_command("git push origin main")
    if not success:
        print(f"Git push 실패: {stderr}")
        return False
    
    print("푸시 완료!")
    return True

if __name__ == "__main__":
    auto_commit_and_push()

