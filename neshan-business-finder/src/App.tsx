import { useCallback, useEffect, useMemo, useState } from 'react'
import { Sidebar } from './components/Sidebar'
import { Map } from './components/Map'
import { RoutePanel } from './components/RoutePanel'
import { ToastStack } from './components/Toast'
import { useGeolocation } from './hooks/useGeolocation'
import { useNeshanAPI } from './hooks/useNeshanAPI'
import { useRoute } from './hooks/useRoute'
import type { Business, RouteTravelMode, ToastMessage } from './types'

function haversineDistance(
  a: { lat: number; lng: number },
  b: { lat: number; lng: number }
): number {
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

export default function App() {
  const { position: userLocation, error: geoError, refresh: refreshLocation } =
    useGeolocation()

  const { results, searchNearby, error: apiError } = useNeshanAPI()
  const { route, loading: routeLoading, error: routeError, calculateRoute, clearRoute } =
    useRoute()

  const [selectedBusiness, setSelectedBusiness] = useState<Business | null>(null)
  const [routeTarget, setRouteTarget] = useState<Business | null>(null)
  const [travelMode, setTravelMode] = useState<RouteTravelMode>('car')
  const [showTraffic, setShowTraffic] = useState(false)
  const [toasts, setToasts] = useState<ToastMessage[]>([])

  const pushToast = useCallback((toast: Omit<ToastMessage, 'id'>) => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2)}`
    setToasts((prev) => [...prev, { ...toast, id }])
  }, [])

  const dismissToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  // اعلان خطای موقعیت مکانی
  useEffect(() => {
    if (geoError) {
      pushToast({ type: 'warning', text: geoError })
    }
  }, [geoError, pushToast])

  // اعلان خطای API نشان (کلید نامعتبر و ...)
  useEffect(() => {
    if (apiError) {
      pushToast({ type: 'info', text: apiError })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    if (routeError) {
      pushToast({ type: 'info', text: routeError })
    }
  }, [routeError, pushToast])

  // محاسبه فاصله هر کسب‌وکار نسبت به موقعیت کاربر
  const businessesWithDistance = useMemo(() => {
    if (!userLocation) return results
    return results
      .map((b) => ({
        ...b,
        distanceMeters: haversineDistance(userLocation, b.location),
      }))
      .sort((a, b) => (a.distanceMeters ?? 0) - (b.distanceMeters ?? 0))
  }, [results, userLocation])

  const handleSelect = useCallback((business: Business) => {
    setSelectedBusiness(business)
  }, [])

  const handleRouteRequest = useCallback(
    (business: Business) => {
      if (!userLocation) {
        pushToast({
          type: 'warning',
          text: 'برای نمایش مسیر، ابتدا موقعیت مکانی خود را فعال کنید.',
        })
        return
      }
      setSelectedBusiness(business)
      setRouteTarget(business)
      calculateRoute(userLocation, business.location, travelMode)
    },
    [userLocation, travelMode, calculateRoute, pushToast]
  )

  const handleModeChange = useCallback(
    (mode: RouteTravelMode) => {
      setTravelMode(mode)
      if (userLocation && routeTarget) {
        calculateRoute(userLocation, routeTarget.location, mode)
      }
    },
    [userLocation, routeTarget, calculateRoute]
  )

  const handleCloseRoute = useCallback(() => {
    setRouteTarget(null)
    clearRoute()
  }, [clearRoute])

  const handleLocateMe = useCallback(() => {
    refreshLocation()
    pushToast({ type: 'success', text: 'در حال به‌روزرسانی موقعیت مکانی...' })
  }, [refreshLocation, pushToast])

  const handleSearch = useCallback(
    (query: string) => {
      const center = userLocation ?? { lat: 35.7595, lng: 51.411 }
      searchNearby(query, center)
    },
    [userLocation, searchNearby]
  )

  return (
    <div className="app-shell">
      <Sidebar
        businesses={businessesWithDistance}
        selectedId={selectedBusiness?.id ?? null}
        onSelect={handleSelect}
        onRoute={handleRouteRequest}
        onSearch={handleSearch}
      />

      <Map
        businesses={businessesWithDistance}
        selectedBusiness={selectedBusiness}
        userLocation={userLocation}
        route={route}
        showTraffic={showTraffic}
        onToggleTraffic={() => setShowTraffic((v) => !v)}
        onMarkerClick={handleSelect}
        onLocateMe={handleLocateMe}
      />

      {routeTarget && (
        <RoutePanel
          business={routeTarget}
          route={route}
          loading={routeLoading}
          warning={routeError}
          mode={travelMode}
          onModeChange={handleModeChange}
          onClose={handleCloseRoute}
        />
      )}

      <ToastStack toasts={toasts} onDismiss={dismissToast} />
    </div>
  )
}
