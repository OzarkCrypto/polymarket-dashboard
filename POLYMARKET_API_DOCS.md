# Polymarket API 사용 가이드

현재 프로젝트에서 사용 중인 Polymarket API와 공식 문서 링크입니다.

## 📚 공식 문서

**메인 문서**: https://docs.polymarket.com/developers

## 🔌 사용 중인 API

### 1. **Gamma API** - 마켓 메타데이터
**Base URL**: `https://gamma-api.polymarket.com/`

#### 사용 중인 엔드포인트

##### `/tags` - 태그 목록 가져오기
```typescript
GET https://gamma-api.polymarket.com/tags
```

**사용 위치**: `app/api/tech-markets/route.ts`

**용도**: Tech 카테고리의 `tag_id`를 찾기 위해 사용

**응답 예시**:
```json
[
  {
    "id": "100381",
    "label": "Tech",
    "slug": "tech",
    "name": "Technology"
  }
]
```

**문서**: https://docs.polymarket.com/developers/gamma-markets-api

---

##### `/markets` - 마켓 목록 가져오기
```typescript
GET https://gamma-api.polymarket.com/markets?closed=false&limit=100&tag_id={tag_id}
```

**쿼리 파라미터**:
- `closed`: `false` (액티브 마켓만)
- `limit`: `100` (가져올 마켓 수)
- `tag_id`: Tech 카테고리의 tag_id (선택사항)

**사용 위치**: `app/api/tech-markets/route.ts`

**응답 구조**:
```json
[
  {
    "id": "market-id",
    "conditionId": "condition-id",
    "question": "Will OpenAI release GPT-5 in 2024?",
    "description": "...",
    "slug": "will-openai-release-gpt-5",
    "outcomes": ["Yes", "No"],
    "closed": false,
    "liquidity": 500000,
    "volume": 1000000,
    "endDate": "2024-12-31T00:00:00Z"
  }
]
```

**문서**: 
- https://docs.polymarket.com/developers/gamma-markets-api/fetch-markets-guide
- https://docs.polymarket.com/developers/gamma-markets-api/gamma-structure

---

### 2. **Data API** - 사용자 데이터 및 홀더 정보
**Base URL**: `https://data-api.polymarket.com/`

#### 사용 중인 엔드포인트

##### `/holders` - 마켓 홀더 정보 가져오기
```typescript
GET https://data-api.polymarket.com/holders?market={conditionId}&limit=10
```

**쿼리 파라미터**:
- `market`: 마켓의 condition ID (필수)
- `limit`: 반환할 홀더 수 (기본값: 100, 최대: 500)
- `minBalance`: 최소 잔액 필터 (선택사항)

**사용 위치**: `app/api/market-holders/route.ts`

**응답 구조**:
```json
[
  {
    "token": "token-address",
    "holders": [
      {
        "proxyWallet": "0x56687bf447db6ffa42ffe2204a05edaa20f55839",
        "pseudonym": "trader123",
        "name": "Trader Name",
        "amount": 50000,
        "outcomeIndex": 0,
        "profileImage": "...",
        "bio": "..."
      }
    ]
  }
]
```

**문서**: 
- https://docs.polymarket.com/api-reference/core/get-top-holders-for-markets

---

## 📖 전체 API 목록

Polymarket은 세 가지 주요 API를 제공합니다:

### 1. **Gamma API** (현재 사용 중)
- 마켓 메타데이터 (이벤트, 마켓, 시리즈, 태그)
- Base URL: `https://gamma-api.polymarket.com/`
- 문서: https://docs.polymarket.com/developers/gamma-markets-api

### 2. **Data API** (현재 사용 중)
- 사용자 데이터, 홀더 정보, 온체인 활동
- Base URL: `https://data-api.polymarket.com/`
- 문서: https://docs.polymarket.com/developers

### 3. **CLOB API** (미사용)
- 중앙 주문장 (Central Limit Order Book)
- 프로그램적 거래 (주문 생성, 취소, 관리)
- Base URL: `https://clob.polymarket.com/`
- 문서: https://docs.polymarket.com/developers/clob-api

---

## 🔍 현재 코드에서의 사용 예시

### Tech 마켓 가져오기
```typescript
// 1. Tech 태그 찾기
const tags = await fetch('https://gamma-api.polymarket.com/tags')
const techTag = tags.find(tag => tag.label.includes('Tech'))

// 2. Tech 마켓 가져오기
const markets = await fetch(
  `https://gamma-api.polymarket.com/markets?closed=false&tag_id=${techTag.id}`
)
```

### 마켓 홀더 가져오기
```typescript
// Yes 홀더 (outcomeIndex: 0)
const yesHolders = await fetch(
  `https://data-api.polymarket.com/holders?market=${conditionId}&limit=10`
)
// 응답에서 outcomeIndex === 0인 홀더만 필터링
```

---

## 📝 참고사항

1. **Rate Limiting**: API 호출 제한이 있을 수 있으므로 적절한 캐싱 사용 권장
2. **인증**: 현재 사용 중인 엔드포인트는 공개 API로 인증 불필요
3. **응답 구조**: API 응답 구조가 변경될 수 있으므로 공식 문서 확인 권장
4. **커뮤니티 SDK**: TypeScript SDK도 있지만 공식이 아님
   - https://polymarket-data.com/

---

## 🔗 유용한 링크

- **공식 문서**: https://docs.polymarket.com/developers
- **Gamma API 구조**: https://docs.polymarket.com/developers/gamma-markets-api/gamma-structure
- **마켓 가져오기 가이드**: https://docs.polymarket.com/developers/gamma-markets-api/fetch-markets-guide
- **홀더 API 레퍼런스**: https://docs.polymarket.com/api-reference/core/get-top-holders-for-markets
