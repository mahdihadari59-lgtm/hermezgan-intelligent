import { useCallback, useState } from 'react'
import type { LatLng, RouteInfo, RouteTravelMode } from '../types'

const NESHAN_API_KEY = import.meta.env.VITE_NESHAN_API_KEY as string | undefined
const NESHAN_BASE_URL = 'https://api.neshan.org'

interface UseRouteResult {
  route: RouteInfo | null
  loading: boolean
  error: string | null
  calculateRoute: (
    origin: LatLng,
    destination: LatLng,
    mode?: RouteTravelMode
  ) => Promise<void>
  clearRoute: () => void
}

// فاصله مستقیم بین دو نقطه (فرمول هاورساین) — برای fallback بدون کلید API
function haversineDistance(a: LatLng, b: LatLng): number {
  const R = 6371000
  const toRad = (deg: number) => (deg * Math.PI) / 180
  const dLat = toRad(b.lat - a.lat)
  const dLng = toRad(b.lng - a.lng)
  const lat1 = toRad(a.lat)
  const lat2 = toRad(b.lat)

  const h =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLng / 2) ** 2
  return 2 * R * Math.asin(Math.sqrt(h))
}

/**
 * هوک محاسبه مسیر بین دو نقطه با استفاده از Neshan Direction API.
 * در نبود کلید API، یک خط مستقیم و تخمین زمانی ساده به‌عنوان fallback ارائه می‌شود.
 */
export function useRoute(): UseRouteResult {
  const [route, setRoute] = useState<RouteInfo | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const calculateRoute = useCallback(
    async (origin: LatLng, destination: LatLng, mode: RouteTravelMode = 'car') => {
      setLoading(true)
      setError(null)

      if (!NESHAN_API_KEY || NESHAN_API_KEY.includes('your_neshan')) {
        const distance = haversineDistance(origin, destination)
        const estimatedSpeedMS = mode === 'motorcycle' ? 11 : 9 // متر بر ثانیه، تخمین شهری
        setRoute({
          distanceMeters: Math.round(distance * 1.3), // ضریب پیچ‌وخم جاده
          durationSeconds: Math.round((distance * 1.3) / estimatedSpeedMS),
          geometry: [origin, destination],
        })
        setError('کلید API نشان تنظیم نشده — مسیر تخمینی (خط مستقیم) نمایش داده می‌شود.')
        setLoading(false)
        return
      }

      try {
        const url = `${NESHAN_BASE_URL}/v4/direction?type=${mode}&origin=${origin.lat},${origin.lng}&destination=${destination.lat},${destination.lng}`
        const res = await fetch(url, {
          headers: { 'Api-Key': NESHAN_API_KEY },
        })

        if (!res.ok) throw new Error(`خطای سرویس مسیریابی: ${res.status}`)

        const data = await res.json()
        const leg = data.routes?.[0]?.legs?.[0]

        if (!leg) throw new Error('مسیری یافت نشد')

        const geometry: LatLng[] = decodePolyline(
          data.routes[0].overview_polyline?.points ?? ''
        )

        setRoute({
          distanceMeters: leg.distance?.value ?? 0,
          durationSeconds: leg.duration?.value ?? 0,
          durationInTrafficSeconds: leg.duration_in_traffic?.value,
          geometry: geometry.length ? geometry : [origin, destination],
          steps: (leg.steps ?? []).map((s: { instruction?: string; distance?: { value: number }; duration?: { value: number } }) => ({
            instruction: s.instruction ?? '',
            distanceMeters: s.distance?.value ?? 0,
            durationSeconds: s.duration?.value ?? 0,
          })),
        })
      } catch (err) {
        setError(err instanceof Error ? err.message : 'خطا در محاسبه مسیر')
        const distance = haversineDistance(origin, destination)
        setRoute({
          distanceMeters: Math.round(distance * 1.3),
          durationSeconds: Math.round((distance * 1.3) / 9),
          geometry: [origin, destination],
        })
      } finally {
        setLoading(false)
      }
    },
    []
  )

  const clearRoute = useCallback(() => setRoute(null), [])

  return { route, loading, error, calculateRoute, clearRoute }
}

// دی‌کد استاندارد Google Polyline Algorithm (نشان از همین فرمت استفاده می‌کند)
function decodePolyline(encoded: string): LatLng[] {
  if (!encoded) return []
  const points: LatLng[] = []
  let index = 0
  let lat = 0
  let lng = 0

  while (index < encoded.length) {
    let b: number
    let shift = 0
    let result = 0
    do {
      b = encoded.charCodeAt(index++) - 63
      result |= (b & 0x1f) << shift
      shift += 5
    } while (b >= 0x20)
    const dlat = result & 1 ? ~(result >> 1) : result >> 1
    lat += dlat

    shift = 0
    result = 0
    do {
      b = encoded.charCodeAt(index++) - 63
      result |= (b & 0x1f) << shift
      shift += 5
    } while (b >= 0x20)
    const dlng = result & 1 ? ~(result >> 1) : result >> 1
    lng += dlng

    points.push({ lat: lat / 1e5, lng: lng / 1e5 })
  }

  return points
}
