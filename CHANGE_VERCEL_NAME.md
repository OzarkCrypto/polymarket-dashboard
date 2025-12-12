# Vercel 프로젝트 이름 변경 가이드

## 방법 1: Vercel 대시보드에서 변경 (가장 쉬움)

1. [Vercel 대시보드](https://vercel.com/dashboard) 접속
2. 프로젝트 선택 (`polymarket-dashboard`)
3. **Settings** 탭 클릭
4. **General** 섹션에서 **Project Name** 찾기
5. 이름을 `polymarket_company_markets`로 변경
6. **Save** 클릭

변경 후 URL이 `https://polymarket-company-markets.vercel.app` 형식으로 변경됩니다.

## 방법 2: Vercel CLI로 변경

```bash
# Vercel CLI 설치 (없는 경우)
npm install -g vercel

# 프로젝트 이름 변경
vercel project rename polymarket_company_markets

# 또는 현재 디렉토리에서
vercel --prod
# 프롬프트에서 프로젝트 이름 입력: polymarket_company_markets
```

## 참고사항

- 프로젝트 이름은 URL에 반영됩니다
- 이름에 하이픈(-)은 언더스코어(_)로 변환될 수 있습니다
- 변경 후 배포가 자동으로 트리거될 수 있습니다
