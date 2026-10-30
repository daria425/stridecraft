import { describe, expect, it } from 'vitest'
import type { Journey, JourneyEvent } from '../../api/queries'
import { buildLegMap, unseenEvents } from './legMap'

function event(n: number, legId = 'tide_road'): JourneyEvent {
  return {
    waypoint_number: n,
    kind: 'encounter',
    title: `Stop ${n}`,
    text: '',
    leg_id: legId,
    crossed_at: '2026-01-01T00:00:00Z',
  }
}

/** Newest first, like the API. */
function journey(crossedCount: number, over: Partial<Journey> = {}): Journey {
  const crossed = Array.from({ length: crossedCount }, (_, i) => event(crossedCount - i))
  return {
    intro: '',
    total_km: 0,
    spacing_km: 50,
    leg_name: 'The Tide Road',
    leg_length: 6,
    leg_waypoint: crossedCount + 1,
    km_to_go: 20,
    landmark: { name: 'The Isle of the Sirens', km_to_go: 270 },
    crossed,
    seen_waypoint: 0,
    ...over,
  }
}

describe('buildLegMap', () => {
  it('starts with nothing crossed and the first stop next', () => {
    const map = buildLegMap(journey(0, { seen_waypoint: 0 }))
    expect(map.position).toBe(0)
    expect(map.nodes.map((n) => n.state)).toEqual([
      'next',
      'ahead',
      'ahead',
      'ahead',
      'ahead',
      'ahead',
    ])
    expect(map.nodes[5]).toMatchObject({ isLandmark: true, label: 'The Isle of the Sirens' })
  })

  it('shows only this leg: crossings from earlier legs are left off', () => {
    // 8 crossed in total, but the strider is 2 stops into a new leg (stops 7 and 8).
    const map = buildLegMap(journey(8, { leg_waypoint: 3, seen_waypoint: 8 }))
    expect(map.position).toBe(2)
    expect(
      map.nodes.filter((n) => n.state === 'done').map((n) => n.event?.waypoint_number),
    ).toEqual([7, 8])
    expect(map.nodes[2].state).toBe('next')
  })

  it('is a fresh leg right after a landmark', () => {
    const map = buildLegMap(journey(6, { leg_waypoint: 1, seen_waypoint: 6 }))
    expect(map.position).toBe(0)
    expect(map.nodes.every((n) => n.event === null)).toBe(true)
  })
})

it('keeps unseen crossings unrevealed, with the strider waiting at the last one seen', () => {
  const map = buildLegMap(journey(3, { seen_waypoint: 1 }))
  expect(map.nodes.map((n) => n.state).slice(0, 4)).toEqual([
    'done',
    'arriving',
    'arriving',
    'next',
  ])
  expect(map.position).toBe(1)
  expect(map.nodes[1].event).toBeNull() // no spoilers
})

describe('unseenEvents', () => {
  it('returns what is newer than the seen mark, oldest first', () => {
    const unseen = unseenEvents(journey(5, { seen_waypoint: 3 }))
    expect(unseen.map((e) => e.waypoint_number)).toEqual([4, 5])
  })

  it('is empty once everything has been seen', () => {
    expect(unseenEvents(journey(5, { seen_waypoint: 5 }))).toEqual([])
  })
})
