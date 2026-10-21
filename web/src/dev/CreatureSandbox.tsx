import { useEffect, useState } from 'react'
import { CreatureSlot } from '../components/CreatureSlot'
import type { EnvironmentId } from '../components/creature/environments'
import './creature-sandbox.css'
import { CETUS_MESH_URL, CETUS_TEXTURED_URL } from './cetus'

/** Dev-only: inspect a self-contained GLB locally, without a server upload or Strava login. */
export function CreatureSandbox() {
  const [model, setModel] = useState<{ name: string; url: string } | null>(null)
  const [environment, setEnvironment] = useState<EnvironmentId>('sanctuary')
  const [preset, setPreset] = useState(CETUS_TEXTURED_URL)

  useEffect(() => {
    return () => {
      if (model) URL.revokeObjectURL(model.url)
    }
  }, [model])

  return (
    <main className="creature-sandbox">
      <CreatureSlot
        stage
        modelUrl={model?.url ?? (preset || null)}
        label={model?.name ?? 'Cetus sanctuary preview'}
        environment={environment}
      />
      <form className="creature-sandbox__controls" onSubmit={(event) => event.preventDefault()}>
        <h1>Creature studio</h1>
        <label>
          Model
          <select
            value={model ? 'local' : preset}
            onChange={(event) => {
              setModel(null)
              setPreset(event.target.value)
            }}
          >
            <option value={CETUS_TEXTURED_URL}>Cetus — textured</option>
            <option value={CETUS_MESH_URL}>Cetus — mesh only</option>
            <option value="">Empty stage</option>
            {model && <option value="local">{model.name}</option>}
          </select>
        </label>
        <label>
          Local model (.glb)
          <input
            type="file"
            accept=".glb"
            onChange={(event) => {
              const file = event.target.files?.[0]
              if (file) setModel({ name: file.name, url: URL.createObjectURL(file) })
              event.target.value = ''
            }}
          />
        </label>
        <label>
          Environment
          <select
            value={environment}
            onChange={(event) => setEnvironment(event.target.value as EnvironmentId)}
          >
            <option value="sanctuary">Flooded sanctuary</option>
            <option value="neutral">Neutral stage</option>
          </select>
        </label>
        <p>
          Files stay in this browser. Use a GLB with embedded textures. An animation named Idle,
          Rest or Breathing plays automatically.
        </p>
        <button type="button" onClick={() => setModel(null)}>
          Clear local model
        </button>
      </form>
    </main>
  )
}
