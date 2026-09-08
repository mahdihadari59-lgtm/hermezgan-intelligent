import { useEffect, useRef } from 'react'
import {
  MapContainer,
  Marker,
  Polyline,
  Popup,
  TileLayer,
  useMap,
} from 'react-leaflet'
import L from 'leaflet'
import type { Business, LatLng, RouteInfo } from '../types'
import { CATEGORY_META } from '../types'
import { DEFAULT_CENTER, DEFAULT_ZOOM } from '../data/businesses'
import { TrafficLayer } from './TrafficLayer'

const NESHAN_MAP_KEY = import.meta.env.VITE_NESHAN_MAP_KEY as string | undefined

interface MapProps {
  businesses: Business[]
  selectedBusiness: Business | null
  userLocation: LatLng | null
  route: RouteInfo | null
  showTraffic: boolean
  onToggleTraffic: () => void
  onMarkerClick: (business: Business) => void
  onLocateMe: () => void
}

function businessDivIcon(business: Business) {
  const meta = CATEGORY_META[business.category]
  return L.divIcon({
    className: '',
    html: `<div class="business-marker" style="background:${meta.color}"><span>${meta.icon}</span></div>`,
    iconSize: [30, 30],
    iconAnchor: [15, 28],
    popupAnchor: [0, -28],
  })
}

const userDivIcon = L.divIcon({
  className: '',
  html: `<div class="user-location-marker"></div>`,
  iconSize: [18, 18],
  iconAnchor: [9, 9],
})

/** کامپوننت داخلی برای هم‌مرکز کردن نقشه با تغییر انتخاب یا مسیر */
function MapViewController({
  selectedBusiness,
  route,
  userLocation,
}: {
  selectedBusiness: Business | null
  route: RouteInfo | null
  userLocation: LatLng | null
}) {
  const map = useMap()

  useEffect(() => {
    if (route && route.geometry.length > 0) {
      const bounds = L.latLngBounds(
        route.geometry.map((p) => [p.lat, p.lng] as [number, number])
      )
      map.fitBounds(bounds, { padding: [60, 60] })
      return
    }
    if (selectedBusiness) {
      map.flyTo(
        [selectedBusiness.location.lat, selectedBusiness.location.lng],
        16,
        { duration: 0.6 }
      )
    }
  }, [selectedBusiness, route, map])

  useEffect(() => {
    if (userLocation && !selectedBusiness && !route) {
      map.flyTo([userLocation.lat, userLocation.lng], 14, { duration: 0.6 })
    }
    // فقط در بار اول دریافت موقعیت اجرا شود
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [Boolean(userLocation)])

  return null
}

export function Map({
  businesses,
  selectedBusiness,
  userLocation,
  route,
  showTraffic,
  onToggleTraffic,
  onMarkerClick,
  onLocateMe,
}: MapProps) {
  const hasMapKey = NESHAN_MAP_KEY && !NESHAN_MAP_KEY.includes('your_neshan')
  const initialCenter = useRef<[number, number]>([
    DEFAULT_CENTER.lat,
    DEFAULT_CENTER.lng,
  ])

  return (
    <div className="map-container">
      <MapContainer
        center={initialCenter.current}
        zoom={DEFAULT_ZOOM}
        zoomControl={false}
      >
        {hasMapKey ? (
          <TileLayer
            url={`https://api.neshan.org/v2/static/tile/{z}/{x}/{y}?key=${NESHAN_MAP_KEY}`}
            attribution='&copy; <a href="https://neshan.org">نشان</a>'
          />
        ) : (
          // fallback به تایل OpenStreetMap در نبود کلید نشان (فقط برای توسعه)
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; OpenStreetMap — بدون کلید نشان، تایل جایگزین نمایش داده می‌شود'
          />
        )}

        <TrafficLayer visible={showTraffic} />

        {businesses.map((b) => (
          <Marker
            key={b.id}
            position={[b.location.lat, b.location.lng]}
            icon={businessDivIcon(b)}
            eventHandlers={{ click: () => onMarkerClick(b) }}
          >
            <Popup>
              <strong>{b.name}</strong>
              <br />
              {b.address}
            </Popup>
          </Marker>
        ))}

        {userLocation && (
          <Marker
            position={[userLocation.lat, userLocation.lng]}
            icon={userDivIcon}
          >
            <Popup>موقعیت شما</Popup>
          </Marker>
        )}

        {route && route.geometry.length > 1 && (
          <Polyline
            positions={route.geometry.map((p) => [p.lat, p.lng])}
            pathOptions={{ color: '#E8A33D', weight: 5, opacity: 0.9 }}
          />
        )}

        <MapViewController
          selectedBusiness={selectedBusiness}
          route={route}
          userLocation={userLocation}
        />
      </MapContainer>

      <div className="map-floating-controls">
        <button className="map-fab" onClick={onLocateMe} title="موقعیت من">
          🎯
        </button>
      </div>

      <button
        className={`traffic-toggle ${showTraffic ? 'active' : ''}`}
        onClick={onToggleTraffic}
      >
        <span className="traffic-dot" />
        ترافیک زنده
        <span className={`switch ${showTraffic ? 'on' : ''}`} />
      </button>
    </div>
  )
}
