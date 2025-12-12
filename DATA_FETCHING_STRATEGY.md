# Polymarket 데이터 수집 최적화 전략

## 🎯 현재 문제점

1. **캐싱 없음**: 모든 요청이 `cache: 'no-store'`로 설정되어 매번 API 호출
2. **Rate Limit 위험**: 불필요한 API 호출로 인한 제한 가능성
3. **느린 응답**: 매번 외부 API를 기다려야 함
4. **비용 증가**: Vercel Serverless Functions 실행 시간 증가

## ✅ 최적화 전략

### 1. **계층적 캐싱 전략 (Hierarchical Caching)**

```
사용자 요청
  ↓
[1] 클라이언트 캐시 (브라우저) - 1분
  ↓ (캐시 미스)
[2] Vercel Edge Cache (CDN) - 5분
  ↓ (캐시 미스)
[3] Next.js API Route Cache - 1분
  ↓ (캐시 미스)
[4] Polymarket API
```

### 2. **데이터 타입별 캐싱 전략**

| 데이터 타입 | TTL | 이유 |
|-----------|-----|------|
| **태그 목록** | 1시간 | 거의 변하지 않음 |
| **마켓 목록** | 1-5분 | 자주 변경되지만 완전 실시간 불필요 |
| **홀더 정보** | 30초-1분 | 상대적으로 자주 변경 |
| **마켓 상세 정보** | 1-2분 | 가격 등이 자주 변경 |

### 3. **Next.js 캐싱 옵션**

#### 옵션 A: **ISR (Incremental Static Regeneration)** - 추천
```typescript
// 정기적으로 재생성 (백그라운드)
export const revalidate = 60 // 60초마다 재생성
```

#### 옵션 B: **Time-based Revalidation**
```typescript
fetch(url, {
  next: { revalidate: 300 } // 5분 캐시
})
```

#### 옵션 C: **On-demand Revalidation**
```typescript
// 특정 이벤트 발생 시 재검증
revalidatePath('/api/tech-markets')
```

## 🚀 구현 방법

### 방법 1: Next.js ISR 사용 (가장 효율적)

**장점**:
- Vercel Edge Network 활용
- 자동 캐싱 및 재검증
- 빠른 응답 시간
- Rate limit 보호

**단점**:
- 최신 데이터가 약간 지연될 수 있음 (1-5분)

### 방법 2: Vercel KV 또는 Redis 캐싱

**장점**:
- 더 세밀한 캐시 제어
- 여러 인스턴스 간 캐시 공유
- 수동 캐시 무효화 가능

**단점**:
- 추가 비용
- 설정 복잡도 증가

### 방법 3: 클라이언트 측 캐싱 + SWR/React Query

**장점**:
- 사용자 경험 향상
- 서버 부하 감소
- 자동 재검증

**단점**:
- 초기 로딩은 여전히 필요

## 📊 추천 전략 (하이브리드)

### 단기 (즉시 적용 가능)
1. **Next.js revalidate 사용**: `next: { revalidate: 300 }` (5분)
2. **태그는 더 긴 캐시**: 1시간
3. **홀더 정보는 짧은 캐시**: 1분

### 중기 (성능 향상)
1. **SWR 또는 React Query 도입**: 클라이언트 측 캐싱
2. **Stale-while-revalidate 패턴**: 캐시된 데이터 먼저 보여주고 백그라운드 업데이트

### 장기 (확장성)
1. **Vercel KV 또는 Upstash Redis**: 분산 캐싱
2. **WebSocket 또는 Server-Sent Events**: 실시간 업데이트 (필요시)

## 🔧 Rate Limit 고려사항

**Polymarket 공식 Rate Limits** ([문서](https://docs.polymarket.com/quickstart/introduction/rate-limits)):

### GAMMA API
- **GAMMA (General)**: 750 requests / 10초
- **GAMMA /markets**: 125 requests / 10초
- **GAMMA Tags**: 100 requests / 10초
- **GAMMA /events**: 100 requests / 10초

### Data API
- **Data API (General)**: 200 requests / 10초
- **Data API /trades**: 75 requests / 10초

### 현재 사용 중인 엔드포인트
- `/tags` (GAMMA): **100 requests / 10초** → 최소 100ms 간격
- `/markets` (GAMMA): **125 requests / 10초** → 최소 80ms 간격
- `/holders` (Data API): **200 requests / 10초** → 최소 50ms 간격

**권장사항**:
- 태그 API: 1시간 캐시 (거의 변하지 않음) → 초당 0.00003 요청
- 마켓 API: 5분 캐시 → 초당 0.003 요청 (안전)
- 홀더 API: 1분 캐시 → 초당 0.017 요청 (안전)
- Rate limit은 **throttling 방식** (요청이 지연되지만 거부되지 않음)
- 에러 시 exponential backoff 적용 권장

## 💡 실전 예시

### 현재 (비효율적)
```typescript
// 매번 API 호출
fetch(url, { cache: 'no-store' })
```

### 최적화 후
```typescript
// 5분 캐시, 백그라운드 재검증
fetch(url, { 
  next: { revalidate: 300 },
  headers: { 'Cache-Control': 'public, s-maxage=300, stale-while-revalidate=600' }
})
```

## 📈 예상 성능 개선

| 메트릭 | 최적화 전 | 최적화 후 | 개선율 |
|--------|----------|-----------|--------|
| API 호출 수 | 100% | 0.3-1.7% | 98-99.7% 감소 |
| 평균 응답 시간 | 500-1000ms | 50-100ms | 80-90% 개선 |
| Rate limit 위험 | 높음 (초당 1+ 요청) | 매우 낮음 (초당 0.00003-0.017 요청) | - |
| Vercel 비용 | 높음 | 낮음 | 80-90% 감소 |

### Rate Limit 안전성 분석

**최적화 전** (캐싱 없음):
- 태그 API: 초당 1+ 요청 → **100 requests/10s 제한 위험** ⚠️
- 마켓 API: 초당 1+ 요청 → **125 requests/10s 제한 위험** ⚠️
- 홀더 API: 초당 1+ 요청 → **200 requests/10s 제한 위험** ⚠️

**최적화 후** (캐싱 적용):
- 태그 API: 초당 0.00003 요청 → **100 requests/10s의 0.0003% 사용** ✅
- 마켓 API: 초당 0.003 요청 → **125 requests/10s의 0.024% 사용** ✅
- 홀더 API: 초당 0.017 요청 → **200 requests/10s의 0.085% 사용** ✅

**결론**: Rate limit 여유가 충분하여 안전하게 운영 가능합니다.
