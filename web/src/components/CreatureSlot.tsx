import { lazy, Suspense } from 'react'
import { SceneBoundary } from './creature/SceneBoundary'
import { environmentForBreed, type EnvironmentId } from './creature/environments'
import './creature-slot.css'

const CreatureScene = lazy(() => import('./creature/CreatureScene'))

/** The shared renderer. Model identity, habitat and layout are independent inputs. */
export function CreatureSlot({
  modelUrl,
  label,
  stage = false,
  breedId,
  environment,
}: {
  modelUrl: string | null
  label: string
  stage?: boolean
  breedId?: string
  environment?: EnvironmentId
}) {
  return (
    <div
      role="img"
      aria-label={label}
      data-model-url={modelUrl ?? undefined}
      className={stage ? 'creature-slot creature-slot--stage' : 'creature-slot'}
    >
      <SceneBoundary
        key={`${modelUrl}:${environment ?? breedId}`}
        fallback={<span className="creature-slot__note">3D preview is unavailable.</span>}
      >
        <Suspense fallback={<span className="creature-slot__note">Preparing the scene…</span>}>
          <CreatureScene
            modelUrl={modelUrl}
            stage={stage}
            environment={environment ?? environmentForBreed(breedId)}
          />
        </Suspense>
      </SceneBoundary>
    </div>
  )
}
