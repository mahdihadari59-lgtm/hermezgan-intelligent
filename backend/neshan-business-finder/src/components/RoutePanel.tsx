import type { Business, RouteInfo, RouteTravelMode } from '../types'

interface RoutePanelProps {
  business: Business
  route: RouteInfo | null
  loading: boolean
  warning: string | null
  mode: RouteTravelMode
  onModeChange: (mode: RouteTravelMode) => void
  onClose: () => void
}

function formatDistance(meters: number): string {
  if (meters < 1000) return `${Math.round(meters)} متر`
  return `${(meters / 1000).toFixed(1)} کیلومتر`
}

function formatDuration(seconds: number): string {
  const minutes = Math.round(seconds / 60)
  if (minutes < 60) return `${minutes} دقیقه`
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return `${h} ساعت${m ? ` و ${m} دقیقه` : ''}`
}

export function RoutePanel({
  business,
  route,
  loading,
  warning,
  mode,
  onModeChange,
  onClose,
}: RoutePanelProps) {
  return (
    <div className="route-panel">
      <div className="route-panel-header">
        <span className="route-panel-title">🧭 مسیر تا {business.name}</span>
        <button className="route-close" onClick={onClose}>
          ✕
        </button>
      </div>

      {loading && <div className="route-warning">در حال محاسبه مسیر...</div>}

      {!loading && route && (
        <>
          <div className="route-stats">
            <div className="route-stat">
              <div className="value">{formatDistance(route.distanceMeters)}</div>
              <div className="label">فاصله</div>
            </div>
            <div className="route-stat">
              <div className="value">
                {formatDuration(
                  route.durationInTrafficSeconds ?? route.durationSeconds
                )}
              </div>
              <div className="label">
                {route.durationInTrafficSeconds ? 'زمان با ترافیک' : 'زمان تخمینی'}
              </div>
            </div>
          </div>

          <div className="route-mode-toggle">
            <button
              className={`mode-btn ${mode === 'car' ? 'active' : ''}`}
              onClick={() => onModeChange('car')}
            >
              🚗 خودرو
            </button>
            <button
              className={`mode-btn ${mode === 'motorcycle' ? 'active' : ''}`}
              onClick={() => onModeChange('motorcycle')}
            >
              🏍️ موتور
            </button>
          </div>
        </>
      )}

      {warning && <div className="route-warning">{warning}</div>}
    </div>
  )
}
