import { TileLayer } from 'react-leaflet'

const NESHAN_MAP_KEY = import.meta.env.VITE_NESHAN_MAP_KEY as string | undefined

interface TrafficLayerProps {
  visible: boolean
}

/**
 * لایه ترافیک زنده نشان — روی تایل پایه نقشه قرار می‌گیرد.
 * از سرویس تایل ترافیک نشان استفاده می‌کند (نیازمند Map Key).
 */
export function TrafficLayer({ visible }: TrafficLayerProps) {
  if (!visible) return null

  const hasKey = NESHAN_MAP_KEY && !NESHAN_MAP_KEY.includes('your_neshan')

  if (!hasKey) {
    // بدون کلید معتبر، لایه ترافیک قابل بارگذاری نیست.
    return null
  }

  return (
    <TileLayer
      url={`https://api.neshan.org/v1/traffic/tiles/{z}/{x}/{y}.png?key=${NESHAN_MAP_KEY}`}
      opacity={0.65}
      zIndex={450}
    />
  )
}
