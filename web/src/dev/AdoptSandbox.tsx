import { useState } from 'react'
import { GiltFrame } from '../components/GiltFrame'
import { BreedPicker, type PickerBreed } from '../features/adopt/BreedPicker'
import '../components/scene.css'
import '../features/adopt/adopt.css'
import { CETUS_TEXTURED_URL } from './cetus'

const BREEDS: PickerBreed[] = [
  {
    id: 'cetus',
    name: 'Cetus',
    description:
      'Sea-monster of the deep, patient and enduring. It reads the long road the way it reads the tide.',
    model_url: CETUS_TEXTURED_URL,
  },
  {
    id: 'pegasus',
    name: 'Pegasus',
    description: 'Winged and restless, it would rather be in the air than anywhere else.',
    model_url: null,
  },
]

/** Dev-only: the whole adoption screen with fake breeds and no API. */
export function AdoptSandbox() {
  const [value, setValue] = useState(BREEDS[0].id)
  return (
    <main className="scene adopt">
      <h1 className="sr-only">Adopt your strider</h1>
      <BreedPicker breeds={BREEDS} value={value} onChange={setValue} />
      <GiltFrame className="adopt__form">
        <form onSubmit={(e) => e.preventDefault()}>
          <label>
            Name
            <input defaultValue="Thessaly" />
          </label>
          <button type="button">Suggest another</button>
          <button type="submit" className="primary">
            Adopt
          </button>
        </form>
      </GiltFrame>
    </main>
  )
}
