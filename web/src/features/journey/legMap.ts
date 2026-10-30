import type { Journey, JourneyEvent } from '../../api/queries'

/** One stop on the current leg's road, in walking order. */
export type MapNode = {
  index: number // 1 for the first waypoint of the leg; the last one is the landmark
  // `arriving` is crossed but not yet shown to the user: it stays a surprise until they have read it.
  state: 'done' | 'arriving' | 'next' | 'ahead'
  isLandmark: boolean
  event: JourneyEvent | null // what happened there, once shown
  label: string // the title once shown, the landmark's name for the last stop, else ''
}

/** What every map draws: the road of the current leg, from where the leg began to its landmark. */
export type LegMap = {
  legName: string
  nodes: MapNode[]
  position: number // the last stop shown to the user, where the strider stands; 0 is the start
  kmToGo: number
  spacingKm: number
  landmarkName: string
}

/** Turn the API's journey into the current leg's road. The leg starts after the last landmark, so
 * its crossed stops are the newest `leg_waypoint - 1` events. Stops the user has not been shown yet
 * (`seen_waypoint`) are left unrevealed, and the strider waits at the last one they have seen. */
export function buildLegMap(journey: Journey): LegMap {
  const done = Math.max(0, Math.min(journey.leg_waypoint - 1, journey.crossed.length))
  const crossedHere = journey.crossed.slice(0, done).reverse() // oldest first
  const nodes: MapNode[] = Array.from({ length: journey.leg_length }, (_, i) => {
    const index = i + 1
    const isLandmark = index === journey.leg_length
    const crossed = crossedHere[i]
    const shown = crossed && crossed.waypoint_number <= journey.seen_waypoint ? crossed : null
    const state = shown
      ? 'done'
      : crossed
        ? 'arriving'
        : index === journey.leg_waypoint
          ? 'next'
          : 'ahead'
    const label = shown?.title ?? (isLandmark ? journey.landmark.name : '')
    return { index, state, isLandmark, event: shown, label }
  })
  return {
    legName: journey.leg_name,
    nodes,
    position: nodes.filter((n) => n.state === 'done').length,
    kmToGo: journey.km_to_go,
    spacingKm: journey.spacing_km,
    landmarkName: journey.landmark.name,
  }
}

/** Crossings the user has not been shown yet, oldest first, so they read in the order they happened. */
export function unseenEvents(journey: Journey): JourneyEvent[] {
  return journey.crossed.filter((e) => e.waypoint_number > journey.seen_waypoint).reverse()
}
