import { useMemo, useRef, type ReactNode } from 'react'
import { Sparkles } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import type { Group } from 'three'
import { useSceneMotion } from '../../../components/creature/useSceneMotion'
import { Clouds } from './Clouds'
import { MapCanvas } from './MapCanvas'
import { RoadLayer, type RoadTheme } from './RoadLayer'
import { Amphora, Column, Cypress, OliveTree, Rock, Shrub, Temple } from './props'
import { fbm, mix, seeded, smoothstep } from './noise'
import { distanceToPolyline, layRoad } from './road'
import { scatter, tint } from './scatter'
import { polarIsland } from './terrain'
import type { MapSceneProps } from './types'

const RADIUS = 10
const POOLS: { x: number; z: number; r: number }[] = [
  { x: -4.5, z: 0.3, r: 1.6 },
  { x: 4.4, z: 1.8, r: 1.4 },
  { x: 0.6, z: -3.6, r: 1.3 },
]
const ROAD: [number, number][] = [
  [-6, 5],
  [-3.5, 3.4],
  [-0.5, 4.2],
  [2, 2.4],
  [1.8, -0.6],
  [-1.2, -1.4],
  [-3.2, -2.6],
  [-2.5, -5.2],
  [1.8, -6],
  [5, -4],
]
const THEME: RoadTheme = { path: '#d9cdb0', edge: '#a39879', width: 0.9 }

function rim(angle: number) {
  return (
    1 +
    0.1 * Math.sin(3 * angle + 0.7) +
    0.06 * Math.sin(5 * angle + 2) +
    0.03 * Math.sin(9 * angle)
  )
}

function heightAt(x: number, z: number) {
  const hills = (fbm(x * 0.22 + 3, z * 0.22) - 0.45) * 2.4
  const away = smoothstep(0.8, 2.2, distanceToPolyline(ROAD, x, z)) // keep the road gentle
  let h = hills * (0.25 + 0.75 * away)
  for (const pool of POOLS) {
    const d = Math.hypot(x - pool.x, z - pool.z) / pool.r
    h = mix(h, 0, 1 - smoothstep(1, 2.2, d)) - 0.55 * (1 - smoothstep(0.5, 1.1, d))
  }
  return h
}

function Island() {
  const geometry = useMemo(
    () =>
      polarIsland({
        radius: RADIUS,
        rim,
        rings: 26,
        segments: 72,
        height: heightAt,
        topColor: (x, z, y, edge) => {
          const grass = tint('#5f8f35', '#98b84f', fbm(x * 0.3, z * 0.3) + y * 0.12)
          return edge > 0.93 ? tint('#8a6a3a', '#5f8f35', (1 - edge) * 14) : grass
        },
        rockColor: (depth, angle) =>
          tint('#76668a', '#b8906c', 1 - depth + 0.15 * Math.sin(angle * 7)),
        depth: 6.5,
        jag: (x, z) => fbm(x * 0.5, z * 0.5, 3) - 0.5,
      }),
    [],
  )
  return (
    <>
      <mesh geometry={geometry.top} receiveShadow castShadow>
        <meshStandardMaterial vertexColors flatShading roughness={0.95} />
      </mesh>
      <mesh geometry={geometry.bottom} castShadow>
        <meshStandardMaterial vertexColors flatShading roughness={0.9} />
      </mesh>
    </>
  )
}

function inside(x: number, z: number, margin = 1) {
  const angle = Math.atan2(z, x)
  return Math.hypot(x, z) < RADIUS * rim(angle) - margin
}

function roadFree(x: number, z: number, margin: number) {
  return distanceToPolyline(ROAD, x, z) > margin + THEME.width
}

function free(x: number, z: number, margin: number) {
  return (
    roadFree(x, z, margin) &&
    POOLS.every((p) => Math.hypot(x - p.x, z - p.z) > p.r * 1.3 + margin * 0.3) &&
    Math.hypot(x + 6, z + 5.5) > 3 // the temple's footprint
  )
}

const BOX = { x: [-RADIUS, RADIUS] as [number, number], z: [-RADIUS, RADIUS] as [number, number] }

function Scenery() {
  const olives = useMemo(
    () => scatter(11, 4, BOX, (x, z) => inside(x, z, 1.2) && free(x, z, 1.1)),
    [],
  )
  const cypress = useMemo(
    () =>
      scatter(10, 7, BOX, (x, z) => inside(x, z, 0.8) && free(x, z, 0.9) && Math.hypot(x, z) > 5.5),
    [],
  )
  const rocks = useMemo(
    () => scatter(14, 11, BOX, (x, z) => inside(x, z, 0.6) && free(x, z, 0.7)),
    [],
  )
  const shrubs = useMemo(
    () => scatter(26, 13, BOX, (x, z) => inside(x, z, 0.5) && free(x, z, 0.6)),
    [],
  )
  const flowers = useMemo(
    () => scatter(40, 17, BOX, (x, z) => inside(x, z, 0.5) && free(x, z, 0.5)),
    [],
  )
  const random = seeded(3)
  return (
    <group>
      {olives.map(([x, z], i) => (
        <OliveTree
          key={i}
          position={[x, heightAt(x, z), z]}
          scale={0.8 + random() * 0.6}
          rotation={random() * 6}
        />
      ))}
      {cypress.map(([x, z], i) => (
        <Cypress key={i} position={[x, heightAt(x, z), z]} scale={0.8 + random() * 0.8} />
      ))}
      {rocks.map(([x, z], i) => (
        <Rock
          key={i}
          position={[x, heightAt(x, z) - 0.05, z]}
          scale={0.5 + random() * 0.8}
          seed={i + 1}
        />
      ))}
      {shrubs.map(([x, z], i) => (
        <Shrub
          key={i}
          position={[x, heightAt(x, z), z]}
          scale={0.7 + random() * 0.9}
          color={i % 3 ? '#7d9a4a' : '#a7a85a'}
        />
      ))}
      {flowers.map(([x, z], i) => (
        <mesh key={i} position={[x, heightAt(x, z) + 0.12, z]}>
          <icosahedronGeometry args={[0.07 + random() * 0.04, 0]} />
          <meshStandardMaterial
            color={['#f4c542', '#f08a4b', '#e9e4f5', '#6aa6e8'][i % 4]}
            emissive={['#f4c542', '#f08a4b', '#e9e4f5', '#6aa6e8'][i % 4]}
            emissiveIntensity={0.25}
            flatShading
          />
        </mesh>
      ))}
      {POOLS.map((pool, i) => (
        <mesh key={i} position={[pool.x, -0.2, pool.z]} rotation={[-Math.PI / 2, 0, 0]}>
          <circleGeometry args={[pool.r * 1.05, 28]} />
          <meshStandardMaterial
            color="#3fc4c0"
            emissive="#1c8f93"
            emissiveIntensity={0.35}
            roughness={0.15}
            metalness={0.1}
          />
        </mesh>
      ))}
      <Temple position={[-6, heightAt(-6, -5.5), -5.5]} rotation={0.5} scale={0.62} columns={4} />
      <Amphora position={[-3.7, heightAt(-3.7, -6.8), -6.8]} scale={1.2} />
      <Amphora position={[-8.2, heightAt(-8.2, -3), -3]} scale={1} rotation={1} />
      <Column position={[6.6, heightAt(6.6, 4), 4]} height={2} broken rotation={0.4} />
      <Column position={[-7.4, heightAt(-7.4, 3.4), 3.4]} height={2.4} rotation={0.2} />
      <Pillar x={7.2} z={-3.2} height={3.2} />
      <Pillar x={-7.2} z={0.6} height={2.4} />
    </group>
  )
}

/** A rock pillar topped with an olive tree: the giant-mushroom beat of the reference, in Greek. */
function Pillar({ x, z, height }: { x: number; z: number; height: number }) {
  return (
    <group position={[x, heightAt(x, z), z]}>
      <mesh position={[0, height / 2, 0]} castShadow receiveShadow>
        <cylinderGeometry args={[0.8, 1.15, height, 7]} />
        <meshStandardMaterial color="#8a7f8c" flatShading roughness={0.95} />
      </mesh>
      <mesh position={[0, height + 0.05, 0]} castShadow>
        <cylinderGeometry args={[1.0, 0.85, 0.22, 7]} />
        <meshStandardMaterial color="#6f9a3a" flatShading />
      </mesh>
      <OliveTree position={[0, height + 0.1, 0]} scale={1.1} />
    </group>
  )
}

/** The whole isle bobs gently on the air. */
function Drift({ motion, children }: { motion: boolean; children: ReactNode }) {
  const group = useRef<Group>(null)
  useFrame(({ clock }) => {
    if (motion && group.current) group.current.position.y = Math.sin(clock.elapsedTime * 0.5) * 0.18
  })
  return <group ref={group}>{children}</group>
}

function FloatingRocks({ motion }: { motion: boolean }) {
  const group = useRef<Group>(null)
  const random = seeded(21)
  const rocks = useMemo(
    () =>
      Array.from({ length: 7 }, () => ({
        a: random() * 6.28,
        r: 11.5 + random() * 3,
        y: -2 + random() * 5,
        s: 0.25 + random() * 0.5,
      })),
    // oxlint-disable-next-line exhaustive-deps
    [],
  )
  useFrame(({ clock }) => {
    if (motion && group.current) group.current.rotation.y = clock.elapsedTime * 0.02
  })
  return (
    <group ref={group}>
      {rocks.map((rock, i) => (
        <mesh
          key={i}
          position={[Math.cos(rock.a) * rock.r, rock.y, Math.sin(rock.a) * rock.r]}
          scale={rock.s}
          rotation={[i, i * 2, 0]}
          castShadow
        >
          <dodecahedronGeometry args={[1, 0]} />
          <meshStandardMaterial color="#6e5f78" flatShading roughness={0.9} />
        </mesh>
      ))}
    </group>
  )
}

export default function IsleMap({ map, modelUrl, breedId, selected, onSelect }: MapSceneProps) {
  const motion = useSceneMotion()
  const road = useMemo(() => layRoad(ROAD, heightAt, map.nodes.length), [map.nodes.length])

  return (
    <MapCanvas
      motion={motion}
      camera={[0, 14, 27]}
      target={[0, -0.5, 0]}
      background="#0e2a2c"
      fog={['#0e2a2c', 36, 90]}
      distance={[9, 40]}
      maxPolar={Math.PI / 2 + 0.5} // the isle floats: let the camera go beneath it
      onMiss={() => onSelect(null)}
    >
      <hemisphereLight args={['#bfe3d6', '#2a2442', 1.1]} />
      <directionalLight
        position={[9, 14, 7]}
        color="#ffe2b0"
        intensity={3}
        castShadow
        shadow-mapSize={[2048, 2048]}
        shadow-camera-left={-13}
        shadow-camera-right={13}
        shadow-camera-top={13}
        shadow-camera-bottom={-13}
        shadow-camera-far={50}
        shadow-normalBias={0.05}
      />
      <directionalLight position={[-8, 4, -8]} color="#6fb8c8" intensity={1.2} />
      <directionalLight position={[2, -10, 6]} color="#a58cc8" intensity={1.4} />
      <Drift motion={motion}>
        <Island />
        <Scenery />
        <RoadLayer
          road={road}
          map={map}
          theme={THEME}
          selected={selected}
          onSelect={onSelect}
          modelUrl={modelUrl}
          breedId={breedId}
          motion={motion}
        />
        <FloatingRocks motion={motion} />
      </Drift>
      <Clouds motion={motion} />
      <Sparkles
        count={60}
        scale={[26, 14, 26]}
        size={3}
        speed={motion ? 0.25 : 0}
        color="#bff5e6"
        position={[0, 2, 0]}
      />
    </MapCanvas>
  )
}
