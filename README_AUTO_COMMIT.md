# 자동 커밋 및 푸시 설정 가이드

Cursor에서 작성한 내용이 자동으로 GitHub와 Streamlit에 반영되도록 설정하는 방법입니다.

## 방법 1: PowerShell 스크립트 사용 (권장)

### 사용 방법:
1. PowerShell을 관리자 권한으로 실행
2. 프로젝트 디렉토리로 이동:
   ```powershell
   cd "C:\Users\alice\OneDrive\바탕 화면\문법 교정 챗봇\streamlit-seoul2"
   ```
3. 스크립트 실행:
   ```powershell
   .\watch_and_commit.ps1
   ```

### 특징:
- 파일 변경을 3초마다 자동 감지
- 변경사항이 있으면 자동으로 커밋 및 푸시
- Ctrl+C로 중지 가능

## 방법 2: Python 스크립트 사용

### 사용 방법:
```bash
python auto_commit.py
```

또는 파일 저장 시 자동 실행하려면 Cursor의 설정에서 파일 저장 시 스크립트 실행을 설정할 수 있습니다.

## 방법 3: Git Hook 사용 (커밋 시 자동 푸시)

커밋할 때마다 자동으로 푸시되도록 설정:
```bash
# Windows에서는 Git Bash 사용
chmod +x .git/hooks/post-commit
```

## 주의사항

⚠️ **자동 커밋은 편리하지만 주의가 필요합니다:**
- 테스트하지 않은 코드가 자동으로 푸시될 수 있습니다
- 중요한 변경사항은 수동으로 커밋하는 것을 권장합니다
- 자동 커밋 메시지는 간단한 형식입니다

## 수동 커밋 (기본 방법)

자동 커밋을 사용하지 않으려면:
```bash
git add .
git commit -m "커밋 메시지"
git push origin main
```

