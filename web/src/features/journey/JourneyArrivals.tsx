import { useJourney, useMarkJourneySeen } from '../../api/queries'
import { Banner } from '../../components/Banner'
import { unseenEvents } from './legMap'
import './journey.css'

/** The banner for a waypoint the strider has just reached: its title and the text from the
 * encounter's YAML. Several can be waiting after a long run or a sync; they show oldest first,
 * and each is marked seen on the server when dismissed, so it appears once on every device. */
export function JourneyArrivals() {
  const journey = useJourney().data
  const markSeen = useMarkJourneySeen()
  if (!journey) return null
  const waiting = unseenEvents(journey)
  const event = waiting[0]
  if (!event) return null

  const eyebrow =
    event.kind === 'landmark' ? 'Landmark reached' : `Waypoint ${event.waypoint_number}`
  return (
    <>
      <div className="arrival-scrim" aria-hidden="true" />
      <div
        className="arrival"
        role="dialog"
        aria-labelledby="arrival-title"
        key={event.waypoint_number}
      >
        <p className="arrival__eyebrow">
          {eyebrow}
          {waiting.length > 1 ? ` · ${waiting.length} new` : ''}
        </p>
        <Banner level={2} id="arrival-title" title={event.title} subtitle={event.text} />
        <button
          type="button"
          className="primary arrival__continue"
          autoFocus
          onClick={() => markSeen.mutate(event.waypoint_number)}
        >
          {waiting.length > 1 ? 'Next' : 'Onward'}
        </button>
      </div>
    </>
  )
}
