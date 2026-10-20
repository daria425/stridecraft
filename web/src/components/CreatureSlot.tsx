import './creature-slot.css'

/** The one place a strider's 3D model gets rendered. For now a dark well that says what will be
 * here; the 3D pass replaces the body and keeps the props. `stage` fills its container edge to
 * edge as a scene; the default is a fixed round well (breed picker). */
export function CreatureSlot({
  modelUrl,
  label,
  stage = false,
}: {
  modelUrl: string | null
  label: string
  stage?: boolean
}) {
  return (
    <div
      role="img"
      aria-label={label}
      data-model-url={modelUrl ?? undefined}
      className={stage ? 'creature-slot creature-slot--stage' : 'creature-slot'}
    >
      <span>{label}</span>
    </div>
  )
}
