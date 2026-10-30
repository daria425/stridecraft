import { User } from 'lucide-react'
import { Link } from 'react-router'
import { Banner } from '../../components/Banner'
import { GiltFrame } from '../../components/GiltFrame'
import { Stage } from '../../components/Stage'
import { StatList, type Stats } from '../../components/StatList'
import { JourneyMenu } from '../journey/JourneyMenu'
import '../../components/scene.css'
import './dashboard.css'

export type DashboardViewProps = {
  trainer: string
  striderName: string
  breedName: string
  breedId?: string
  adoptedOn: string
  modelUrl: string | null
  stats: Stats
  syncNote: string
  syncFailed: boolean
  onLogout: () => void
}

/** The scene fills the screen; the name banner and stats float over it. */
export function DashboardView(props: DashboardViewProps) {
  return (
    <main className="scene dashboard">
      <Stage modelUrl={props.modelUrl} label={props.striderName} breedId={props.breedId} />

      <header className="dashboard__bar">
        <span>{props.trainer}</span>
        <JourneyMenu />
        <div className="dashboard__actions">
          <Link to="/profile" aria-label="View profile" title="View profile">
            <User size={18} aria-hidden="true" />
          </Link>
          <button type="button" onClick={props.onLogout}>
            Log out
          </button>
        </div>
      </header>

      <section className="dashboard__banner" aria-labelledby="strider-name">
        <Banner
          level={1}
          id="strider-name"
          title={props.striderName}
          subtitle={`${props.breedName}, adopted ${props.adoptedOn}`}
        />
      </section>

      <aside className="dashboard__stats">
        <GiltFrame className="dashboard__stats-frame">
          <StatList stats={props.stats} />
        </GiltFrame>
        <p
          className={
            props.syncFailed ? 'dashboard__sync dashboard__sync--failed' : 'dashboard__sync'
          }
          aria-live="polite"
        >
          {props.syncNote}
        </p>
      </aside>
    </main>
  )
}
