# 🚀 최종 배포 가이드

## 현재 상태
✅ Git 저장소 초기화 완료
✅ 모든 파일 커밋 완료 (2개 커밋)
✅ 배포 스크립트 준비 완료

## 빠른 배포 (3단계)

### 1단계: GitHub 저장소 생성
브라우저에서 https://github.com/new 열기
- 저장소 이름: `polymarket-dashboard` (또는 원하는 이름)
- Public 선택
- "Create repository" 클릭
- 생성된 저장소의 URL 복사 (예: `https://github.com/your-username/polymarket-dashboard.git`)

### 2단계: 코드 푸시
터미널에서 실행:

```bash
cd /Users/chasanghun/Desktop/Strategy
./push_and_deploy.sh
```

또는 수동으로:

```bash
git remote add origin https://github.com/YOUR_USERNAME/polymarket-dashboard.git
git push -u origin main
```

### 3단계: Vercel 배포
브라우저에서 https://vercel.com/new 열기
- "Import Git Repository" 클릭
- GitHub 저장소 선택
- "Deploy" 클릭
- 완료! 🎉

## 배포 후 확인
배포가 완료되면 Vercel이 제공하는 URL로 접속하여:
1. "데이터 새로고침" 버튼 클릭
2. 마켓 데이터가 표시되는지 확인

## 문제 해결

### GitHub 푸시 오류
- GitHub 인증 확인 필요
- Personal Access Token 사용:
  ```bash
  git remote set-url origin https://YOUR_TOKEN@github.com/USERNAME/REPO.git
  ```

### Vercel 배포 오류
- Node.js 버전 확인 (`node --version`)
- Vercel 로그에서 오류 확인
- `package.json` 파일 확인

## 완료!
배포가 완료되면 대시보드가 인터넷에서 접근 가능합니다! 🎊



