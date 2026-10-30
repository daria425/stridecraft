import { BufferAttribute, BufferGeometry, type Color } from 'three'

/** An island: a grassy top and a rocky underside that meet at one shared rim, so there is no gap.
 * `rim(angle)` scales the radius per direction for an uneven outline; `height` is the ground
 * height at x/z (it is blended to zero at the rim); `depth` is how far the rock hangs below. */
export function polarIsland(options: {
  radius: number
  rim: (angle: number) => number
  rings: number
  segments: number
  height: (x: number, z: number) => number
  topColor: (x: number, z: number, y: number, edge: number) => Color
  rockColor: (depth: number, angle: number) => Color
  depth: number
  jag: (x: number, z: number) => number
}): { top: BufferGeometry; bottom: BufferGeometry } {
  const { radius, rim, rings, segments, height, topColor, rockColor, depth, jag } = options
  const top = { p: [] as number[], c: [] as number[], i: [] as number[] }
  const bottom = { p: [] as number[], c: [] as number[], i: [] as number[] }
  for (let ring = 0; ring <= rings; ring++) {
    const u = ring / rings
    for (let s = 0; s <= segments; s++) {
      const angle = (s / segments) * Math.PI * 2
      const reach = radius * rim(angle) * u
      const x = Math.cos(angle) * reach
      const z = Math.sin(angle) * reach
      const fade = 1 - Math.min(1, Math.max(0, (u - 0.82) / 0.18)) ** 2 // flat at the rim
      const y = height(x, z) * fade
      top.p.push(x, y, z)
      const paint = topColor(x, z, y, u)
      top.c.push(paint.r, paint.g, paint.b)

      // The rock is a bowl; jag breaks it into facets without moving the shared rim.
      const bowl = depth * (1 - u * u) ** 0.65
      const by = -bowl + jag(x, z) * bowl * 0.35
      bottom.p.push(x * (0.55 + 0.45 * u ** 0.6), by, z * (0.55 + 0.45 * u ** 0.6))
      const rock = rockColor(bowl / depth, angle)
      bottom.c.push(rock.r, rock.g, rock.b)
    }
  }
  const stride = segments + 1
  for (let ring = 0; ring < rings; ring++) {
    for (let s = 0; s < segments; s++) {
      const a = ring * stride + s
      const b = a + 1
      const d = a + stride
      top.i.push(a, b, d, b, d + 1, d)
      bottom.i.push(a, d, b, b, d, d + 1)
    }
  }
  // The rim must match exactly: reset the bottom's last ring to the top's.
  for (let s = 0; s <= segments; s++) {
    const index = (rings * stride + s) * 3
    bottom.p[index] = top.p[index]
    bottom.p[index + 1] = top.p[index + 1]
    bottom.p[index + 2] = top.p[index + 2]
  }
  return { top: build(top.p, top.c, top.i), bottom: build(bottom.p, bottom.c, bottom.i) }
}

function build(positions: number[], colors: number[], indices: number[]): BufferGeometry {
  const geometry = new BufferGeometry()
  geometry.setAttribute('position', new BufferAttribute(new Float32Array(positions), 3))
  geometry.setAttribute('color', new BufferAttribute(new Float32Array(colors), 3))
  geometry.setIndex(indices)
  geometry.computeVertexNormals()
  return geometry
}
