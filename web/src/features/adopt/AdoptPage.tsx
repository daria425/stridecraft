import { useEffect, useState } from 'react'
import { useAdopt, useBreeds, useRandomName } from '../../api/queries'
import { GiltFrame } from '../../components/GiltFrame'
import { SceneMessage } from '../../components/SceneMessage'
import { BreedPicker } from './BreedPicker'
import '../../components/scene.css'
import './adopt.css'

const MAX_NAME_LENGTH = 30
// Km between journey waypoints; the server enforces the same bounds (services/adoption.py).
const MIN_SPACING_KM = 50
const MAX_SPACING_KM = 1000

export function AdoptPage() {
  const breeds = useBreeds()
  const adopt = useAdopt()
  const randomName = useRandomName()
  const [breedId, setBreedId] = useState<string | null>(null)
  const [name, setName] = useState('')
  const [spacing, setSpacing] = useState(String(MIN_SPACING_KM))

  const shuffle = () => randomName().then(setName)
  useEffect(() => {
    let current = true
    void randomName().then((suggested) => current && setName(suggested))
    return () => {
      current = false
    }
  }, [randomName])

  if (breeds.isPending) return <SceneMessage>Loading breeds...</SceneMessage>
  if (breeds.isError)
    return <SceneMessage>Could not load breeds. Try again in a moment.</SceneMessage>
  const chosen = breedId ?? breeds.data[0]?.id
  if (!chosen) return <SceneMessage>There are no breeds to adopt yet.</SceneMessage>

  return (
    <main className="scene adopt">
      <h1 className="sr-only">Adopt your strider</h1>
      <BreedPicker breeds={breeds.data} value={chosen} onChange={setBreedId} />
      <GiltFrame className="adopt__form">
        <form
          onSubmit={(event) => {
            event.preventDefault()
            adopt.mutate({
              breed: chosen,
              name: name.trim() || null,
              waypoint_spacing_km: Number(spacing),
            })
          }}
        >
          <label>
            Name
            <input
              value={name}
              maxLength={MAX_NAME_LENGTH}
              onChange={(e) => setName(e.target.value)}
            />
          </label>
          <button type="button" onClick={shuffle}>
            Suggest another
          </button>
          <label>
            Distance between waypoints (km)
            <input
              type="number"
              inputMode="numeric"
              required
              min={MIN_SPACING_KM}
              max={MAX_SPACING_KM}
              step={1}
              value={spacing}
              aria-describedby="spacing-hint"
              onChange={(e) => setSpacing(e.target.value)}
            />
          </label>
          <p id="spacing-hint" className="adopt__hint">
            A smaller number means more frequent waypoints, so faster progression. Set it to match
            your typical weekly mileage.
          </p>
          <button type="submit" className="primary" disabled={adopt.isPending}>
            Adopt
          </button>
          {adopt.error && <p role="alert">{adopt.error.message}</p>}
        </form>
      </GiltFrame>
    </main>
  )
}
