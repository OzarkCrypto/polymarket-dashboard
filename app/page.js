'use client'

import { useState, useEffect, useCallback } from 'react'

const TECH_MARKETS_DATA = [
  {
    id: '1',
    title: 'Will Polymarket US go live in 2025?',
    probability: 100,
    prediction: 'Yes',
    volume: '$59m',
    volumeToday: '$24m',
    liquidity: '$3m',
    comments: 4280,
    endsIn: '25 days',
    tags: ['Tech', 'Politics'],
    hot: true
  },
  {
    id: '2', 
    title: '#1 Searched Person on Google this year?',
    probability: 100,
    prediction: 'd4vd',
    volume: '$55m',
    volumeToday: '$3m',
    liquidity: '$535k',
    comments: 1659,
    endsIn: '25 days',
    tags: ['Tech', 'Celebrities'],
    hot: true
  },
  {
    id: '3',
    title: 'Which company has best AI model end of 2025?',
    probability: 86,
    prediction: 'Google',
    volume: '$19m',
    volumeToday: '$880k',
    liquidity: '$2m',
    comments: 3468,
    endsIn: '26 days',
    tags: ['Tech', 'AI'],
    hot: true
  },
  {
    id: '4',
    title: '#1 Searched News on Google this year?',
    probability: 100,
    prediction: 'Charlie Kirk assassination',
    volume: '$805k',
    volumeToday: '$166k',
    liquidity: '$102k',
    comments: 16,
    endsIn: '25 days',
    tags: ['Tech', 'Culture']
  },
  {
    id: '5',
    title: 'Gemini 3.0 Flash released by...?',
    probability: 93,
    prediction: 'December 31',
    volume: '$2m',
    volumeToday: '$137k',
    liquidity: '$128k',
    comments: 120,
    endsIn: '25 days',
    tags: ['Tech', 'AI']
  },
  {
    id: '6',
    title: 'Game of the Year 2025',
    probability: 93,
    prediction: 'Clair Obscur: Expedition 33',
    volume: '$39m',
    volumeToday: '$120k',
    liquidity: '$362k',
    comments: 175,
    endsIn: '5 days',
    tags: ['Tech', 'Video Games'],
    hot: true
  },
  {
    id: '7',
    title: '2nd Largest company end of 2025?',
    probability: 86,
    prediction: 'Apple',
    volume: '$661k',
    volumeToday: '$97k',
    liquidity: '$228k',
    comments: 70,
    endsIn: '25 days',
    tags: ['Tech', 'Business']
  },
  {
    id: '8',
    title: 'Which company has second best AI model end of December?',
    probability: 73,
    prediction: 'Google',
    volume: '$475k',
    volumeToday: '$63.8k',
    liquidity: '$72.9k',
    comments: 51,
    endsIn: '25 days',
    tags: ['Tech', 'AI']
  },
  {
    id: '9',
    title: 'Will DraftKings launch a prediction market in 2025?',
    probability: 69,
    prediction: 'Yes',
    volume: '$391k',
    volumeToday: '$58.3k',
    liquidity: '$10.1k',
    comments: 86,
    endsIn: '25 days',
    tags: ['Tech', 'Prediction Markets']
  },
  {
    id: '10',
    title: '#2 Free App in the US Apple App Store on December 5?',
    probability: 99,
    prediction: 'ChatGPT',
    volume: '$173k',
    volumeToday: null,
    liquidity: '$46.9k',
    comments: 17,
    endsIn: null,
    tags: ['Tech', 'Apple']
  },
  {
    id: '11',
    title: 'Will OpenAI release a new frontier model by December 13?',
    probability: 77,
    prediction: 'Yes',
    volume: '$48.5k',
    volumeToday: null,
    liquidity: '$14.4k',
    comments: 12,
    endsIn: '7 days',
    tags: ['Tech', 'AI'],
    hot: true
  },
  {
    id: '12',
    title: '3rd Largest company end of 2025?',
    probability: 86,
    prediction: 'Alphabet',
    volume: '$180k',
    volumeToday: null,
    liquidity: '$52.8k',
    comments: 1,
    endsIn: '25 days',
    tags: ['Tech', 'Business']
  },
  {
    id: '13',
    title: 'Which company has top AI model end of December? (Style Control On)',
    probability: 85,
    prediction: 'Google',
    volume: '$2m',
    volumeToday: null,
    liquidity: '$121k',
    comments: 19,
    endsIn: '25 days',
    tags: ['Tech', 'AI']
  },
  {
    id: '14',
    title: 'Next CEO of X?',
    probability: 96,
    prediction: 'No CEO announced in 2025',
    volume: '$2m',
    volumeToday: null,
    liquidity: '$151k',
    comments: 21,
    endsIn: '25 days',
    tags: ['Tech', 'Finance']
  },
  {
    id: '15',
    title: 'Which company will have the best AI model for coding at the end of 2025?',
    probability: 85,
    prediction: 'Anthropic',
    volume: '$3m',
    volumeToday: null,
    liquidity: '$118k',
    comments: 56,
    endsIn: '25 days',
    tags: ['Tech', 'AI']
  },
  {
    id: '16',
    title: 'Google Gemini 3 score on Humanity\'s Last Exam by January 31?',
    probability: 45,
    prediction: '40%+',
    volume: '$507k',
    volumeToday: null,
    liquidity: '$7.4k',
    comments: 72,
    endsIn: '~2 months',
    tags: ['Tech', 'Business']
  },
  {
    id: '17',
    title: 'OpenAI IPO by...?',
    probability: 33,
    prediction: 'December 31, 2026',
    volume: '$630k',
    volumeToday: null,
    liquidity: '$93.8k',
    comments: 5,
    endsIn: '~1 year',
    tags: ['Tech', 'Business']
  },
  {
    id: '18',
    title: 'IPOs in 2025?',
    probability: 98,
    prediction: 'Wealthfront',
    volume: '$591k',
    volumeToday: null,
    liquidity: '$211k',
    comments: 0,
    endsIn: '25 days',
    tags: ['Tech', 'Business']
  }
]

const SUBCATEGORIES = ['All', 'AI', 'Business', 'Apple', 'Video Games', 'Prediction Markets', 'Finance', 'Culture']

function formatNumber(num) {
  if (typeof num === 'string') return num
  if (num >= 1000000) return `$${(num / 1000000).toFixed(1)}m`
  if (num >= 1000) return `$${(num / 1000).toFixed(1)}k`
  return `$${num}`
}

function getProbabilityClass(prob) {
  if (prob < 30) return 'low'
  if (prob < 70) return 'medium'
  return ''
}

function getTagClass(tag) {
  if (tag.toLowerCase() === 'ai') return 'ai'
  if (tag.toLowerCase() === 'business' || tag.toLowerCase() === 'finance') return 'business'
  return ''
}

export default function Dashboard() {
  const [markets, setMarkets] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('All')
  const [lastUpdate, setLastUpdate] = useState(null)
  const [refreshing, setRefreshing] = useState(false)
  const [sortBy, setSortBy] = useState('volume')

  const fetchMarkets = useCallback(async () => {
    setRefreshing(true)
    
    // Simulate API fetch delay
    await new Promise(resolve => setTimeout(resolve, 800))
    
    setMarkets(TECH_MARKETS_DATA)
    setLastUpdate(new Date())
    setLoading(false)
    setRefreshing(false)
  }, [])

  useEffect(() => {
    fetchMarkets()
    
    // Auto refresh every 30 seconds
    const interval = setInterval(fetchMarkets, 30000)
    return () => clearInterval(interval)
  }, [fetchMarkets])

  const filteredMarkets = markets.filter(market => {
    if (filter === 'All') return true
    return market.tags.some(tag => tag.toLowerCase() === filter.toLowerCase())
  })

  const sortedMarkets = [...filteredMarkets].sort((a, b) => {
    if (sortBy === 'volume') {
      const aVol = parseFloat(a.volume.replace(/[$,mk]/gi, '')) * (a.volume.includes('m') ? 1000000 : a.volume.includes('k') ? 1000 : 1)
      const bVol = parseFloat(b.volume.replace(/[$,mk]/gi, '')) * (b.volume.includes('m') ? 1000000 : b.volume.includes('k') ? 1000 : 1)
      return bVol - aVol
    }
    if (sortBy === 'probability') {
      return b.probability - a.probability
    }
    if (sortBy === 'ending') {
      const getEndingDays = (str) => {
        if (!str) return 9999
        const match = str.match(/(\d+)/)
        return match ? parseInt(match[1]) : 9999
      }
      return getEndingDays(a.endsIn) - getEndingDays(b.endsIn)
    }
    return 0
  })

  const totalVolume = markets.reduce((sum, m) => {
    const vol = parseFloat(m.volume.replace(/[$,mk]/gi, '')) * (m.volume.includes('m') ? 1000000 : m.volume.includes('k') ? 1000 : 1)
    return sum + vol
  }, 0)

  const activeMarkets = markets.length

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading">
          <div className="loading-spinner"></div>
          <div className="loading-text">Loading Tech Markets...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="dashboard">
      <header className="header">
        <div className="logo">
          <div className="logo-icon">PM</div>
          <div className="logo-text">
            <h1>POLYMARKET INSIDER</h1>
            <p>Tech Prediction Markets Dashboard</p>
          </div>
        </div>
        <div className="header-stats">
          <div className="stat-box">
            <div className="stat-label">Total Volume</div>
            <div className="stat-value">{formatNumber(totalVolume)}</div>
          </div>
          <div className="stat-box">
            <div className="stat-label">Active Markets</div>
            <div className="stat-value blue">{activeMarkets}</div>
          </div>
        </div>
      </header>

      <div className="filters">
        {SUBCATEGORIES.map(cat => (
          <button
            key={cat}
            className={`filter-btn ${filter === cat ? 'active' : ''}`}
            onClick={() => setFilter(cat)}
          >
            {cat}
          </button>
        ))}
        <select 
          className="filter-btn" 
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          style={{ marginLeft: 'auto' }}
        >
          <option value="volume">Sort: Volume</option>
          <option value="probability">Sort: Probability</option>
          <option value="ending">Sort: Ending Soon</option>
        </select>
      </div>

      <div className="markets-grid">
        {sortedMarkets.map(market => (
          <div 
            key={market.id} 
            className="market-card"
            onClick={() => window.open(`https://polymarket.com/event/${market.title.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`, '_blank')}
          >
            {market.hot && <span className="hot-badge">🔥 HOT</span>}
            
            <div className="market-header">
              <div className="market-tags">
                {market.tags.map(tag => (
                  <span key={tag} className={`tag ${getTagClass(tag)}`}>{tag}</span>
                ))}
              </div>
              {market.endsIn && (
                <div className="market-time">{market.endsIn}</div>
              )}
            </div>

            <h3 className="market-title">{market.title}</h3>

            <div className="market-prediction">
              <span className={`probability ${getProbabilityClass(market.probability)}`}>
                {market.probability}%
              </span>
              <span className="prediction-label">{market.prediction}</span>
            </div>

            <div className="progress-bar">
              <div 
                className={`progress-fill ${getProbabilityClass(market.probability)}`}
                style={{ width: `${market.probability}%` }}
              />
            </div>

            <div className="market-stats">
              <div className="market-stat">
                <div className="market-stat-label">Volume</div>
                <div className="market-stat-value">{market.volume}</div>
                {market.volumeToday && (
                  <div className="volume-indicator">
                    <span className="volume-change">+{market.volumeToday} today</span>
                  </div>
                )}
              </div>
              <div className="market-stat">
                <div className="market-stat-label">Liquidity</div>
                <div className="market-stat-value">{market.liquidity}</div>
              </div>
              <div className="market-stat">
                <div className="market-stat-label">Comments</div>
                <div className="market-stat-value">{market.comments.toLocaleString()}</div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {sortedMarkets.length === 0 && (
        <div className="empty-state">
          <h3>No markets found</h3>
          <p>Try changing your filter settings</p>
        </div>
      )}

      <button 
        className={`refresh-btn ${refreshing ? 'spinning' : ''}`}
        onClick={fetchMarkets}
        disabled={refreshing}
      >
        🔄
      </button>

      {lastUpdate && (
        <div className="last-update">
          Last update: {lastUpdate.toLocaleTimeString()}
        </div>
      )}
    </div>
  )
}
