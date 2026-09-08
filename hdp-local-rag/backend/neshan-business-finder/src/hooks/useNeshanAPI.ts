import { useCallback, useState } from 'react'
import type { Business, LatLng } from '../types'
import { businesses as fallbackBusinesses } from '../data/businesses'

const NESHAN_API_KEY = import.meta.env.VITE_NESHAN_API_KEY as string | undefined
const NESHAN_BASE_URL = 'https://api.neshan.org'

interface NeshanSearchItem {
  location: { x: number; y: number } // x=lng, y=lat
  title: string
  address: string
  category?: string
  region?: string
}

interface NeshanSearchResponse {
  count: number
  items: NeshanSearchItem[]
}

interface UseNeshanAPIResult {
  loading: boolean
  error: string | null
  results: Business[]
  searchNearby: (query: string, center: LatLng) => Promise<void>
  reverseGeocode: (point: LatLng) => Promise<string | null>
}

/**
 * هوک اتصال به API نشان (Search + Reverse Geocoding).
 * در صورت نبود کلید API یا خطای شبکه، به داده نمونه (fallback) سوییچ می‌کند
 * تا محیط توسعه بدون نیاز فوری به کلید هم قابل استفاده باشد.
 */
export function useNeshanAPI(): UseNeshanAPIResult {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [results, setResults] = useState<Business[]>(fallbackBusinesses)

  const searchNearby = useCallback(async (query: string, center: LatLng) => {
    setLoading(true)
    setError(null)

    if (!NESHAN_API_KEY || NESHAN_API_KEY.includes('your_neshan')) {
      // بدون کلید معتبر: فیلتر روی داده محلی به‌عنوان fallback
      const filtered = query.trim()
        ? fallbackBusinesses.filter((b) =>
            (b.name + b.address).toLowerCase().includes(query.toLowerCase())
          )
        : fallbackBusinesses
      setResults(filtered)
      setLoading(false)
      setError('کلید API نشان تنظیم نشده — نتایج نمونه نمایش داده می‌شود.')
      return
    }

    try {
      const url = `${NESHAN_BASE_URL}/v1/search?term=${encodeURIComponent(
        query
      )}&lat=${center.lat}&lng=${center.lng}`

      const res = await fetch(url, {
        headers: { 'Api-Key': NESHAN_API_KEY },
      })

      if (!res.ok) throw new Error(`خطای سرویس نشان: ${res.status}`)

      const data: NeshanSearchResponse = await res.json()

      const mapped: Business[] = data.items.map((item, idx) => ({
        id: `neshan-${idx}-${item.location.x}-${item.location.y}`,
        name: item.title,
        address: item.address,
        category: 'other',
        location: { lat: item.location.y, lng: item.location.x },
      }))

      setResults(mapped)
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'خطا در دریافت اطلاعات از نشان'
      )
      setResults(fallbackBusinesses)
    } finally {
      setLoading(false)
    }
  }, [])

  const reverseGeocode = useCallback(
    async (point: LatLng): Promise<string | null> => {
      if (!NESHAN_API_KEY || NESHAN_API_KEY.includes('your_neshan')) {
        return null
      }
      try {
        const url = `${NESHAN_BASE_URL}/v5/reverse?lat=${point.lat}&lng=${point.lng}`
        const res = await fetch(url, {
          headers: { 'Api-Key': NESHAN_API_KEY },
        })
        if (!res.ok) return null
        const data = await res.json()
        return data.formatted_address ?? null
      } catch {
        return null
      }
    },
    []
  )

  return { loading, error, results, searchNearby, reverseGeocode }
}
