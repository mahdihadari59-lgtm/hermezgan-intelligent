// ============================================
// تایپ‌های مرکزی اپلیکیشن یاب
// ============================================

export type BusinessCategory =
  | 'restaurant'
  | 'cafe'
  | 'pharmacy'
  | 'supermarket'
  | 'hospital'
  | 'bank'
  | 'gas_station'
  | 'bakery'
  | 'gym'
  | 'other'

export interface LatLng {
  lat: number
  lng: number
}

export interface Business {
  id: string
  name: string
  category: BusinessCategory
  address: string
  location: LatLng
  phone?: string
  rating?: number // 0..5
  reviewsCount?: number
  openNow?: boolean
  openHours?: string
  distanceMeters?: number // نسبت به موقعیت کاربر، محاسبه‌شده در زمان اجرا
  imageUrl?: string
  tags?: string[]
}

export interface RouteStep {
  instruction: string
  distanceMeters: number
  durationSeconds: number
}

export interface RouteInfo {
  distanceMeters: number
  durationSeconds: number
  durationInTrafficSeconds?: number
  geometry: LatLng[] // نقاط مسیر برای رسم روی نقشه
  steps?: RouteStep[]
}

export type RouteTravelMode = 'car' | 'motorcycle'

export interface GeolocationState {
  position: LatLng | null
  accuracy: number | null
  loading: boolean
  error: string | null
  permissionDenied: boolean
}

export interface ToastMessage {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  text: string
  durationMs?: number
}

export interface CategoryMeta {
  key: BusinessCategory
  label: string
  icon: string
  color: string
}

export const CATEGORY_META: Record<BusinessCategory, CategoryMeta> = {
  restaurant: { key: 'restaurant', label: 'رستوران', icon: '🍽️', color: '#E8A33D' },
  cafe: { key: 'cafe', label: 'کافه', icon: '☕', color: '#8B5E3C' },
  pharmacy: { key: 'pharmacy', label: 'داروخانه', icon: '💊', color: '#D64545' },
  supermarket: { key: 'supermarket', label: 'سوپرمارکت', icon: '🛒', color: '#4C9A6A' },
  hospital: { key: 'hospital', label: 'بیمارستان', icon: '🏥', color: '#C0392B' },
  bank: { key: 'bank', label: 'بانک', icon: '🏦', color: '#2C5F6F' },
  gas_station: { key: 'gas_station', label: 'پمپ بنزین', icon: '⛽', color: '#4A6D7C' },
  bakery: { key: 'bakery', label: 'نانوایی', icon: '🍞', color: '#B5793A' },
  gym: { key: 'gym', label: 'باشگاه ورزشی', icon: '🏋️', color: '#5B4B8A' },
  other: { key: 'other', label: 'سایر', icon: '📍', color: '#6B7280' },
}
