import { useCallback, useEffect, useRef } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useStartSync, useSyncStatus } from '../../api/queries'
import { shouldSync } from './autosync'

/** Keeps the dashboard fresh with no button: sync when it opens and when the tab comes back into
 * view (a run finished while it sat in the background). A webhook would replace this later. */
export function useAutoSync() {
  const client = useQueryClient()
  const status = useSyncStatus()
  const { mutate: startSync } = useStartSync()
  const latest = useRef(status.data)
  useEffect(() => {
    latest.current = status.data
  })

  const check = useCallback(() => {
    const current = latest.current
    if (current && shouldSync(current.last_synced_at, current.state, Date.now())) startSync()
  }, [startSync])

  // On open: once, as soon as the status is known. Not on every status change, or a failed sync
  // with an old last_synced_at would be retried in a loop.
  const known = status.data !== undefined
  useEffect(() => {
    if (known) check()
  }, [known, check])

  useEffect(() => {
    const onVisible = () => {
      if (document.visibilityState === 'visible') check()
    }
    document.addEventListener('visibilitychange', onVisible)
    return () => document.removeEventListener('visibilitychange', onVisible)
  }, [check])

  // When an import finishes, the strider's stats have changed.
  const state = status.data?.state
  const previous = useRef(state)
  useEffect(() => {
    if (previous.current === 'running' && state !== 'running') {
      void client.invalidateQueries({ queryKey: ['me'] })
    }
    previous.current = state
  }, [state, client])

  return status
}
