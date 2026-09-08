import { useEffect } from 'react'
import type { ToastMessage } from '../types'

interface ToastProps {
  toasts: ToastMessage[]
  onDismiss: (id: string) => void
}

const ICONS: Record<ToastMessage['type'], string> = {
  success: '✓',
  error: '✕',
  warning: '⚠',
  info: 'ℹ',
}

export function ToastStack({ toasts, onDismiss }: ToastProps) {
  return (
    <div className="toast-stack">
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} onDismiss={onDismiss} />
      ))}
    </div>
  )
}

function ToastItem({
  toast,
  onDismiss,
}: {
  toast: ToastMessage
  onDismiss: (id: string) => void
}) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onDismiss(toast.id)
    }, toast.durationMs ?? 3500)
    return () => clearTimeout(timer)
  }, [toast, onDismiss])

  return (
    <div className={`toast ${toast.type}`} onClick={() => onDismiss(toast.id)}>
      <span>{ICONS[toast.type]}</span>
      <span>{toast.text}</span>
    </div>
  )
}
