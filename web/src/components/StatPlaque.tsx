import type { ReactNode } from 'react'
import './stat-plaque.css'

export type StatName = 'speed' | 'endurance' | 'hills' | 'consistency'

const GLYPHS: Record<StatName, ReactNode> = {
  // Wing: three swept feathers
  speed: <path d="M4 18 C10 18 17 14 22 6 M4 18 C9 16 14 15 19 11 M4 18 C8 17 11 17 15 15" />,
  // Flask: the alchemist's vessel
  endurance: <path d="M10 3 H14 M11 3 V9 L5 20 H19 L13 9 V3 M8 15 H16" />,
  // Peaks
  hills: <path d="M2 20 L9 7 L13 14 L16 10 L22 20 Z" />,
  // Cycle: ring of weeks closing on itself
  consistency: <path d="M12 3 a9 9 0 1 0 9 9 M21 12 l-3 -3 M21 12 l3 -3" />,
}

/** One stat as an engraved plaque. Stats are uncapped totals, so it shows the value, never a fill. */
export function StatPlaque({
  stat,
  label,
  value,
}: {
  stat: StatName
  label: string
  value: number
}) {
  return (
    <div className="stat-plaque">
      <svg viewBox="0 0 24 24" className="stat-plaque__glyph" aria-hidden="true" focusable="false">
        {GLYPHS[stat]}
      </svg>
      <dt className="stat-plaque__label">{label}</dt>
      <dd className="stat-plaque__value">{value.toFixed(1)}</dd>
    </div>
  )
}
