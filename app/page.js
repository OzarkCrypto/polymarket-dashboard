'use client'

import { useState, useEffect } from 'react'

export default function Home() {
  const [markets, setMarkets] = useState([])
  const [holders, setHolders] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // 1. 마켓 목록 가져오기
      const marketsRes = await fetch('/api/markets')
      if (!marketsRes.ok) throw new Error('Failed to fetch markets')
      const marketsData = await marketsRes.json()
      
      if (marketsData.error) throw new Error(marketsData.error)
      
      setMarkets(marketsData)
      
      // 2. 모든 토큰 ID 수집
      const allTokens = []
      marketsData.forEach(event => {
        event.markets?.forEach(market => {
          if (market.clobTokenIds) {
            allTokens.push(...market.clobTokenIds)
          }
        })
      })
      
      // 3. 홀더 정보 가져오기 (한번에 여러 토큰)
      if (allTokens.length > 0) {
        const holdersRes = await fetch(`/api/holders?tokens=${allTokens.join(',')}`)
        if (holdersRes.ok) {
          const holdersData = await holdersRes.json()
          
          // 토큰별로 정리
          const holdersMap = {}
          holdersData.forEach(item => {
            holdersMap[item.token] = item.holders?.slice(0, 10) || []
          })
          setHolders(holdersMap)
        }
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const formatAmount = (amount) => {
    if (amount >= 1000000) return `$${(amount / 1000000).toFixed(1)}M`
    if (amount >= 1000) return `$${(amount / 1000).toFixed(1)}K`
    return `$${amount.toFixed(0)}`
  }

  const formatPrice = (price) => {
    return (parseFloat(price) * 100).toFixed(1) + '%'
  }

  if (loading) return <div className="loading">Loading Tech Markets...</div>
  if (error) return <div className="error">Error: {error}</div>

  return (
    <div>
      <h1>Polymarket Tech Markets</h1>
      <button onClick={fetchData}>🔄 Refresh</button>
      
      {markets.length === 0 && <p>No markets found</p>}
      
      {markets.map(event => (
        <div key={event.id}>
          {event.markets?.map(market => {
            const yesToken = market.clobTokenIds?.[0]
            const noToken = market.clobTokenIds?.[1]
            const yesPrice = market.outcomePrices?.[0]
            const noPrice = market.outcomePrices?.[1]
            const yesHolders = holders[yesToken] || []
            const noHolders = holders[noToken] || []
            
            return (
              <div key={market.id} className="market">
                <div className="market-title">
                  <a href={event.url} target="_blank" rel="noopener noreferrer">
                    {market.question || event.title}
                  </a>
                </div>
                
                <div className="price">
                  YES: {yesPrice ? formatPrice(yesPrice) : '-'} / NO: {noPrice ? formatPrice(noPrice) : '-'}
                </div>
                
                <div className="holders-section">
                  <div className="holder-list yes">
                    <h3>YES TOP 10 HOLDERS</h3>
                    {yesHolders.length === 0 && <div className="loading">No data</div>}
                    {yesHolders.map((h, i) => (
                      <div key={i} className="holder">
                        <a 
                          href={`https://polymarket.com/profile/${h.proxyWallet}`}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {h.name || h.pseudonym || h.proxyWallet?.slice(0, 10) + '...'}
                        </a>
                        <span className="amount">{formatAmount(h.amount || 0)}</span>
                      </div>
                    ))}
                  </div>
                  
                  <div className="holder-list no">
                    <h3>NO TOP 10 HOLDERS</h3>
                    {noHolders.length === 0 && <div className="loading">No data</div>}
                    {noHolders.map((h, i) => (
                      <div key={i} className="holder">
                        <a 
                          href={`https://polymarket.com/profile/${h.proxyWallet}`}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          {h.name || h.pseudonym || h.proxyWallet?.slice(0, 10) + '...'}
                        </a>
                        <span className="amount">{formatAmount(h.amount || 0)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      ))}
    </div>
  )
}
