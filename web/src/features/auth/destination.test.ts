import { describe, expect, it } from 'vitest'
import type { Me } from '../../api/queries'
import { destinationFor } from './destination'

const user = { id: 1, username: 'ada', firstname: 'Ada', profile_url: null }
const strider = {
  name: 'Aura',
  breed: 'cetus',
  adopted_at: '2026-10-01T00:00:00Z',
  stats: { speed: 10, endurance: 10, hills: 10, consistency: 10 },
}

describe('destinationFor', () => {
  it('sends anonymous visitors to login', () => {
    expect(destinationFor(null)).toBe('/login')
  })

  it('sends a user without a strider to adoption', () => {
    expect(destinationFor({ ...user, strider: null } as Me)).toBe('/adopt')
  })

  it('sends a user with a strider to the dashboard', () => {
    expect(destinationFor({ ...user, strider } as Me)).toBe('/')
  })
})
