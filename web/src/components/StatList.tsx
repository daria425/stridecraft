import { StatPlaque, type StatName } from './StatPlaque'
import './stat-plaque.css'

export type Stats = Record<StatName, number>

const LABELS: Record<StatName, string> = {
  speed: 'Speed',
  endurance: 'Endurance',
  hills: 'Hills',
  consistency: 'Consistency',
}

/** The four stats as plaques: a single column with glyphs on desktop, a compact 2x2 on phones. */
export function StatList({ stats }: { stats: Stats }) {
  return (
    <dl className="stat-list">
      {(Object.keys(LABELS) as StatName[]).map((stat) => (
        <StatPlaque key={stat} stat={stat} label={LABELS[stat]} value={stats[stat]} />
      ))}
    </dl>
  )
}
