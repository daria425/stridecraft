import { useLogout, useMe, useBreeds, type SyncStatus } from '../../api/queries'
import { DashboardView } from './DashboardView'
import { useAutoSync } from './useAutoSync'

function describeSync(status: SyncStatus | undefined): string {
  if (!status) return ''
  if (status.state === 'running') return 'Importing your runs...'
  if (status.state === 'failed')
    return `Last import failed${status.error ? `: ${status.error}` : ''}.`
  const when = status.last_synced_at ? new Date(status.last_synced_at).toLocaleString() : 'never'
  const note = status.last_result?.truncated
    ? ' Some of your oldest runs were left out because you were away for a long time.'
    : ''
  return `Last synced: ${when}.${note}`
}

export function DashboardPage() {
  const me = useMe().data
  const breeds = useBreeds().data
  const sync = useAutoSync()
  const logout = useLogout()
  const strider = me?.strider
  if (!me || !strider) return null
  const breed = breeds?.find((b) => b.id === strider.breed)

  return (
    <DashboardView
      trainer={me.firstname ?? me.username}
      striderName={strider.name}
      breedName={breed?.name ?? strider.breed}
      breedId={strider.breed}
      adoptedOn={new Date(strider.adopted_at).toLocaleDateString()}
      modelUrl={breed?.model_url ?? null}
      stats={strider.stats}
      syncNote={describeSync(sync.data)}
      syncFailed={sync.data?.state === 'failed'}
      onLogout={() => logout.mutate()}
    />
  )
}
