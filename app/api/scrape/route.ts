import { NextRequest, NextResponse } from 'next/server'

// Tech 마켓 API와 동일한 로직을 직접 구현 (순환 참조 방지)
export async function GET(request: NextRequest) {
  try {
    const category = request.nextUrl.searchParams.get('category') || 'tech'
    
    // 직접 Polymarket API 호출
    try {
      // 1. Tech 카테고리 tag_id 찾기
      const tagsResponse = await fetch('https://gamma-api.polymarket.com/tags', {
        headers: {
          'Accept': 'application/json',
        },
        cache: 'no-store' // Vercel 호환성
      })
      
      let techTagId = null
      if (tagsResponse.ok) {
        const tags = await tagsResponse.json()
        if (Array.isArray(tags)) {
          const techTag = tags.find((tag: any) => 
            tag.label?.toLowerCase().includes('tech') || 
            tag.slug?.toLowerCase().includes('tech') ||
            tag.name?.toLowerCase().includes('tech')
          )
          if (techTag) {
            techTagId = techTag.id
          }
        }
      }
      
      // 2. Tech 카테고리 마켓 가져오기 (액티브만)
      const marketsUrl = techTagId 
        ? `https://gamma-api.polymarket.com/markets?closed=false&limit=100&tag_id=${techTagId}`
        : 'https://gamma-api.polymarket.com/markets?closed=false&limit=100'
      
      const marketsResponse = await fetch(marketsUrl, {
        headers: {
          'Accept': 'application/json',
        },
        cache: 'no-store' // Vercel 호환성
      })
      
      if (marketsResponse.ok) {
        const marketsData = await marketsResponse.json()
        let markets = Array.isArray(marketsData) ? marketsData : marketsData.data || []
        
        // 마켓 데이터 정규화
        const normalizedMarkets = markets
          .map((market: any) => {
            const conditionId = market.conditionId || 
                               market.condition_id || 
                               market.id || 
                               market.token_id ||
                               (market.tokens && market.tokens[0]?.token_id) ||
                               ''
            
            const outcomes = market.outcomes || 
                            (market.tokens && market.tokens.map((t: any) => t.outcome || t.label)) ||
                            ['Yes', 'No']
            
            return {
              id: market.id || market.slug || conditionId,
              conditionId: conditionId,
              question: market.question || market.title || market.name || '',
              description: market.description || market.desc || '',
              slug: market.slug || market.id || '',
              outcomes: outcomes,
              closed: market.closed || market.isResolved || false,
              endDate: market.endDate || market.end_date,
              liquidity: market.liquidity || market.totalLiquidity || 0,
              volume: market.volume || market.totalVolume || 0,
              link: `https://polymarket.com/event/${market.slug || market.id || conditionId}`,
            }
          })
          .filter((m: any) => !m.closed && m.conditionId)
        
        return NextResponse.json({
          success: true,
          count: normalizedMarkets.length,
          markets: normalizedMarkets,
          timestamp: new Date().toISOString(),
        }, { status: 200 })
      } else {
        // API 응답이 실패한 경우
        const errorText = await marketsResponse.text().catch(() => 'Unknown error')
        console.error('Markets API error:', marketsResponse.status, errorText)
        return NextResponse.json({
          success: false,
          error: `API returned ${marketsResponse.status}`,
          markets: [],
          timestamp: new Date().toISOString(),
        }, { status: 200 })
      }
    } catch (error: any) {
      console.error('Direct API error:', error)
      return NextResponse.json({
        success: false,
        error: error.message || 'Failed to fetch markets',
        markets: [],
        timestamp: new Date().toISOString(),
      }, { status: 200 })
    }
    
  } catch (error: any) {
    console.error('Unexpected error:', error)
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Unknown error',
        markets: [],
        timestamp: new Date().toISOString(),
      },
      { status: 200 } // 클라이언트에서 처리할 수 있도록 200 반환
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

