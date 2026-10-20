export const STALE_AFTER_MS = 10 * 60 * 1000

/** Whether opening (or returning to) the dashboard should start an import: never synced, or the
 * last one is older than STALE_AFTER_MS, and none is running already. */
export function shouldSync(
  lastSyncedAt: string | null,
  state: 'idle' | 'running' | 'failed',
  now: number,
): boolean {
  if (state === 'running') return false
  if (lastSyncedAt === null) return true
  return now - new Date(lastSyncedAt).getTime() > STALE_AFTER_MS
}
