"""
Polymarket Scraper - 기업 관련 마켓 수집
==========================================
Polymarket에서 기업 관련 마켓을 수집하고 필터링합니다.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from datetime import datetime
import re
from typing import List, Dict, Optional

# 주요 기업 키워드 (확장 가능)
COMPANY_KEYWORDS = [
    # Tech Companies
    'openai', 'google', 'microsoft', 'apple', 'meta', 'facebook', 'amazon', 'tesla',
    'nvidia', 'netflix', 'twitter', 'x.com', 'uber', 'airbnb', 'spotify', 'snapchat',
    'tiktok', 'bytedance', 'alibaba', 'tencent', 'samsung', 'sony', 'intel', 'amd',
    'qualcomm', 'oracle', 'salesforce', 'adobe', 'paypal', 'visa', 'mastercard',
    
    # AI Companies
    'anthropic', 'claude', 'deepmind', 'stability ai', 'midjourney', 'runway',
    'character.ai', 'perplexity', 'cohere', 'mistral', 'inflection',
    
    # Crypto/Blockchain Companies
    'coinbase', 'binance', 'kraken', 'ftx', 'crypto.com', 'gemini', 'bitfinex',
    'ethereum', 'solana', 'polygon', 'avalanche', 'cardano', 'polkadot',
    
    # Automotive
    'ford', 'gm', 'general motors', 'toyota', 'honda', 'bmw', 'mercedes', 'volkswagen',
    'rivian', 'lucid', 'nio', 'xpeng', 'li auto',
    
    # Other Major Companies
    'disney', 'warner bros', 'paramount', 'comcast', 'verizon', 'at&t', 't-mobile',
    'boeing', 'lockheed', 'spacex', 'blue origin', 'virgin galactic',
    'pfizer', 'moderna', 'johnson & johnson', 'novavax',
    'walmart', 'target', 'costco', 'home depot', 'lowes',
]

# 제품 출시 관련 키워드
PRODUCT_KEYWORDS = [
    'release', 'launch', 'announce', 'announcement', 'product', 'model', 'version',
    'update', 'upgrade', 'feature', 'beta', 'alpha', 'preview', 'demo',
    'ship', 'shipping', 'available', 'coming', 'debut', 'unveil', 'reveal'
]

# 정보 우위가 있을 수 있는 패턴
INSIDER_INFO_PATTERNS = [
    r'release.*date',
    r'launch.*date',
    r'when.*will.*release',
    r'when.*will.*launch',
    r'date.*of.*release',
    r'date.*of.*launch',
    r'product.*release',
    r'new.*model',
    r'new.*version',
    r'upcoming.*release',
]


class PolymarketScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        self.base_url = "https://polymarket.com"
        
    def fetch_markets_page(self, page: int = 1, category: Optional[str] = None) -> Optional[str]:
        """Polymarket 마켓 페이지 가져오기"""
        try:
            # Polymarket의 마켓 페이지
            url = f"{self.base_url}/markets"
            params = {}
            if category:
                params['category'] = category
            if page > 1:
                params['page'] = page
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            return None
    
    def parse_markets_from_html(self, html: str) -> List[Dict]:
        """HTML에서 마켓 정보 파싱"""
        markets = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # Polymarket은 React 기반이므로, JSON-LD나 data 속성에서 정보 추출 시도
        # 1. JSON-LD 스크립트 태그에서 데이터 추출
        scripts = soup.find_all('script', type='application/json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                # 중첩된 구조에서 마켓 정보 찾기
                if isinstance(data, dict):
                    # 다양한 가능한 키 확인
                    for key in ['events', 'markets', 'data', 'items']:
                        if key in data and isinstance(data[key], list):
                            for item in data[key]:
                                if isinstance(item, dict):
                                    title = item.get('title') or item.get('question') or item.get('name', '')
                                    if title:
                                        slug = item.get('slug', '') or item.get('id', '')
                                        link = item.get('url', '')
                                        if not link and slug:
                                            link = f"{self.base_url}/event/{slug}"
                                        markets.append({
                                            'title': title,
                                            'description': item.get('description', ''),
                                            'link': link,
                                            'scraped_at': datetime.now().isoformat()
                                        })
            except (json.JSONDecodeError, AttributeError):
                continue
        
        # 2. 일반적인 HTML 구조에서 추출 (폴백)
        if not markets:
            # 링크가 /event/로 시작하는 모든 링크 찾기
            event_links = soup.find_all('a', href=re.compile(r'/event/'))
            seen_titles = set()
            
            for link_elem in event_links:
                try:
                    href = link_elem.get('href', '')
                    title = link_elem.get_text(strip=True)
                    
                    # 중복 제거
                    if title and title not in seen_titles:
                        seen_titles.add(title)
                        full_link = self.base_url + href if not href.startswith('http') else href
                        
                        markets.append({
                            'title': title,
                            'description': '',
                            'link': full_link,
                            'scraped_at': datetime.now().isoformat()
                        })
                except Exception:
                    continue
        
        return markets
    
    def get_category_tag_id(self, category_name: str = "tech") -> Optional[str]:
        """카테고리 이름으로 tag_id 찾기"""
        try:
            tags_url = "https://gamma-api.polymarket.com/tags"
            response = self.session.get(tags_url, timeout=15)
            
            if response.status_code == 200:
                tags = response.json()
                if isinstance(tags, list):
                    for tag in tags:
                        if isinstance(tag, dict):
                            label = tag.get('label', '').lower()
                            if category_name.lower() in label or label in category_name.lower():
                                return tag.get('id')
                elif isinstance(tags, dict):
                    # 응답이 dict인 경우
                    if 'data' in tags:
                        for tag in tags['data']:
                            label = tag.get('label', '').lower()
                            if category_name.lower() in label or label in category_name.lower():
                                return tag.get('id')
        except Exception as e:
            print(f"Error fetching tags: {e}")
        
        return None
    
    def fetch_markets_api(self, limit: int = 100, category: Optional[str] = None) -> List[Dict]:
        """Polymarket API를 통해 마켓 데이터 가져오기"""
        markets = []
        
        # 카테고리 필터링을 위한 tag_id 가져오기
        tag_id = None
        if category:
            tag_id = self.get_category_tag_id(category)
            if tag_id:
                print(f"✅ '{category}' 카테고리 tag_id: {tag_id}")
            else:
                print(f"⚠️  '{category}' 카테고리 tag_id를 찾지 못했습니다. 전체 마켓을 가져옵니다.")
        
        # Polymarket Markets API 시도
        try:
            markets_url = "https://gamma-api.polymarket.com/markets"
            params = {
                'closed': 'false',
                'limit': limit,
                'offset': 0
            }
            
            if tag_id:
                params['tag_id'] = tag_id
            
            response = self.session.get(markets_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                # API 응답 구조에 맞게 파싱
                if isinstance(data, list):
                    markets = data
                elif isinstance(data, dict):
                    if 'data' in data:
                        markets = data['data']
                    elif 'events' in data:
                        markets = data['events']
                    elif 'markets' in data:
                        markets = data['markets']
                    
                    # markets 리스트 안에 data가 있는 경우
                    if markets and len(markets) > 0 and isinstance(markets[0], dict) and 'data' in markets[0]:
                        markets = markets[0]['data']
                
                # 마켓 데이터 정규화
                normalized_markets = []
                for market in markets:
                    if isinstance(market, dict):
                        # Polymarket API 응답 구조에 맞게 정규화
                        title = market.get('question') or market.get('title') or market.get('name', '')
                        if title:
                            slug = market.get('slug', '') or market.get('id', '')
                            link = market.get('url', '')
                            if not link and slug:
                                link = f"{self.base_url}/event/{slug}"
                            
                            # conditionId 추출
                            condition_id = market.get('conditionId') or market.get('condition_id') or market.get('id') or ''
                            if not condition_id and slug:
                                condition_id = slug
                            
                            normalized_markets.append({
                                'title': title,
                                'question': title,  # API와 일관성 유지
                                'description': market.get('description', ''),
                                'link': link,
                                'conditionId': condition_id,
                                'id': market.get('id') or slug or condition_id,
                                'slug': slug,
                                'outcomes': market.get('outcomes', ['Yes', 'No']),
                                'closed': market.get('closed', False),
                                'scraped_at': datetime.now().isoformat()
                            })
                markets = normalized_markets
        except Exception as e:
            print(f"API fetch failed: {e}")
        
        # API 실패 시 웹 스크래핑으로 폴백
        if not markets:
            try:
                html = self.fetch_markets_page(category=category)
                if html:
                    markets = self.parse_markets_from_html(html)
            except Exception as e:
                print(f"Web scraping also failed: {e}")
        
        return markets
    
    def is_company_related(self, title: str, description: str = "") -> tuple[bool, List[str]]:
        """마켓이 기업 관련인지 확인"""
        text = (title + " " + description).lower()
        matched_companies = []
        
        for company in COMPANY_KEYWORDS:
            if company.lower() in text:
                matched_companies.append(company)
        
        return len(matched_companies) > 0, matched_companies
    
    def has_insider_info_potential(self, title: str, description: str = "") -> bool:
        """내부 정보 우위가 있을 수 있는 마켓인지 확인"""
        text = (title + " " + description).lower()
        
        # 제품 출시 관련 키워드 확인
        has_product_keyword = any(keyword in text for keyword in PRODUCT_KEYWORDS)
        
        # 패턴 매칭
        has_pattern = any(re.search(pattern, text, re.I) for pattern in INSIDER_INFO_PATTERNS)
        
        return has_product_keyword or has_pattern
    
    def filter_company_markets(self, markets: List[Dict]) -> pd.DataFrame:
        """기업 관련 마켓 필터링"""
        filtered = []
        
        for market in markets:
            # 다양한 필드명에서 title 가져오기
            title = market.get('title', '') or market.get('question', '') or market.get('name', '')
            description = market.get('description', '') or market.get('desc', '')
            
            is_company, companies = self.is_company_related(title, description)
            has_insider_potential = self.has_insider_info_potential(title, description)
            
            if is_company:
                # 표준화된 필드명으로 저장
                filtered_market = {
                    'title': title,
                    'description': description,
                    'link': market.get('link', '') or market.get('url', ''),
                    'is_company_related': True,
                    'matched_companies': ', '.join(companies),
                    'has_insider_potential': has_insider_potential,
                    'scraped_at': market.get('scraped_at', datetime.now().isoformat())
                }
                filtered.append(filtered_market)
        
        return pd.DataFrame(filtered)
    
    def scrape_all_markets(self, max_pages: int = 10, use_selenium: bool = False, category: Optional[str] = None) -> pd.DataFrame:
        """모든 마켓 수집 및 필터링"""
        category_text = f" ({category} 카테고리)" if category else ""
        print(f"🔍 Polymarket 마켓 수집 중{category_text}...")
        all_markets = []
        
        # Selenium 사용 옵션
        if use_selenium:
            try:
                from selenium import webdriver
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                print("🌐 Selenium을 사용하여 동적 콘텐츠 로드 중...")
                options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                
                driver = webdriver.Chrome(options=options)
                url = f"{self.base_url}/markets"
                if category:
                    url += f"?category={category}"
                driver.get(url)
                
                # 페이지 로드 대기
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # 스크롤하여 더 많은 콘텐츠 로드
                for i in range(3):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                
                html = driver.page_source
                driver.quit()
                
                markets = self.parse_markets_from_html(html)
                all_markets.extend(markets)
                print(f"✅ Selenium을 통해 {len(markets)}개 마켓 수집")
            except ImportError:
                print("⚠️  Selenium이 설치되지 않았습니다. 일반 스크래핑으로 진행합니다.")
                use_selenium = False
            except Exception as e:
                print(f"⚠️  Selenium 오류: {e}. 일반 스크래핑으로 진행합니다.")
                use_selenium = False
        
        # API 방식 시도 (Selenium 미사용 또는 실패 시)
        if not use_selenium or len(all_markets) == 0:
            markets = self.fetch_markets_api(limit=500, category=category)
            if markets:
                all_markets.extend(markets)
                print(f"✅ API를 통해 {len(markets)}개 마켓 수집")
            else:
                # 웹 스크래핑 방식
                for page in range(1, max_pages + 1):
                    html = self.fetch_markets_page(page=page, category=category)
                    if html:
                        markets = self.parse_markets_from_html(html)
                        if not markets:
                            break
                        all_markets.extend(markets)
                        print(f"📄 페이지 {page}: {len(markets)}개 마켓 수집")
                        time.sleep(1)  # Rate limiting
                    else:
                        break
        
        # 중복 제거
        seen_titles = set()
        unique_markets = []
        for market in all_markets:
            title = market.get('title', '') or market.get('question', '')
            if title and title not in seen_titles:
                seen_titles.add(title)
                unique_markets.append(market)
        
        print(f"\n📊 총 {len(unique_markets)}개 고유 마켓 수집 완료")
        
        # 기업 관련 마켓 필터링
        print("\n🔍 기업 관련 마켓 필터링 중...")
        df = self.filter_company_markets(unique_markets)
        
        print(f"✅ {len(df)}개 기업 관련 마켓 발견")
        if len(df) > 0 and 'has_insider_potential' in df.columns:
            print(f"   - 내부 정보 우위 가능성: {df['has_insider_potential'].sum()}개")
        
        return df
    
    def scrape_tech_markets(self, max_pages: int = 10, use_selenium: bool = False) -> pd.DataFrame:
        """Tech 카테고리 마켓만 수집"""
        return self.scrape_all_markets(max_pages=max_pages, use_selenium=use_selenium, category="tech")


def main():
    """메인 실행 함수"""
    scraper = PolymarketScraper()
    df = scraper.scrape_all_markets(max_pages=5)
    
    if len(df) > 0:
        # 결과 저장
        output_file = "polymarket_company_markets.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 결과 저장: {output_file}")
        
        # 내부 정보 우위 가능성이 높은 마켓만 출력
        insider_markets = df[df['has_insider_potential'] == True]
        if len(insider_markets) > 0:
            print("\n🎯 내부 정보 우위 가능성이 높은 마켓:")
            for idx, row in insider_markets.iterrows():
                print(f"\n  {row['title']}")
                print(f"    기업: {row['matched_companies']}")
                print(f"    링크: {row.get('link', 'N/A')}")
    else:
        print("\n⚠️  기업 관련 마켓을 찾지 못했습니다.")


if __name__ == "__main__":
    main()

