'use client'

import { useState, useEffect } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { RefreshCw, ExternalLink, TrendingUp, Building2, Filter } from 'lucide-react'

interface Market {
  title: string
  description: string
  link: string
  matched_companies: string
  has_insider_potential: boolean
  scraped_at: string
}

export default function Home() {
  const [markets, setMarkets] = useState<Market[]>([])
  const [loading, setLoading] = useState(false)
  const [filterInsiderOnly, setFilterInsiderOnly] = useState(false)
  const [selectedCompanies, setSelectedCompanies] = useState<string[]>([])
  const [sortBy, setSortBy] = useState<'title' | 'company' | 'insider'>('title')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc')

  const fetchMarkets = async () => {
    setLoading(true)
    try {
      const response = await axios.get('/api/scrape')
      if (response.data.success) {
        setMarkets(response.data.markets || [])
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

  useEffect(() => {
    fetchMarkets()
  }, [])

  // Get unique companies
  const companies = Array.from(
    new Set(
      markets.flatMap(m => m.matched_companies?.split(', ') || [])
    )
  ).filter(Boolean).sort()

  // Filter markets
  let filteredMarkets = [...markets]
  
  if (filterInsiderOnly) {
    filteredMarkets = filteredMarkets.filter(m => m.has_insider_potential)
  }
  
  if (selectedCompanies.length > 0) {
    filteredMarkets = filteredMarkets.filter(m =>
      selectedCompanies.some(company => 
        m.matched_companies?.toLowerCase().includes(company.toLowerCase())
      )
    )
  }

  // Sort markets
  filteredMarkets.sort((a, b) => {
    let aVal: any, bVal: any
    
    if (sortBy === 'title') {
      aVal = a.title
      bVal = b.title
    } else if (sortBy === 'company') {
      aVal = a.matched_companies
      bVal = b.matched_companies
    } else {
      aVal = a.has_insider_potential ? 1 : 0
      bVal = b.has_insider_potential ? 1 : 0
    }
    
    if (sortOrder === 'asc') {
      return aVal > bVal ? 1 : -1
    } else {
      return aVal < bVal ? 1 : -1
    }
  })

  // Company distribution
  const companyCounts: Record<string, number> = {}
  filteredMarkets.forEach(m => {
    const comps = m.matched_companies?.split(', ') || []
    comps.forEach(c => {
      companyCounts[c] = (companyCounts[c] || 0) + 1
    })
  })
  
  const chartData = Object.entries(companyCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 15)
    .map(([name, count]) => ({ name, count }))

  const COLORS = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981']

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            📊 Polymarket 기업 마켓 대시보드
          </h1>
          <p className="text-gray-600">
            내부 정보 우위가 있을 수 있는 기업 관련 마켓을 필터링하여 보여줍니다.
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">총 마켓 수</p>
                <p className="text-2xl font-bold text-gray-900">{filteredMarkets.length}</p>
              </div>
              <Building2 className="w-8 h-8 text-blue-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">정보 우위 가능성</p>
                <p className="text-2xl font-bold text-gray-900">
                  {filteredMarkets.filter(m => m.has_insider_potential).length}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">관련 기업 수</p>
                <p className="text-2xl font-bold text-gray-900">{companies.length}</p>
              </div>
              <Filter className="w-8 h-8 text-purple-500" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <button
              onClick={fetchMarkets}
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              {loading ? '수집 중...' : '데이터 새로고침'}
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">필터</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="flex items-center gap-2 mb-2">
                <input
                  type="checkbox"
                  checked={filterInsiderOnly}
                  onChange={(e) => setFilterInsiderOnly(e.target.checked)}
                  className="w-4 h-4"
                />
                <span>내부 정보 우위 가능성만 보기</span>
              </label>
            </div>
            
            <div>
              <label className="block mb-2 text-sm font-medium">기업 선택</label>
              <select
                multiple
                value={selectedCompanies}
                onChange={(e) => {
                  const values = Array.from(e.target.selectedOptions, option => option.value)
                  setSelectedCompanies(values)
                }}
                className="w-full border rounded-lg p-2 min-h-[100px]"
                size={5}
              >
                {companies.map(company => (
                  <option key={company} value={company}>{company}</option>
                ))}
              </select>
              {selectedCompanies.length > 0 && (
                <button
                  onClick={() => setSelectedCompanies([])}
                  className="mt-2 text-sm text-blue-600 hover:underline"
                >
                  선택 해제
                </button>
              )}
            </div>
            
            <div>
              <label className="block mb-2 text-sm font-medium">정렬 기준</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                className="w-full border rounded-lg p-2"
              >
                <option value="title">제목</option>
                <option value="company">기업</option>
                <option value="insider">정보 우위</option>
              </select>
            </div>
            
            <div>
              <label className="block mb-2 text-sm font-medium">정렬 순서</label>
              <select
                value={sortOrder}
                onChange={(e) => setSortOrder(e.target.value as any)}
                className="w-full border rounded-lg p-2"
              >
                <option value="asc">오름차순</option>
                <option value="desc">내림차순</option>
              </select>
            </div>
          </div>
        </div>

        {/* Charts */}
        {chartData.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">기업별 마켓 분포</h2>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">정보 우위 분포</h2>
              <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                  <Pie
                    data={[
                      { name: '정보 우위 가능', value: filteredMarkets.filter(m => m.has_insider_potential).length },
                      { name: '일반 마켓', value: filteredMarkets.filter(m => !m.has_insider_potential).length },
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={120}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {[0, 1].map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* Markets List */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">마켓 목록 ({filteredMarkets.length}개)</h2>
          
          {filteredMarkets.length === 0 ? (
            <p className="text-gray-500 text-center py-8">표시할 마켓이 없습니다.</p>
          ) : (
            <div className="space-y-4">
              {filteredMarkets.map((market, idx) => (
                <div
                  key={idx}
                  className="border rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        {market.title}
                      </h3>
                      {market.description && (
                        <p className="text-gray-600 text-sm mb-2">{market.description}</p>
                      )}
                      <div className="flex flex-wrap gap-2 mt-2">
                        <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                          {market.matched_companies}
                        </span>
                        {market.has_insider_potential && (
                          <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded font-semibold">
                            🎯 정보 우위
                          </span>
                        )}
                      </div>
                    </div>
                    {market.link && (
                      <a
                        href={market.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-blue-600 hover:text-blue-800"
                      >
                        <ExternalLink className="w-4 h-4" />
                        <span className="text-sm">보기</span>
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

