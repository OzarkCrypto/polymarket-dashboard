# 빠른 시작 가이드

## 🚀 GitHub + Vercel 배포 (자동화)

### 방법 1: 자동 스크립트 사용

1. **GitHub에서 저장소 생성**
   - https://github.com/new 접속
   - 저장소 이름 입력 (예: `polymarket-dashboard`)
   - "Create repository" 클릭

2. **배포 스크립트 실행**
   ```bash
   export GITHUB_REPO_URL=https://github.com/YOUR_USERNAME/polymarket-dashboard.git
   ./deploy.sh
   ```

### 방법 2: 수동 배포

#### GitHub에 푸시

```bash
# 1. GitHub에서 저장소 생성 후 URL 복사

# 2. 원격 저장소 추가
git remote add origin https://github.com/YOUR_USERNAME/polymarket-dashboard.git

# 3. 푸시
git push -u origin main
```

#### Vercel에 배포

**옵션 A: 웹사이트에서 배포 (추천)**
1. https://vercel.com/new 접속
2. GitHub 저장소 선택
3. "Deploy" 클릭
4. 완료! 🎉

**옵션 B: CLI로 배포**
```bash
# Vercel CLI 설치
npm install -g vercel

# 배포
vercel --prod
```

## 📋 체크리스트

- [ ] GitHub 저장소 생성
- [ ] 코드 푸시 완료
- [ ] Vercel 계정 생성/로그인
- [ ] Vercel에 프로젝트 연결
- [ ] 배포 완료 확인

## 🎯 배포 후 확인사항

1. 배포된 URL 접속
2. "데이터 새로고침" 버튼 클릭
3. 마켓 데이터가 정상적으로 표시되는지 확인

## ⚠️ 문제 해결

### GitHub 푸시 오류
- GitHub 인증 확인
- 저장소 URL이 올바른지 확인

### Vercel 배포 오류
- Node.js 설치 확인 (`node --version`)
- `package.json` 파일 확인
- Vercel 로그 확인

## 📞 도움이 필요하면

배포 중 문제가 발생하면:
1. 에러 메시지 확인
2. Vercel 로그 확인
3. GitHub Issues 확인

