# Polymarket Tech 마켓 & 홀더 대시보드 배포 가이드

## 기능

- 💻 Tech 카테고리의 액티브 마켓만 표시
- 👥 각 마켓의 Yes/No 탑10 홀더 정보 표시
- 📊 실시간 데이터 업데이트
- 🔄 마켓 클릭 시 홀더 정보 자동 로드

## 로컬 개발

### 1. 의존성 설치

```bash
npm install
```

### 2. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 `http://localhost:3000` 접속

## Vercel 배포

### 1. Vercel CLI 설치 (선택사항)

```bash
npm i -g vercel
```

### 2. Vercel에 배포

```bash
vercel
```

또는 GitHub에 푸시 후 Vercel 대시보드에서 연결

### 3. 환경 변수 설정

Vercel 대시보드에서 환경 변수 설정은 필요 없습니다. (모든 API는 공개 API 사용)

## API 엔드포인트

### `/api/tech-markets`
Tech 카테고리의 액티브 마켓 목록을 가져옵니다.

**응답 예시:**
```json
{
  "success": true,
  "count": 10,
  "markets": [
    {
      "id": "market-id",
      "conditionId": "condition-id",
      "question": "Will OpenAI release GPT-5 in 2024?",
      "description": "...",
      "slug": "will-openai-release-gpt-5",
      "outcomes": ["Yes", "No"],
      "closed": false,
      "volume": 1000000,
      "liquidity": 500000,
      "link": "https://polymarket.com/event/..."
    }
  ]
}
```

### `/api/market-holders`
특정 마켓의 홀더 정보를 가져옵니다.

**쿼리 파라미터:**
- `conditionId` (필수): 마켓의 condition ID
- `outcomeIndex` (선택): 0 = Yes, 1 = No
- `limit` (선택): 반환할 홀더 수 (기본값: 10)

**응답 예시:**
```json
{
  "success": true,
  "conditionId": "condition-id",
  "outcomeIndex": 0,
  "holders": [
    {
      "proxyWallet": "0x...",
      "address": "0x...",
      "pseudonym": "trader123",
      "name": "Trader Name",
      "amount": 50000,
      "outcomeIndex": 0,
      "profileImage": "...",
      "bio": "..."
    }
  ],
  "count": 10
}
```

## 사용 방법

1. 페이지 로드 시 자동으로 Tech 마켓 목록이 표시됩니다.
2. 마켓 카드를 클릭하면 해당 마켓의 Yes/No 탑10 홀더 정보가 표시됩니다.
3. "데이터 새로고침" 버튼을 클릭하여 최신 마켓 데이터를 가져올 수 있습니다.

## 기술 스택

- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **API**: Next.js API Routes
- **External APIs**: 
  - Polymarket Gamma API (마켓 데이터)
  - Polymarket Data API (홀더 데이터)

## 주의사항

- Polymarket API는 rate limit이 있을 수 있으므로 과도한 요청을 피하세요.
- 홀더 정보는 마켓을 확장할 때만 로드되므로 성능에 최적화되어 있습니다.
- 일부 마켓은 홀더 정보가 없을 수 있습니다.
