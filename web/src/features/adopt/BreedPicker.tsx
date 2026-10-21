import { Banner } from '../../components/Banner'
import { ChevronButton } from '../../components/ChevronButton'
import { GiltFrame } from '../../components/GiltFrame'
import { Stage } from '../../components/Stage'
import './breed-picker.css'

export type PickerBreed = {
  id: string
  name: string
  description: string
  model_url: string | null
}

/** Carousel: one breed at a time, shown on the stage. Knows nothing about the API or the adoption
 * flow, so it can be swapped for another layout (a grid, say) without touching the page that uses
 * it. Renders straight into the page's grid: the stage behind, arrows and banner, then the lore. */
export function BreedPicker({
  breeds,
  value,
  onChange,
}: {
  breeds: PickerBreed[]
  value: string
  onChange: (id: string) => void
}) {
  const index = Math.max(
    0,
    breeds.findIndex((b) => b.id === value),
  )
  const breed = breeds[index]
  const step = (by: number) => onChange(breeds[(index + by + breeds.length) % breeds.length].id)
  if (!breed) return null
  const single = breeds.length < 2
  return (
    <section aria-label="Choose a breed" className="breed-picker">
      <Stage modelUrl={breed.model_url} label={breed.name} breedId={breed.id} />
      <div className="breed-picker__banner">
        <ChevronButton
          direction="left"
          label="Previous breed"
          onClick={() => step(-1)}
          disabled={single}
        />
        <Banner level={2} title={breed.name} subtitle={`${index + 1} of ${breeds.length}`} />
        <ChevronButton
          direction="right"
          label="Next breed"
          onClick={() => step(1)}
          disabled={single}
        />
      </div>
      <GiltFrame
        className="breed-picker__lore"
        role="region"
        aria-label={`About ${breed.name}`}
        tabIndex={0}
      >
        <p>{breed.description}</p>
      </GiltFrame>
    </section>
  )
}
