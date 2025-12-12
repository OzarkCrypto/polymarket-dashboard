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

**Polymarket Rate Limits**:
- Data API: 200 requests / 10초
- Gamma API: 공개 문서에 명시되지 않음 (보수적으로 가정)

**권장사항**:
- 최소 1초당 1요청 이하로 제한
- 캐싱으로 실제 API 호출 최소화
- 에러 시 exponential backoff

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

| 메트릭 | 현재 | 최적화 후 | 개선율 |
|--------|------|-----------|--------|
| API 호출 수 | 100% | 5-10% | 90-95% 감소 |
| 평균 응답 시간 | 500-1000ms | 50-100ms | 80-90% 개선 |
| Rate limit 위험 | 높음 | 낮음 | - |
| Vercel 비용 | 높음 | 낮음 | 80-90% 감소 |
