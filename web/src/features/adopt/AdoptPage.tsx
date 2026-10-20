import { useEffect, useState } from 'react'
import { useAdopt, useBreeds, useRandomName } from '../../api/queries'
import { GiltFrame } from '../../components/GiltFrame'
import { BreedPicker } from './BreedPicker'
import '../../components/scene.css'
import './adopt.css'

const MAX_NAME_LENGTH = 30

export function AdoptPage() {
  const breeds = useBreeds()
  const adopt = useAdopt()
  const randomName = useRandomName()
  const [breedId, setBreedId] = useState<string | null>(null)
  const [name, setName] = useState('')

  const shuffle = () => randomName().then(setName)
  useEffect(() => {
    let current = true
    void randomName().then((suggested) => current && setName(suggested))
    return () => {
      current = false
    }
  }, [randomName])

  if (breeds.isPending) return <AdoptMessage>Loading breeds...</AdoptMessage>
  if (breeds.isError)
    return <AdoptMessage>Could not load breeds. Try again in a moment.</AdoptMessage>
  const chosen = breedId ?? breeds.data[0]?.id
  if (!chosen) return <AdoptMessage>There are no breeds to adopt yet.</AdoptMessage>

  return (
    <main className="scene adopt">
      <h1 className="sr-only">Adopt your strider</h1>
      <BreedPicker breeds={breeds.data} value={chosen} onChange={setBreedId} />
      <GiltFrame className="adopt__form">
        <form
          onSubmit={(event) => {
            event.preventDefault()
            adopt.mutate({ breed: chosen, name: name.trim() || null })
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
          <button type="submit" className="primary" disabled={adopt.isPending}>
            Adopt
          </button>
          {adopt.error && <p role="alert">{adopt.error.message}</p>}
        </form>
      </GiltFrame>
    </main>
  )
}

function AdoptMessage({ children }: { children: string }) {
  return (
    <main className="scene adopt adopt--message">
      <p>{children}</p>
    </main>
  )
}
