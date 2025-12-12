import { NextRequest, NextResponse } from 'next/server'

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const conditionId = searchParams.get('conditionId')
    const outcomeIndex = searchParams.get('outcomeIndex') // 0 = Yes, 1 = No
    const limit = parseInt(searchParams.get('limit') || '10')
    
    if (!conditionId) {
      return NextResponse.json(
        { success: false, error: 'conditionId is required' },
        { status: 400 }
      )
    }
    
    try {
      // Polymarket Data API를 사용하여 홀더 정보 가져오기
      // condition_id는 token address 형식일 수 있으므로 변환 필요
      const holdersUrl = `https://data-api.polymarket.com/holders?market=${conditionId}&limit=${limit}`
      
      const holdersResponse = await fetch(holdersUrl, {
        headers: {
          'Accept': 'application/json',
        },
        next: { revalidate: 60 } // 1분 캐시 (홀더 정보는 상대적으로 자주 변경)
      })
      
      if (holdersResponse.ok) {
        const holdersData = await holdersResponse.json()
        
        // 응답 구조에 따라 파싱
        let holders: any[] = []
        if (Array.isArray(holdersData)) {
          // 첫 번째 요소의 holders 배열 사용
          if (holdersData[0]?.holders) {
            holders = holdersData[0].holders
          } else {
            holders = holdersData
          }
        } else if (holdersData.holders) {
          holders = holdersData.holders
        }
        
        // outcomeIndex로 필터링 (0 = Yes, 1 = No)
        if (outcomeIndex !== null) {
          const outcomeIdx = parseInt(outcomeIndex)
          holders = holders.filter((h: any) => h.outcomeIndex === outcomeIdx)
        }
        
        // amount 기준으로 정렬 (내림차순)
        holders.sort((a: any, b: any) => (b.amount || 0) - (a.amount || 0))
        
        // 상위 N개만 반환
        holders = holders.slice(0, limit)
        
        return NextResponse.json({
          success: true,
          conditionId,
          outcomeIndex: outcomeIndex ? parseInt(outcomeIndex) : null,
          holders: holders.map((h: any) => ({
            proxyWallet: h.proxyWallet,
            address: h.proxyWallet,
            pseudonym: h.pseudonym || h.name || 'Anonymous',
            name: h.name || h.pseudonym || 'Anonymous',
            amount: h.amount || 0,
            outcomeIndex: h.outcomeIndex,
            profileImage: h.profileImage || h.profileImageOptimized,
            bio: h.bio || '',
          })),
          count: holders.length,
        })
      } else {
        // API 실패 시 빈 배열 반환
        return NextResponse.json({
          success: true,
          conditionId,
          outcomeIndex: outcomeIndex ? parseInt(outcomeIndex) : null,
          holders: [],
          count: 0,
          note: 'Holders data not available',
        })
      }
    } catch (error: any) {
      console.error('Error fetching holders:', error)
      return NextResponse.json({
        success: true,
        conditionId,
        outcomeIndex: outcomeIndex ? parseInt(outcomeIndex) : null,
        holders: [],
        count: 0,
        error: error.message,
      })
    }
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
