/**
 * Rate Limiter for Polymarket API
 * Based on official rate limits: https://docs.polymarket.com/quickstart/introduction/rate-limits
 */

interface RateLimitConfig {
  maxRequests: number
  windowMs: number
  name: string
}

// Rate limit configurations from official docs
export const RATE_LIMITS = {
  GAMMA_GENERAL: {
    maxRequests: 750,
    windowMs: 10000, // 10 seconds
    name: 'GAMMA General',
  },
  GAMMA_MARKETS: {
    maxRequests: 125,
    windowMs: 10000,
    name: 'GAMMA /markets',
  },
  GAMMA_TAGS: {
    maxRequests: 100,
    windowMs: 10000,
    name: 'GAMMA Tags',
  },
  DATA_API_GENERAL: {
    maxRequests: 200,
    windowMs: 10000,
    name: 'Data API General',
  },
} as const

/**
 * Calculate minimum delay between requests to stay under rate limit
 */
export function getMinDelay(config: RateLimitConfig): number {
  // Add 10% buffer for safety
  return Math.ceil((config.windowMs / config.maxRequests) * 1.1)
}

/**
 * Get recommended cache duration based on rate limits and data volatility
 */
export function getRecommendedCacheTTL(endpoint: string): number {
  switch (endpoint) {
    case 'tags':
      // Tags rarely change, cache for 1 hour
      return 3600
    case 'markets':
      // Markets change frequently but not real-time critical, cache for 5 minutes
      return 300
    case 'holders':
      // Holders change more frequently, cache for 1 minute
      return 60
    default:
      return 300 // Default 5 minutes
  }
}

/**
 * Check if we're approaching rate limit (80% threshold)
 */
export function isNearRateLimit(
  requestCount: number,
  config: RateLimitConfig
): boolean {
  return requestCount >= config.maxRequests * 0.8
}
