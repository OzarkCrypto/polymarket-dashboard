# Polymarket 기업 관련 마켓 대시보드

Polymarket에서 기업 관련 마켓을 필터링하여 내부 정보 우위가 있을 수 있는 마켓을 찾는 대시보드입니다.

## 기능

- 🔍 **기업 관련 마켓 자동 필터링**: 주요 기업(OpenAI, Google, Apple 등)과 관련된 마켓만 표시
- 🎯 **정보 우위 마켓 식별**: 제품 출시일, 발표일 등 내부 정보를 가진 사람이 우위를 가질 수 있는 마켓 강조
- 📊 **대시보드**: Streamlit 기반의 인터랙티브 대시보드
- 📈 **시각화**: 기업별 마켓 분포 차트

## 설치

```bash
pip install -r requirements.txt
```

## 사용 방법

### 1. 데이터 수집 (스크립트 실행)

```bash
python polymarket_scraper.py
```

이 스크립트는 Polymarket에서 마켓 데이터를 수집하고, 기업 관련 마켓만 필터링하여 `polymarket_company_markets.csv` 파일로 저장합니다.

### 2. 대시보드 실행

```bash
streamlit run polymarket_dashboard.py
```

브라우저에서 대시보드가 자동으로 열립니다.

### 3. 대시보드 사용

1. 사이드바에서 **"데이터 새로고침"** 버튼을 클릭하여 최신 데이터를 수집합니다.
2. 필터를 사용하여:
   - 내부 정보 우위 가능성이 있는 마켓만 보기
   - 특정 기업 관련 마켓만 보기
3. 마켓 카드를 클릭하여 Polymarket에서 자세히 확인합니다.

## 필터링 기준

### 기업 키워드
- Tech: OpenAI, Google, Microsoft, Apple, Meta, Amazon, Tesla 등
- AI: Anthropic, DeepMind, Stability AI, Midjourney 등
- Crypto: Coinbase, Binance, Ethereum, Solana 등
- 기타 주요 기업들

### 정보 우위 패턴
- 제품 출시일 관련: "when will X release", "release date"
- 발표일 관련: "announcement date", "launch date"
- 제품 관련: "new model", "new version", "product release"

## 주의사항

⚠️ **법적 고지**: 내부자 정보를 이용한 거래는 법적 문제를 일으킬 수 있습니다. 이 도구는 정보 수집 목적으로만 사용하시기 바랍니다.

## 파일 구조

- `polymarket_scraper.py`: 데이터 수집 스크립트
- `polymarket_dashboard.py`: Streamlit 대시보드
- `requirements.txt`: 필요한 Python 패키지 목록
- `polymarket_company_markets.csv`: 수집된 마켓 데이터 (자동 생성)

## 문제 해결

### 데이터를 가져오지 못하는 경우

Polymarket은 동적 웹사이트이므로, 때때로 웹 스크래핑이 실패할 수 있습니다. 다음을 시도해보세요:

1. 브라우저에서 Polymarket에 직접 접속하여 사이트가 정상 작동하는지 확인
2. 네트워크 연결 확인
3. 몇 분 후 다시 시도 (Rate limiting 가능성)

### 더 정확한 데이터 수집을 원하는 경우

Selenium을 사용하여 브라우저를 자동화할 수 있습니다. `polymarket_scraper.py`를 수정하여 Selenium을 추가하세요:

```bash
pip install selenium
```

## 예시

예를 들어, 다음과 같은 마켓들이 필터링됩니다:

- ✅ "What day will OpenAI release a new frontier model?" → OpenAI 관련, 정보 우위 가능성 높음
- ✅ "When will Apple announce the iPhone 16?" → Apple 관련, 정보 우위 가능성 높음
- ❌ "Will Bitcoin reach $100k?" → 기업 관련 아님

## 라이선스

이 프로젝트는 개인 사용 목적으로 제공됩니다.

