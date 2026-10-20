import { describe, expect, it } from 'vitest'
import { shouldSync, STALE_AFTER_MS } from './autosync'

const NOW = Date.parse('2026-10-16T12:00:00Z')
const ago = (ms: number) => new Date(NOW - ms).toISOString()

describe('shouldSync', () => {
  it('syncs a user who never synced', () => {
    expect(shouldSync(null, 'idle', NOW)).toBe(true)
  })

  it('leaves a fresh sync alone and picks up a stale one', () => {
    expect(shouldSync(ago(STALE_AFTER_MS - 1000), 'idle', NOW)).toBe(false)
    expect(shouldSync(ago(STALE_AFTER_MS + 1000), 'idle', NOW)).toBe(true)
  })

  it('never starts a second import while one is running', () => {
    expect(shouldSync(null, 'running', NOW)).toBe(false)
  })

  it('retries after a failure once stale', () => {
    expect(shouldSync(ago(STALE_AFTER_MS + 1000), 'failed', NOW)).toBe(true)
  })
})
