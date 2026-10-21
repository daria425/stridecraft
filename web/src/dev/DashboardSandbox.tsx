import { DashboardView } from '../features/dashboard/DashboardView'
import { CETUS_TEXTURED_URL } from './cetus'

/** Dev-only: the dashboard with fake data, no Strava or API needed. `?name=` tries a long name. */
export function DashboardSandbox() {
  const name = new URLSearchParams(window.location.search).get('name') ?? 'Thessaly'
  return (
    <DashboardView
      trainer="Daria"
      striderName={name}
      breedName="Cetus"
      breedId="cetus"
      adoptedOn="1 Sep 2026"
      modelUrl={CETUS_TEXTURED_URL}
      stats={{ speed: 10.8, endurance: 12.4, hills: 11.1, consistency: 10.6 }}
      syncNote="Last synced: 16 Oct 2026, 08:12."
      syncFailed={false}
      onLogout={() => {}}
    />
  )
}
