import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const maxPages = parseInt(searchParams.get('pages') || '3')
    
    // Call Python scraper via API route
    // In Vercel, we'll use the Python serverless function
    // For local dev, we can call the Python script directly
    
    const baseUrl = process.env.VERCEL_URL 
      ? `https://${process.env.VERCEL_URL}` 
      : 'http://localhost:3000'
    
    try {
      // Try to call Python API (for Vercel deployment)
      const pythonApiUrl = `${baseUrl}/api/scrape-py?pages=${maxPages}`
      const response = await fetch(pythonApiUrl, {
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        return NextResponse.json(data)
      }
    } catch (error) {
      console.log('Python API not available, using fallback')
    }
    
    // Fallback: Simple mock data or direct scraping
    // For production, this should call the Python scraper
    const mockMarkets = [
      {
        title: 'What day will OpenAI release a new frontier model?',
        description: 'Prediction market for OpenAI frontier model release date',
        link: 'https://polymarket.com/event/what-day-will-openai-release-a-new-frontier-model',
        matched_companies: 'openai',
        has_insider_potential: true,
        scraped_at: new Date().toISOString(),
      },
    ]
    
    return NextResponse.json({
      success: true,
      count: mockMarkets.length,
      markets: mockMarkets,
      timestamp: new Date().toISOString(),
      note: 'Using fallback data. Python scraper will be used in production.',
    })
    
  } catch (error: any) {
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Unknown error',
      },
      { status: 500 }
    )
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  })
}

