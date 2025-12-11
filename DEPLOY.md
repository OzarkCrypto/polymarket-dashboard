# 배포 가이드

## GitHub에 올리기

1. **저장소 초기화**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Polymarket 기업 마켓 대시보드"
   ```

2. **GitHub에 저장소 생성**
   - GitHub에서 새 저장소 생성 (예: `polymarket-dashboard`)
   - 저장소 이름을 복사

3. **원격 저장소 연결 및 푸시**
   ```bash
   git remote add origin https://github.com/your-username/polymarket-dashboard.git
   git branch -M main
   git push -u origin main
   ```

## Vercel에 배포하기

### 방법 1: Vercel 웹사이트에서 배포

1. [Vercel](https://vercel.com)에 가입/로그인
2. "Add New Project" 클릭
3. GitHub 저장소 선택 (또는 Import Git Repository)
4. 프로젝트 설정:
   - **Framework Preset**: Next.js (자동 감지)
   - **Root Directory**: `./` (기본값)
   - **Build Command**: `npm run build` (자동 설정됨)
   - **Output Directory**: `.next` (자동 설정됨)
   - **Install Command**: `npm install` (자동 설정됨)
5. "Deploy" 클릭

### 방법 2: Vercel CLI로 배포

```bash
# Vercel CLI 설치
npm i -g vercel

# 배포
vercel

# 프로덕션 배포
vercel --prod
```

## 환경 변수 설정 (필요시)

Vercel 대시보드에서:
1. 프로젝트 선택
2. Settings → Environment Variables
3. 필요한 환경 변수 추가

## 배포 후 확인

배포가 완료되면 Vercel이 제공하는 URL로 접속하여 확인하세요.

예: `https://your-project-name.vercel.app`

## 문제 해결

### Python 런타임 오류

Vercel에서 Python을 사용하려면:
1. `vercel.json`에 Python 함수 설정 확인
2. `requirements-vercel.txt` 파일 확인
3. Vercel 로그에서 오류 확인

### 빌드 오류

1. 로컬에서 테스트:
   ```bash
   npm install
   npm run build
   ```

2. Vercel 로그 확인:
   - Vercel 대시보드 → 프로젝트 → Deployments → 로그 확인

### API 호출 오류

1. 브라우저 개발자 도구에서 네트워크 탭 확인
2. API 엔드포인트가 올바른지 확인 (`/api/scrape`)
3. CORS 오류가 있는지 확인

## 업데이트 배포

코드를 수정한 후:

```bash
git add .
git commit -m "Update: 설명"
git push
```

Vercel이 자동으로 새 배포를 시작합니다.

