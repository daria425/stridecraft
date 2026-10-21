import { CreatureSlot } from './CreatureSlot'
import './stage.css'

/** Pages float their panels over a single canvas, including its floor engraving. */
export function Stage({
  modelUrl,
  label,
  breedId,
}: {
  modelUrl: string | null
  label: string
  breedId?: string
}) {
  return (
    <div className="stage">
      <CreatureSlot stage modelUrl={modelUrl} label={label} breedId={breedId} />
    </div>
  )
}
