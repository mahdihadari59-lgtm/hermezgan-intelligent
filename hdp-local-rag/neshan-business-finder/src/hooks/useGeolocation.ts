import { useCallback, useEffect, useRef, useState } from 'react'
import type { GeolocationState } from '../types'

interface UseGeolocationOptions {
  watch?: boolean
  enableHighAccuracy?: boolean
}

/**
 * هوک دریافت و رهگیری موقعیت جغرافیایی کاربر با Geolocation API مرورگر.
 * قابلیت watch (رهگیری زنده) برای مسیر‌یابی زنده فعال است.
 */
export function useGeolocation(options: UseGeolocationOptions = {}) {
  const { watch = false, enableHighAccuracy = true } = options

  const [state, setState] = useState<GeolocationState>({
    position: null,
    accuracy: null,
    loading: true,
    error: null,
    permissionDenied: false,
  })

  const watchIdRef = useRef<number | null>(null)

  const handleSuccess = useCallback((pos: GeolocationPosition) => {
    setState({
      position: { lat: pos.coords.latitude, lng: pos.coords.longitude },
      accuracy: pos.coords.accuracy,
      loading: false,
      error: null,
      permissionDenied: false,
    })
  }, [])

  const handleError = useCallback((err: GeolocationPositionError) => {
    setState((prev) => ({
      ...prev,
      loading: false,
      error:
        err.code === err.PERMISSION_DENIED
          ? 'دسترسی به موقعیت مکانی رد شد'
          : 'خطا در دریافت موقعیت مکانی',
      permissionDenied: err.code === err.PERMISSION_DENIED,
    }))
  }, [])

  const refresh = useCallback(() => {
    if (!navigator.geolocation) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: 'مرورگر شما از موقعیت‌یابی پشتیبانی نمی‌کند',
      }))
      return
    }
    setState((prev) => ({ ...prev, loading: true }))
    navigator.geolocation.getCurrentPosition(handleSuccess, handleError, {
      enableHighAccuracy,
      timeout: 10000,
      maximumAge: 5000,
    })
  }, [enableHighAccuracy, handleSuccess, handleError])

  useEffect(() => {
    if (!navigator.geolocation) {
      setState((prev) => ({
        ...prev,
        loading: false,
        error: 'مرورگر شما از موقعیت‌یابی پشتیبانی نمی‌کند',
      }))
      return
    }

    if (watch) {
      watchIdRef.current = navigator.geolocation.watchPosition(
        handleSuccess,
        handleError,
        { enableHighAccuracy, timeout: 10000, maximumAge: 5000 }
      )
    } else {
      navigator.geolocation.getCurrentPosition(handleSuccess, handleError, {
        enableHighAccuracy,
        timeout: 10000,
        maximumAge: 5000,
      })
    }

    return () => {
      if (watchIdRef.current !== null) {
        navigator.geolocation.clearWatch(watchIdRef.current)
      }
    }
  }, [watch, enableHighAccuracy, handleSuccess, handleError])

  return { ...state, refresh }
}
