import type { Business } from '../types'
import { CATEGORY_META } from '../types'

interface BusinessCardProps {
  business: Business
  selected: boolean
  onSelect: (business: Business) => void
  onRoute: (business: Business) => void
}

function formatDistance(meters?: number): string {
  if (meters === undefined) return ''
  if (meters < 1000) return `${Math.round(meters)} متر`
  return `${(meters / 1000).toFixed(1)} کیلومتر`
}

export function BusinessCard({
  business,
  selected,
  onSelect,
  onRoute,
}: BusinessCardProps) {
  const meta = CATEGORY_META[business.category]

  return (
    <div
      className={`business-card ${selected ? 'selected' : ''}`}
      onClick={() => onSelect(business)}
    >
      <div className="business-card-top">
        <div
          className="business-icon"
          style={{ background: `${meta.color}22`, color: meta.color }}
        >
          {meta.icon}
        </div>
        <div className="business-info">
          <p className="business-name">{business.name}</p>
          <p className="business-address">{business.address}</p>

          <div className="business-meta-row">
            {business.rating !== undefined && (
              <span className="rating-badge">
                ★ {business.rating.toFixed(1)}
                {business.reviewsCount ? ` (${business.reviewsCount})` : ''}
              </span>
            )}

            {business.openNow !== undefined && (
              <span
                className={`status-badge ${business.openNow ? 'open' : 'closed'}`}
              >
                <span className="status-dot" />
                {business.openNow ? 'باز' : 'بسته'}
              </span>
            )}

            {business.distanceMeters !== undefined && (
              <span className="distance-badge">
                {formatDistance(business.distanceMeters)}
              </span>
            )}
          </div>

          {business.tags && business.tags.length > 0 && (
            <div className="business-tags">
              {business.tags.map((tag) => (
                <span className="tag-pill" key={tag}>
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      <button
        className="route-btn"
        onClick={(e) => {
          e.stopPropagation()
          onRoute(business)
        }}
      >
        🧭 نمایش مسیر
      </button>
    </div>
  )
}
