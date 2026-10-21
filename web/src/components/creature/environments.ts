/** Presentation choices only. Breed definitions and model URLs still come from the API.
 * Keep locations optional: deciding on a Pegasus habitat shouldn't change the model loader. */
export type EnvironmentId = 'sanctuary' | 'neutral'

export function environmentForBreed(breedId?: string): EnvironmentId {
  return breedId === 'cetus' ? 'sanctuary' : 'neutral'
}
