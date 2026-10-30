import { BufferAttribute, BufferGeometry, CatmullRomCurve3, Vector3 } from 'three'

/** The road of one leg, laid on a map's ground. `nodes[0]` is the start, `nodes[n]` the landmark;
 * `curve` runs through all of them at even spacing, so `t` is a fraction of the way along. */
export type Road = {
  curve: CatmullRomCurve3
  nodes: Vector3[]
  nodeT: number[]
}

/** Lay a road through control points on the ground (x/z pairs, where the ground's height is
 * looked up) and space `stops` waypoints evenly along it, after the start. */
export function layRoad(
  control: [number, number][],
  heightAt: (x: number, z: number) => number,
  stops: number,
): Road {
  const flat = new CatmullRomCurve3(
    control.map(([x, z]) => new Vector3(x, 0, z)),
    false,
    'centripetal',
  )
  const dense = Array.from({ length: 240 }, (_, i) => {
    const point = flat.getPointAt(i / 239)
    return new Vector3(point.x, heightAt(point.x, point.z), point.z)
  })
  const curve = new CatmullRomCurve3(dense, false, 'centripetal')
  const nodeT = Array.from({ length: stops + 1 }, (_, i) => i / stops)
  return { curve, nodes: nodeT.map((t) => curve.getPointAt(t)), nodeT }
}

/** A flat ribbon along part of the road, lifted a little off the ground so it never z-fights. */
export function ribbon(
  curve: CatmullRomCurve3,
  from: number,
  to: number,
  width: number,
  lift: number,
): BufferGeometry {
  const steps = Math.max(2, Math.ceil((to - from) * 240))
  const positions: number[] = []
  const indices: number[] = []
  const up = new Vector3(0, 1, 0)
  for (let i = 0; i <= steps; i++) {
    const t = from + ((to - from) * i) / steps
    const point = curve.getPointAt(Math.min(1, t))
    const side = curve
      .getTangentAt(Math.min(1, t))
      .cross(up)
      .normalize()
      .multiplyScalar(width / 2)
    positions.push(point.x - side.x, point.y + lift, point.z - side.z)
    positions.push(point.x + side.x, point.y + lift, point.z + side.z)
    if (i < steps) {
      const a = i * 2
      indices.push(a, a + 1, a + 2, a + 1, a + 3, a + 2)
    }
  }
  const geometry = new BufferGeometry()
  geometry.setAttribute('position', new BufferAttribute(new Float32Array(positions), 3))
  geometry.setIndex(indices)
  geometry.computeVertexNormals()
  return geometry
}

/** Distance in the ground plane from a point to the road's control polyline. Lets a map flatten
 * its ground and keep its scenery off the road before the road's own heights are known. */
export function distanceToPolyline(control: [number, number][], x: number, z: number): number {
  let best = Infinity
  for (let i = 0; i < control.length - 1; i++) {
    const [ax, az] = control[i]
    const [bx, bz] = control[i + 1]
    const dx = bx - ax
    const dz = bz - az
    const t = Math.max(0, Math.min(1, ((x - ax) * dx + (z - az) * dz) / (dx * dx + dz * dz || 1)))
    best = Math.min(best, Math.hypot(x - (ax + dx * t), z - (az + dz * t)))
  }
  return best
}
