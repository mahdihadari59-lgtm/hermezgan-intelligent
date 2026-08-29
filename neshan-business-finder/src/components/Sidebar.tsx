import { useMemo, useState } from 'react'
import type { Business, BusinessCategory } from '../types'
import { CATEGORY_META } from '../types'
import { BusinessCard } from './BusinessCard'

interface SidebarProps {
  businesses: Business[]
  selectedId: string | null
  onSelect: (business: Business) => void
  onRoute: (business: Business) => void
  onSearch: (query: string) => void
}

const CATEGORIES = Object.values(CATEGORY_META)

export function Sidebar({
  businesses,
  selectedId,
  onSelect,
  onRoute,
  onSearch,
}: SidebarProps) {
  const [query, setQuery] = useState('')
  const [activeCategory, setActiveCategory] = useState<BusinessCategory | 'all'>(
    'all'
  )

  const filtered = useMemo(() => {
    let list = businesses
    if (activeCategory !== 'all') {
      list = list.filter((b) => b.category === activeCategory)
    }
    return list
  }, [businesses, activeCategory])

  function handleSearchChange(value: string) {
    setQuery(value)
    onSearch(value)
  }

  return (
    <aside className="sidebar">
      <header className="app-header">
        <div className="logo-mark">ی</div>
        <div>
          <h1>یاب</h1>
          <p>کسب‌وکارهای اطراف شما</p>
        </div>
      </header>

      <div className="search-box">
        <div className="search-input-wrap">
          <input
            type="text"
            placeholder="جست‌وجوی رستوران، داروخانه، کافه..."
            value={query}
            onChange={(e) => handleSearchChange(e.target.value)}
          />
          <span className="search-icon">🔍</span>
        </div>
      </div>

      <div className="category-filters">
        <button
          className={`category-chip ${activeCategory === 'all' ? 'active' : ''}`}
          onClick={() => setActiveCategory('all')}
        >
          همه
        </button>
        {CATEGORIES.map((cat) => (
          <button
            key={cat.key}
            className={`category-chip ${activeCategory === cat.key ? 'active' : ''}`}
            onClick={() => setActiveCategory(cat.key)}
          >
            {cat.icon} {cat.label}
          </button>
        ))}
      </div>

      <div className="business-list">
        <div className="list-meta">
          <strong>{filtered.length}</strong> کسب‌وکار یافت شد
        </div>

        {filtered.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🔎</div>
            نتیجه‌ای یافت نشد.
            <br />
            فیلتر دیگری را امتحان کنید.
          </div>
        ) : (
          filtered.map((b) => (
            <BusinessCard
              key={b.id}
              business={b}
              selected={b.id === selectedId}
              onSelect={onSelect}
              onRoute={onRoute}
            />
          ))
        )}
      </div>
    </aside>
  )
}
