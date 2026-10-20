import { useState } from 'react'
import { BreedPicker, type PickerBreed } from '../features/adopt/BreedPicker'
import '../components/scene.css'
import '../features/adopt/adopt.css'

const FAKE_BREEDS: PickerBreed[] = [
  { id: 'a', name: 'Cetus', description: 'A short description.', model_url: null },
  {
    id: 'b',
    name: 'Chimera',
    description: 'A much longer description '.repeat(12),
    model_url: null,
  },
  { id: 'c', name: 'Pegasus', description: 'Another one.', model_url: null },
]

/** Dev-only: iterate on the picker without Strava, a login or real breeds. */
export function PickerSandbox() {
  const [value, setValue] = useState(FAKE_BREEDS[0].id)
  return (
    <main className="scene adopt">
      <h1 className="sr-only">Picker sandbox</h1>
      <BreedPicker breeds={FAKE_BREEDS} value={value} onChange={setValue} />
    </main>
  )
}
