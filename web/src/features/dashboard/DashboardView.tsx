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
        <button type="button" onClick={props.onLogout}>
          Log out
        </button>
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
