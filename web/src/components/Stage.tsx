import { CreatureSlot } from './CreatureSlot'
import { SigilRing } from './SigilRing'
import './stage.css'

/** The full-screen scene: a summoning circle on the floor and the strider's 3D slot. Fills the
 * nearest positioned ancestor; pages float their panels over it. */
export function Stage({ modelUrl, label }: { modelUrl: string | null; label: string }) {
  return (
    <div className="stage">
      <div className="stage__floor" aria-hidden="true">
        <SigilRing />
      </div>
      <CreatureSlot stage modelUrl={modelUrl} label={label} />
    </div>
  )
}
