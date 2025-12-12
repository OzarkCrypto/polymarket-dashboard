'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'
import { RefreshCw, ExternalLink, Users, TrendingUp, ChevronDown, ChevronUp } from 'lucide-react'

interface Market {
  id: string
  conditionId: string
  question: string
  description: string
  slug: string
  outcomes: string[]
  closed: boolean
  endDate?: string
  liquidity?: number
  volume?: number
  link: string
}

interface Holder {
  proxyWallet: string
  address: string
  pseudonym: string
  name: string
  amount: number
  outcomeIndex: number
  profileImage?: string
  bio?: string
}

interface MarketWithHolders extends Market {
  yesHolders: Holder[]
  noHolders: Holder[]
  loadingHolders: boolean
}

export default function Home() {
  const [markets, setMarkets] = useState<MarketWithHolders[]>([])
  const [loading, setLoading] = useState(false)
  const [expandedMarkets, setExpandedMarkets] = useState<Set<string>>(new Set())

  const fetchMarkets = async () => {
    setLoading(true)
    try {
      const response = await axios.get('/api/tech-markets')
      if (response.data.success && response.data.markets) {
        const marketsWithHolders: MarketWithHolders[] = response.data.markets.map((market: Market) => ({
          ...market,
          yesHolders: [],
          noHolders: [],
          loadingHolders: false,
        }))
        setMarkets(marketsWithHolders)
      } else {
        alert('데이터 수집에 실패했습니다: ' + (response.data.error || 'Unknown error'))
      }
    } catch (error: any) {
      console.error('Error fetching markets:', error)
      alert('데이터를 가져오는 중 오류가 발생했습니다: ' + (error.message || 'Unknown error'))
    } finally {
      setLoading(false)
    }
  }

  const fetchHolders = async (market: MarketWithHolders) => {
    if (market.loadingHolders || (market.yesHolders.length > 0 && market.noHolders.length > 0)) {
      return
    }

    // 로딩 상태 설정
    setMarkets(prev => prev.map(m => 
      m.id === market.id ? { ...m, loadingHolders: true } : m
    ))

    try {
      // Yes 홀더 가져오기 (outcomeIndex: 0)
      const yesResponse = await axios.get(`/api/market-holders?conditionId=${market.conditionId}&outcomeIndex=0&limit=10`)
      const yesHolders = yesResponse.data.success ? yesResponse.data.holders : []

      // No 홀더 가져오기 (outcomeIndex: 1)
      const noResponse = await axios.get(`/api/market-holders?conditionId=${market.conditionId}&outcomeIndex=1&limit=10`)
      const noHolders = noResponse.data.success ? noResponse.data.holders : []

      // 상태 업데이트
      setMarkets(prev => prev.map(m => 
        m.id === market.id 
          ? { ...m, yesHolders, noHolders, loadingHolders: false }
          : m
      ))
    } catch (error: any) {
      console.error('Error fetching holders:', error)
      setMarkets(prev => prev.map(m => 
        m.id === market.id ? { ...m, loadingHolders: false } : m
      ))
    }
  }

  const toggleMarket = (marketId: string) => {
    const newExpanded = new Set(expandedMarkets)
    if (newExpanded.has(marketId)) {
      newExpanded.delete(marketId)
    } else {
      newExpanded.add(marketId)
      // 확장할 때 홀더 정보 가져오기
      const market = markets.find(m => m.id === marketId)
      if (market) {
        fetchHolders(market)
      }
    }
    setExpandedMarkets(newExpanded)
  }

  useEffect(() => {
    fetchMarkets()
  }, [])

  const formatAddress = (address: string) => {
    if (!address) return 'N/A'
    return `${address.slice(0, 6)}...${address.slice(-4)}`
  }

  const formatAmount = (amount: number) => {
    if (amount >= 1000000) {
      return `${(amount / 1000000).toFixed(2)}M`
    } else if (amount >= 1000) {
      return `${(amount / 1000).toFixed(2)}K`
    }
    return amount.toFixed(2)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            💻 Polymarket Tech 마켓 & 홀더 대시보드
          </h1>
          <p className="text-gray-600">
            Tech 카테고리의 액티브 마켓과 각 마켓의 Yes/No 탑10 홀더를 확인하세요.
          </p>
        </div>

        {/* Stats Card */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">총 액티브 마켓 수</p>
              <p className="text-3xl font-bold text-gray-900">{markets.length}</p>
            </div>
            <button
              onClick={fetchMarkets}
              disabled={loading}
              className="flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              {loading ? '로딩 중...' : '데이터 새로고침'}
            </button>
          </div>
        </div>

        {/* Markets List */}
        <div className="space-y-4">
          {markets.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-12 text-center">
              <p className="text-gray-500 text-lg">
                {loading ? '마켓 데이터를 불러오는 중...' : '마켓 데이터가 없습니다. 새로고침 버튼을 클릭하세요.'}
              </p>
            </div>
          ) : (
            markets.map((market) => {
              const isExpanded = expandedMarkets.has(market.id)
              
              return (
                <div
                  key={market.id}
                  className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow"
                >
                  {/* Market Header */}
                  <div
                    className="p-6 cursor-pointer"
                    onClick={() => toggleMarket(market.id)}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">
                          {market.question}
                        </h3>
                        {market.description && (
                          <p className="text-gray-600 text-sm mb-3">{market.description}</p>
                        )}
                        <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                          {market.volume && (
                            <span>💰 Volume: ${formatAmount(market.volume)}</span>
                          )}
                          {market.liquidity && (
                            <span>💧 Liquidity: ${formatAmount(market.liquidity)}</span>
                          )}
                          {market.endDate && (
                            <span>📅 Ends: {new Date(market.endDate).toLocaleDateString()}</span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {market.link && (
                          <a
                            href={market.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-2 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <ExternalLink className="w-5 h-5" />
                          </a>
                        )}
                        {isExpanded ? (
                          <ChevronUp className="w-6 h-6 text-gray-400" />
                        ) : (
                          <ChevronDown className="w-6 h-6 text-gray-400" />
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Holders Section */}
                  {isExpanded && (
                    <div className="border-t border-gray-200 p-6">
                      {market.loadingHolders ? (
                        <div className="text-center py-8">
                          <RefreshCw className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-2" />
                          <p className="text-gray-500">홀더 정보를 불러오는 중...</p>
                        </div>
                      ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          {/* Yes Holders */}
                          <div>
                            <div className="flex items-center gap-2 mb-4">
                              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                              <h4 className="text-lg font-semibold text-gray-900">Yes 탑10 홀더</h4>
                            </div>
                            {market.yesHolders.length === 0 ? (
                              <p className="text-gray-500 text-sm py-4">홀더 정보가 없습니다.</p>
                            ) : (
                              <div className="space-y-2">
                                {market.yesHolders.map((holder, idx) => (
                                  <div
                                    key={holder.address}
                                    className="flex items-center justify-between p-3 bg-green-50 rounded-lg hover:bg-green-100 transition-colors"
                                  >
                                    <div className="flex items-center gap-3 flex-1 min-w-0">
                                      <div className="flex-shrink-0 w-8 h-8 bg-green-200 rounded-full flex items-center justify-center text-xs font-bold text-green-800">
                                        {idx + 1}
                                      </div>
                                      <div className="flex-1 min-w-0">
                                        <p className="font-medium text-gray-900 truncate">
                                          {holder.pseudonym || holder.name || 'Anonymous'}
                                        </p>
                                        <p className="text-xs text-gray-500 truncate">
                                          {formatAddress(holder.address)}
                                        </p>
                                      </div>
                                    </div>
                                    <div className="flex-shrink-0 ml-4">
                                      <p className="text-sm font-semibold text-green-700">
                                        {formatAmount(holder.amount)}
                                      </p>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>

                          {/* No Holders */}
                          <div>
                            <div className="flex items-center gap-2 mb-4">
                              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                              <h4 className="text-lg font-semibold text-gray-900">No 탑10 홀더</h4>
                            </div>
                            {market.noHolders.length === 0 ? (
                              <p className="text-gray-500 text-sm py-4">홀더 정보가 없습니다.</p>
                            ) : (
                              <div className="space-y-2">
                                {market.noHolders.map((holder, idx) => (
                                  <div
                                    key={holder.address}
                                    className="flex items-center justify-between p-3 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
                                  >
                                    <div className="flex items-center gap-3 flex-1 min-w-0">
                                      <div className="flex-shrink-0 w-8 h-8 bg-red-200 rounded-full flex items-center justify-center text-xs font-bold text-red-800">
                                        {idx + 1}
                                      </div>
                                      <div className="flex-1 min-w-0">
                                        <p className="font-medium text-gray-900 truncate">
                                          {holder.pseudonym || holder.name || 'Anonymous'}
                                        </p>
                                        <p className="text-xs text-gray-500 truncate">
                                          {formatAddress(holder.address)}
                                        </p>
                                      </div>
                                    </div>
                                    <div className="flex-shrink-0 ml-4">
                                      <p className="text-sm font-semibold text-red-700">
                                        {formatAmount(holder.amount)}
                                      </p>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })
          )}
        </div>
      </div>
    </div>
  )
}
