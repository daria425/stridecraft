import type { LegMap } from '../legMap'

/** What every map scene receives: the leg to draw and which stop is selected. */
export type MapSceneProps = {
  map: LegMap
  modelUrl: string | null
  breedId?: string
  selected: number | null
  onSelect: (index: number | null) => void
}
