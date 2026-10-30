import { useMemo } from 'react'
import { LatheGeometry, Vector2 } from 'three'
import { seeded } from './noise'

/** Low-poly Greek scenery, built from primitives. Everything is flat-shaded so the facets read
 * like the hand-painted dioramas in references/. Positions are the base of the object. */

type Place = { position?: [number, number, number]; rotation?: number; scale?: number }

function Flat({ color, roughness = 0.85, ...rest }: { color: string; roughness?: number }) {
  return <meshStandardMaterial color={color} roughness={roughness} flatShading {...rest} />
}

export function Rock({
  position = [0, 0, 0],
  scale = 1,
  rotation = 0,
  color = '#7b7480',
  seed = 1,
}: Place & { color?: string; seed?: number }) {
  const r = seeded(seed)
  return (
    <mesh
      position={[position[0], position[1] + 0.25 * scale, position[2]]}
      rotation={[r() * 3, rotation, r() * 3]}
      scale={[scale * (0.8 + r() * 0.6), scale * (0.5 + r() * 0.4), scale * (0.8 + r() * 0.6)]}
      castShadow
      receiveShadow
    >
      <dodecahedronGeometry args={[0.5, 0]} />
      <Flat color={color} />
    </mesh>
  )
}

export function OliveTree({
  position = [0, 0, 0],
  scale = 1,
  rotation = 0,
  leaf = '#7f9a62',
}: Place & { leaf?: string }) {
  return (
    <group position={position} rotation={[0, rotation, 0]} scale={scale}>
      <mesh position={[0, 0.45, 0]} rotation={[0, 0, 0.18]} castShadow>
        <cylinderGeometry args={[0.1, 0.18, 0.95, 6]} />
        <Flat color="#5b4636" />
      </mesh>
      <mesh position={[0.18, 0.78, 0.05]} rotation={[0, 0, -0.5]} castShadow>
        <cylinderGeometry args={[0.06, 0.1, 0.55, 5]} />
        <Flat color="#5b4636" />
      </mesh>
      {[
        [0, 1.2, 0, 0.62],
        [-0.42, 1.0, 0.12, 0.42],
        [0.5, 1.15, -0.1, 0.46],
        [0.1, 1.5, 0.15, 0.36],
      ].map(([x, y, z, r], i) => (
        <mesh key={i} position={[x, y, z]} scale={[1.15, 0.8, 1.05]} castShadow>
          <icosahedronGeometry args={[r, 0]} />
          <Flat color={i % 2 ? leaf : '#92ab75'} />
        </mesh>
      ))}
    </group>
  )
}

export function Cypress({
  position = [0, 0, 0],
  scale = 1,
  color = '#2f5a45',
}: Place & { color?: string }) {
  return (
    <group position={position} scale={scale}>
      <mesh position={[0, 0.2, 0]} castShadow>
        <cylinderGeometry args={[0.06, 0.09, 0.4, 5]} />
        <Flat color="#4a3a2e" />
      </mesh>
      <mesh position={[0, 1.35, 0]} scale={[0.55, 1.6, 0.55]} castShadow>
        <icosahedronGeometry args={[0.7, 0]} />
        <Flat color={color} />
      </mesh>
    </group>
  )
}

export function Shrub({
  position = [0, 0, 0],
  scale = 1,
  color = '#8a9a5b',
}: Place & { color?: string }) {
  return (
    <mesh
      position={[position[0], position[1] + 0.16 * scale, position[2]]}
      scale={scale}
      castShadow
    >
      <icosahedronGeometry args={[0.28, 0]} />
      <Flat color={color} />
    </mesh>
  )
}

/** A fluted-looking column. `broken` cuts it short and leaves a drum on the ground. */
export function Column({
  position = [0, 0, 0],
  height = 2.4,
  radius = 0.22,
  rotation = 0,
  color = '#e7dcc4',
  broken = false,
}: Place & { height?: number; radius?: number; color?: string; broken?: boolean }) {
  const shaft = broken ? height * 0.55 : height
  return (
    <group position={position} rotation={[0, rotation, 0]}>
      <mesh position={[0, 0.07, 0]} castShadow receiveShadow>
        <boxGeometry args={[radius * 2.9, 0.14, radius * 2.9]} />
        <Flat color={color} />
      </mesh>
      <mesh position={[0, 0.14 + shaft / 2, 0]} castShadow receiveShadow>
        <cylinderGeometry args={[radius * 0.86, radius, shaft, 10]} />
        <Flat color={color} />
      </mesh>
      {broken ? (
        <mesh
          position={[radius * 2.1, radius * 0.9, radius * 1.4]}
          rotation={[0.1, 0.5, Math.PI / 2 - 0.2]}
          castShadow
          receiveShadow
        >
          <cylinderGeometry args={[radius * 0.86, radius * 0.9, height * 0.3, 10]} />
          <Flat color={color} />
        </mesh>
      ) : (
        <mesh position={[0, 0.14 + shaft + 0.07, 0]} castShadow>
          <boxGeometry args={[radius * 2.7, 0.14, radius * 2.7]} />
          <Flat color={color} />
        </mesh>
      )}
    </group>
  )
}

/** A small temple: stepped base, two rows of columns, a beam and a triangular pediment. */
export function Temple({
  position = [0, 0, 0],
  rotation = 0,
  scale = 1,
  columns = 4,
  color = '#efe6d2',
  roof = '#c9694a',
  ruined = false,
}: Place & { columns?: number; color?: string; roof?: string; ruined?: boolean }) {
  const width = columns * 0.9
  const spots = Array.from({ length: columns }, (_, i) => -width / 2 + 0.45 + i * 0.9)
  return (
    <group position={position} rotation={[0, rotation, 0]} scale={scale}>
      <mesh position={[0, 0.1, 0]} receiveShadow castShadow>
        <boxGeometry args={[width + 0.9, 0.2, 2.6]} />
        <Flat color={color} />
      </mesh>
      <mesh position={[0, 0.28, 0]} receiveShadow castShadow>
        <boxGeometry args={[width + 0.5, 0.16, 2.2]} />
        <Flat color={color} />
      </mesh>
      {spots.flatMap((x, i) =>
        [-0.85, 0.85].map((z) => (
          <Column
            key={`${i}:${z}`}
            position={[x, 0.36, z]}
            height={1.9 - (ruined && (i + (z > 0 ? 1 : 0)) % 2 ? 0.8 : 0)}
            radius={0.17}
            color={color}
            broken={ruined && (i + (z > 0 ? 1 : 0)) % 3 === 0}
          />
        )),
      )}
      {!ruined && (
        <>
          <mesh position={[0, 2.5, 0]} castShadow>
            <boxGeometry args={[width + 0.3, 0.22, 2.2]} />
            <Flat color={color} />
          </mesh>
          <mesh
            position={[0, 2.99, 0]}
            rotation={[Math.PI / 2, 0, 0]}
            scale={[1, 1, 0.32]}
            castShadow
          >
            <cylinderGeometry args={[(width + 0.3) / 1.75, (width + 0.3) / 1.75, 2.1, 3]} />
            <Flat color={roof} />
          </mesh>
        </>
      )}
    </group>
  )
}

/** A clay amphora, turned on a lathe. */
export function Amphora({
  position = [0, 0, 0],
  scale = 1,
  rotation = 0,
  color = '#b8643e',
}: Place & { color?: string }) {
  const geometry = useMemo(
    () =>
      new LatheGeometry(
        [
          [0, 0],
          [0.12, 0.02],
          [0.2, 0.2],
          [0.22, 0.38],
          [0.14, 0.58],
          [0.08, 0.7],
          [0.11, 0.76],
          [0.0, 0.76],
        ].map(([x, y]) => new Vector2(x, y)),
        10,
      ),
    [],
  )
  return (
    <mesh
      position={position}
      rotation={[0, rotation, 0.12 * (scale > 1 ? 1 : 0)]}
      scale={scale}
      geometry={geometry}
      castShadow
    >
      <Flat color={color} />
    </mesh>
  )
}
