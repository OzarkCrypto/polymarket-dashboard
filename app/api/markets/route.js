export async function GET() {
  try {
    const res = await fetch(
      'https://gamma-api.polymarket.com/events?tag=tech&closed=false&limit=50',
      { next: { revalidate: 60 } }
    );
    
    if (!res.ok) {
      throw new Error('Failed to fetch markets');
    }
    
    const events = await res.json();
    
    // 마켓 데이터 정리
    const markets = events.map(event => ({
      id: event.id,
      title: event.title,
      slug: event.slug,
      url: `https://polymarket.com/event/${event.slug}`,
      markets: event.markets?.map(m => ({
        id: m.id,
        question: m.question,
        outcomePrices: m.outcomePrices, // ["0.85", "0.15"] 형태
        clobTokenIds: m.clobTokenIds,   // [yesTokenId, noTokenId]
      })) || []
    }));
    
    return Response.json(markets);
  } catch (error) {
    console.error('Markets API error:', error);
    return Response.json({ error: error.message }, { status: 500 });
  }
}
