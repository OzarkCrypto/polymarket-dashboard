# Polymarket 기업 마켓 대시보드

Polymarket에서 기업 관련 마켓을 필터링하여 내부 정보 우위가 있을 수 있는 마켓을 찾는 웹 대시보드입니다.

## 🚀 배포 방법

### Vercel에 배포하기

1. **GitHub에 저장소 생성**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/polymarket-dashboard.git
   git push -u origin main
   ```

2. **Vercel에 연결**
   - [Vercel](https://vercel.com)에 가입/로그인
   - "New Project" 클릭
   - GitHub 저장소 선택
   - 프레임워크: Next.js 자동 감지
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Deploy 클릭

3. **환경 변수 설정 (필요시)**
   - Vercel 대시보드에서 프로젝트 설정 → Environment Variables

### 로컬 개발

```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 브라우저에서 http://localhost:3000 열기
```

## 📁 프로젝트 구조

```
.
├── app/                    # Next.js App Router
│   ├── page.tsx           # 메인 페이지
│   ├── layout.tsx         # 레이아웃
│   └── globals.css        # 전역 스타일
├── api/                   # API Routes
│   └── scrape/
│       └── index.py       # Vercel Serverless Function
├── polymarket_scraper.py  # Python 스크래퍼 모듈
├── package.json           # Node.js 의존성
├── requirements.txt      # Python 의존성
├── vercel.json           # Vercel 설정
└── README.md             # 이 파일
```

## 🛠️ 기술 스택

- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Backend**: Vercel Serverless Functions (Python)
- **Charts**: Recharts
- **Icons**: Lucide React

## ✨ 기능

- 🔍 **기업 관련 마켓 필터링**: 주요 기업(OpenAI, Google, Apple 등)과 관련된 마켓만 표시
- 🎯 **정보 우위 마켓 식별**: 제품 출시일, 발표일 등 내부 정보를 가진 사람이 우위를 가질 수 있는 마켓 강조
- 📊 **시각화**: 기업별 마켓 분포 차트 및 정보 우위 분포 파이 차트
- 🔄 **실시간 데이터 수집**: Polymarket에서 최신 마켓 데이터 수집

## 📝 사용 방법

1. 대시보드 접속
2. "데이터 새로고침" 버튼 클릭하여 최신 마켓 데이터 수집
3. 필터를 사용하여:
   - 내부 정보 우위 가능성이 있는 마켓만 보기
   - 특정 기업 관련 마켓만 보기
4. 마켓 카드를 클릭하여 Polymarket에서 자세히 확인

## ⚠️ 주의사항

**법적 고지**: 내부자 정보를 이용한 거래는 법적 문제를 일으킬 수 있습니다. 이 도구는 정보 수집 목적으로만 사용하시기 바랍니다.

## 🔧 문제 해결

### 데이터를 가져오지 못하는 경우

- Polymarket 사이트가 정상 작동하는지 확인
- 네트워크 연결 확인
- 몇 분 후 다시 시도 (Rate limiting 가능성)

### Vercel 배포 오류

- Python 런타임이 제대로 설정되었는지 확인
- `vercel.json` 파일이 올바른지 확인
- Vercel 로그에서 오류 메시지 확인

## 📄 라이선스

이 프로젝트는 개인 사용 목적으로 제공됩니다.

