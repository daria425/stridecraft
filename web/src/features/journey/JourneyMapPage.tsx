import { lazy, Suspense, useMemo, useState } from 'react'
import { useBreeds, useJourney, useMe, type Journey } from '../../api/queries'
import { GiltFrame } from '../../components/GiltFrame'
import { SceneBoundary } from '../../components/creature/SceneBoundary'
import { SceneMessage } from '../../components/SceneMessage'
import '../../components/scene.css'
import '../../components/stage.css'
import { JourneyArrivals } from './JourneyArrivals'
import { JourneyMenu } from './JourneyMenu'
import { buildLegMap, type LegMap, type MapNode } from './legMap'
import './journey.css'

// three.js only comes down when the map is opened.
const Scene = lazy(() => import('./maps/IsleMap'))

function describe(node: MapNode, kmToGo: number): { title: string; text: string } {
  if (node.event) return { title: node.event.title, text: node.event.text }
  if (node.state === 'arriving')
    return {
      title: 'Something awaits',
      text: 'Dismiss the banner to see what the strider found here.',
    }
  const place = node.isLandmark ? node.label : `Stop ${node.index}`
  return node.state === 'next'
    ? { title: place, text: `${kmToGo.toFixed(1)} km to go.` }
    : {
        title: place,
        text: node.isLandmark
          ? 'The end of this leg of the road.'
          : 'The road has not reached here yet.',
      }
}

function Hud({ map }: { map: LegMap }) {
  const done = map.nodes.filter((n) => n.state === 'done').length
  return (
    <GiltFrame className="journey-hud">
      <h1>The Voyage</h1>
      <p className="journey-hud__leg">{map.legName}</p>
      <p
        className="journey-hud__progress"
        aria-label={`${done} of ${map.nodes.length} stops reached`}
      >
        {map.nodes.map((n) => (
          <span key={n.index} className={`journey-hud__pip journey-hud__pip--${n.state}`} />
        ))}
      </p>
      <p className="journey-hud__km">
        <strong>{map.kmToGo.toFixed(1)} km</strong> to the next waypoint · {map.spacingKm} km apart
      </p>
    </GiltFrame>
  )
}

function Detail({ map, selected }: { map: LegMap; selected: number | null }) {
  const node = map.nodes.find((n) => n.index === selected)
  if (!node)
    return (
      <p className="journey-detail__hint">Drag to look around. Select a stop to read about it.</p>
    )
  const { title, text } = describe(node, map.kmToGo)
  return (
    <GiltFrame className="journey-detail" aria-live="polite">
      <h2>{title}</h2>
      <p>{text}</p>
    </GiltFrame>
  )
}

function JourneyMapView({ journey }: { journey: Journey }) {
  const me = useMe().data
  const breeds = useBreeds().data
  const strider = me?.strider
  const modelUrl = breeds?.find((b) => b.id === strider?.breed)?.model_url ?? null
  const map = useMemo(() => buildLegMap(journey), [journey])
  const [selected, setSelected] = useState<number | null>(null)

  return (
    <main className="scene journey-map">
      <div className="stage">
        <SceneBoundary
          fallback={<p className="journey-map__note">The map could not be drawn on this device.</p>}
        >
          <Suspense fallback={<p className="journey-map__note">Unrolling the map…</p>}>
            <Scene
              map={map}
              modelUrl={modelUrl}
              breedId={strider?.breed}
              selected={selected}
              onSelect={setSelected}
            />
          </Suspense>
        </SceneBoundary>
      </div>
      <header className="journey-map__bar">
        <JourneyMenu />
      </header>
      <div className="journey-map__hud">
        <Hud map={map} />
      </div>
      <div className="journey-map__detail">
        <Detail map={map} selected={selected} />
      </div>
      <JourneyArrivals />
    </main>
  )
}

/** The voyage: the current leg of the road as a 3D map. */
export function JourneyMapPage() {
  const journey = useJourney()
  if (journey.isPending) return <SceneMessage>Charting the road...</SceneMessage>
  if (journey.isError)
    return <SceneMessage>Could not load the journey. Try again in a moment.</SceneMessage>
  return <JourneyMapView journey={journey.data} />
}
