"""
Vercel Serverless Function - Polymarket Scraper API (Python)
"""
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

try:
    from polymarket_scraper import PolymarketScraper
    import pandas as pd
except ImportError:
    # Fallback implementation
    import requests
    from bs4 import BeautifulSoup
    import re
    from datetime import datetime
    from typing import List, Dict
    
    COMPANY_KEYWORDS = [
        'openai', 'google', 'microsoft', 'apple', 'meta', 'facebook', 'amazon', 'tesla',
        'nvidia', 'netflix', 'twitter', 'x.com', 'uber', 'airbnb', 'spotify', 'snapchat',
        'anthropic', 'claude', 'deepmind', 'stability ai', 'midjourney', 'runway',
        'coinbase', 'binance', 'ethereum', 'solana', 'spacex', 'disney', 'tesla',
    ]
    
    PRODUCT_KEYWORDS = [
        'release', 'launch', 'announce', 'announcement', 'product', 'model', 'version',
        'update', 'upgrade', 'feature', 'beta', 'alpha', 'preview', 'demo',
    ]
    
    INSIDER_INFO_PATTERNS = [
        r'release.*date', r'launch.*date', r'when.*will.*release', r'when.*will.*launch',
        r'date.*of.*release', r'product.*release', r'new.*model', r'new.*version',
    ]

def handler(req):
    """Vercel Serverless Function handler"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        
        method = req.get('method', 'GET')
        if method == 'OPTIONS':
            return {'statusCode': 200, 'headers': headers, 'body': ''}
        
        # Get query parameters
        query = req.get('query', {}) or {}
        if isinstance(query, str):
            import urllib.parse
            query = dict(urllib.parse.parse_qsl(query))
        
        max_pages = int(query.get('pages', '3'))
        category = query.get('category', None)  # 'tech' 등 카테고리 필터
        
        # Try to use PolymarketScraper if available
        try:
            scraper = PolymarketScraper()
            if category:
                df = scraper.scrape_all_markets(max_pages=max_pages, use_selenium=False, category=category)
            else:
                df = scraper.scrape_all_markets(max_pages=max_pages, use_selenium=False)
            
            # DataFrame을 dict로 변환할 때 conditionId 포함
            markets_list = []
            if len(df) > 0:
                for _, row in df.iterrows():
                    market_dict = row.to_dict()
                    # conditionId가 없으면 추가 시도
                    if 'conditionId' not in market_dict or not market_dict.get('conditionId'):
                        # link에서 slug 추출하여 conditionId로 사용
                        link = market_dict.get('link', '')
                        if link:
                            import re
                            slug_match = re.search(r'/event/([^/?]+)', link)
                            if slug_match:
                                market_dict['conditionId'] = slug_match.group(1)
                    markets_list.append(market_dict)
            
            result = {
                'success': True,
                'count': len(markets_list),
                'markets': markets_list,
                'timestamp': datetime.now().isoformat()
            }
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(result, default=str)
            }
        except Exception as e:
            # Fallback to simple scraping
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            })
            
            markets = []
            base_url = "https://polymarket.com"
            
            try:
                response = session.get(f"{base_url}/markets", timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    links = soup.find_all('a', href=re.compile(r'/event/'))
                    
                    seen = set()
                    for link in links[:50]:
                        href = link.get('href', '')
                        title = link.get_text(strip=True)
                        if title and title not in seen:
                            seen.add(title)
                            markets.append({
                                'title': title,
                                'description': '',
                                'link': base_url + href if not href.startswith('http') else href,
                                'scraped_at': datetime.now().isoformat()
                            })
            except Exception as scrape_error:
                pass
            
            # Filter company-related markets
            filtered = []
            for market in markets:
                text = (market['title'] + ' ' + market.get('description', '')).lower()
                matched_companies = [c for c in COMPANY_KEYWORDS if c.lower() in text]
                
                if matched_companies:
                    has_insider = any(
                        keyword in text for keyword in PRODUCT_KEYWORDS
                    ) or any(
                        re.search(pattern, text, re.I) for pattern in INSIDER_INFO_PATTERNS
                    )
                    
                    filtered.append({
                        **market,
                        'is_company_related': True,
                        'matched_companies': ', '.join(matched_companies),
                        'has_insider_potential': has_insider
                    })
            
            result = {
                'success': True,
                'count': len(filtered),
                'markets': filtered,
                'timestamp': datetime.now().isoformat()
            }
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(result, default=str)
            }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'success': False, 'error': str(e)})
        }

