import { Color } from 'three'
import { seeded } from './noise'

/** Pick up to `count` random spots in a box that pass `accept`, the same ones every time. */
export function scatter(
  count: number,
  seed: number,
  box: { x: [number, number]; z: [number, number] },
  accept: (x: number, z: number) => boolean,
): [number, number][] {
  const random = seeded(seed)
  const spots: [number, number][] = []
  for (let tries = 0; tries < count * 40 && spots.length < count; tries++) {
    const x = box.x[0] + random() * (box.x[1] - box.x[0])
    const z = box.z[0] + random() * (box.z[1] - box.z[0])
    if (accept(x, z)) spots.push([x, z])
  }
  return spots
}

const scratch = new Color()

/** A blend of two colours. The returned Color is reused: read it before the next call. */
export function tint(a: string, b: string, t: number): Color {
  return scratch.set(a).lerp(new Color(b), Math.min(1, Math.max(0, t)))
}
