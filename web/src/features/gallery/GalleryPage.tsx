import { useState } from 'react'
import { useBreeds } from '../../api/queries'
import { CreatureSlot } from '../../components/CreatureSlot'
import { SceneMessage } from '../../components/SceneMessage'
import '../../components/scene.css'
import './gallery.css'

/** TEMPORARY: previews every breed's `model` from the YAML via GET /breeds. Delete when done. */
export function GalleryPage() {
  const breeds = useBreeds()
  const [picked, setPicked] = useState<string | null>(null)

  if (breeds.isPending) return <SceneMessage>Loading breeds...</SceneMessage>
  if (breeds.isError) return <SceneMessage>Could not load breeds.</SceneMessage>

  const current = breeds.data.find((b) => b.id === picked) ?? breeds.data[0]
  if (!current) return <SceneMessage>There are no breeds.</SceneMessage>

  return (
    <main className="gallery">
      <nav className="gallery__list" aria-label="Breeds">
        {breeds.data.map((b) => (
          <button
            key={b.id}
            type="button"
            aria-pressed={b.id === current.id}
            className="gallery__item"
            onClick={() => setPicked(b.id)}
          >
            {b.name}
            <small>{b.model_url ? 'model' : 'no model yet'}</small>
          </button>
        ))}
      </nav>
      <section className="gallery__view">
        <CreatureSlot
          stage
          modelUrl={current.model_url ?? null}
          label={`${current.name} preview`}
          breedId={current.id}
        />
        <p className="gallery__url">{current.model_url ?? 'model: null'}</p>
      </section>
    </main>
  )
}
