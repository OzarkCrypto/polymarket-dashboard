"""
Vercel Serverless Function for Polymarket scraping
"""
import json
import sys
import os

# Add parent directory to path to import scraper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from polymarket_scraper import PolymarketScraper

def handler(req):
    """Vercel Serverless Function handler"""
    try:
        # CORS headers
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        
        # Handle OPTIONS request
        if req.get('method') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': ''
            }
        
        # Get query parameters
        query = req.get('query', {})
        use_selenium = query.get('selenium', 'false').lower() == 'true'
        max_pages = int(query.get('pages', '5'))
        
        # Scrape markets
        scraper = PolymarketScraper()
        df = scraper.scrape_all_markets(max_pages=max_pages, use_selenium=use_selenium)
        
        # Convert DataFrame to JSON
        result = {
            'success': True,
            'count': len(df),
            'markets': df.to_dict('records') if len(df) > 0 else [],
            'timestamp': str(pd.Timestamp.now())
        }
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(result, default=str)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }

