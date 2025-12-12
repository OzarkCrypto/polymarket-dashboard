import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const category = request.nextUrl.searchParams.get('category') || 'tech'
    
    // Tech 마켓 API로 리다이렉트
    const baseUrl = process.env.VERCEL_URL 
      ? `https://${process.env.VERCEL_URL}` 
      : 'http://localhost:3000'
    
    try {
      const response = await fetch(`${baseUrl}/api/tech-markets?category=${category}`, {
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        return NextResponse.json(data)
      }
    } catch (error) {
      console.log('Tech markets API error:', error)
    }
    
    // Fallback: 빈 데이터
    return NextResponse.json({
      success: false,
      error: 'Failed to fetch markets',
      markets: [],
      timestamp: new Date().toISOString(),
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

