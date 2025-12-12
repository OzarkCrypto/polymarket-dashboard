export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const tokens = searchParams.get('tokens'); // comma separated token IDs
    
    if (!tokens) {
      return Response.json({ error: 'tokens parameter required' }, { status: 400 });
    }
    
    const res = await fetch(
      `https://data-api.polymarket.com/holders?tokens=${tokens}`,
      { next: { revalidate: 60 } }
    );
    
    if (!res.ok) {
      throw new Error('Failed to fetch holders');
    }
    
    const data = await res.json();
    return Response.json(data);
  } catch (error) {
    console.error('Holders API error:', error);
    return Response.json({ error: error.message }, { status: 500 });
  }
}
