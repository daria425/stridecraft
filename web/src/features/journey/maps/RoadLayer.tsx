import { Suspense, useCallback, useMemo, useRef, useState } from 'react'
import { Html } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { type Group, type Mesh, type Vector3 } from 'three'
import { CreatureModel } from '../../../components/creature/CreatureModel'
import { SceneBoundary } from '../../../components/creature/SceneBoundary'
import type { LegMap, MapNode } from '../legMap'
import { ribbon, type Road } from './road'

/** How a map dresses its road. */
export type RoadTheme = {
  path: string // the stone or sand of the road itself
  edge: string // a slightly darker kerb
  width: number
}

const GOLD = '#f0c85a'
const ARRIVING = '#9fe8ff'
const DIM = '#5d6070'

function gemColor(state: MapNode['state']) {
  return state === 'done' ? GOLD : state === 'ahead' ? DIM : ARRIVING
}

function Waypoint({
  node,
  at,
  selected,
  kmToGo,
  onSelect,
  motion,
}: {
  node: MapNode
  at: Vector3
  selected: boolean
  kmToGo: number
  onSelect: () => void
  motion: boolean
}) {
  const gem = useRef<Mesh>(null)
  const ring = useRef<Mesh>(null)
  const [hovered, setHovered] = useState(false)
  const lively = node.state === 'arriving' || node.state === 'next'
  const color = gemColor(node.state)
  const big = node.isLandmark ? 2 : 1.35

  useFrame(({ clock }) => {
    const t = clock.elapsedTime
    if (gem.current) {
      gem.current.rotation.y = motion ? t * 1.2 : 0
      gem.current.position.y =
        (node.isLandmark ? 1.85 : 0.95) + (motion ? Math.sin(t * 2) * 0.06 : 0)
    }
    if (ring.current && lively) {
      const pulse = motion ? 1 + 0.18 * Math.sin(t * 3) : 1
      ring.current.scale.setScalar(pulse)
    }
  })

  const showLabel = hovered || selected || node.isLandmark || node.state === 'next'
  const label =
    node.state === 'next' && !node.isLandmark
      ? `${kmToGo.toFixed(1)} km to go`
      : node.state === 'arriving'
        ? 'Something is here…'
        : node.label || `Stop ${node.index}`

  return (
    <group
      position={at}
      onClick={(e) => {
        e.stopPropagation()
        onSelect()
      }}
      onPointerOver={(e) => {
        e.stopPropagation()
        setHovered(true)
        document.body.style.cursor = 'pointer'
      }}
      onPointerOut={() => {
        setHovered(false)
        document.body.style.cursor = ''
      }}
    >
      <mesh position={[0, 0.03, 0]} rotation={[-Math.PI / 2, 0, 0]} ref={ring}>
        <ringGeometry args={[0.55 * big, 0.68 * big, 32]} />
        <meshBasicMaterial
          color={selected ? '#ffffff' : color}
          transparent
          opacity={lively || selected ? 0.9 : 0.35}
        />
      </mesh>
      {node.isLandmark ? (
        <group scale={big}>
          {[-0.45, 0.45].map((x) => (
            <mesh key={x} position={[x, 0.55, 0]} castShadow>
              <cylinderGeometry args={[0.1, 0.13, 1.1, 8]} />
              <meshStandardMaterial color="#e7dcc4" flatShading />
            </mesh>
          ))}
          <mesh position={[0, 1.2, 0]} castShadow>
            <boxGeometry args={[1.25, 0.16, 0.3]} />
            <meshStandardMaterial color="#e7dcc4" flatShading />
          </mesh>
        </group>
      ) : (
        <group>
          {[0.34, 0.26, 0.19].map((r, i) => (
            <mesh
              key={i}
              position={[(i - 1) * 0.03, 0.1 + i * 0.15, 0]}
              scale={[1, 0.55, 1]}
              castShadow
            >
              <dodecahedronGeometry args={[r, 0]} />
              <meshStandardMaterial color="#8d8794" flatShading roughness={0.9} />
            </mesh>
          ))}
        </group>
      )}
      <mesh ref={gem} position={[0, 0.95, 0]} scale={big}>
        <octahedronGeometry args={[0.2, 0]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={node.state === 'ahead' ? 0.1 : 1.4}
          flatShading
        />
      </mesh>
      {node.state !== 'ahead' && (
        <pointLight
          position={[0, 1.2, 0]}
          color={color}
          intensity={node.state === 'done' ? 1.2 : 3}
          distance={4}
        />
      )}
      {showLabel && (
        <Html
          position={[0, node.isLandmark ? 2.6 : 1.6, 0]}
          center
          zIndexRange={[5, 0]}
          style={{ pointerEvents: 'none' }}
        >
          <span
            className={`map-label map-label--${node.state}${node.isLandmark ? ' map-label--landmark' : ''}`}
          >
            {label}
          </span>
        </Html>
      )}
    </group>
  )
}

/** Which way the creature models face when the road runs along +z; 0 until asset review says
 * otherwise. */
const MODEL_FORWARD_OFFSET = 0
const WALK_SPEED = 0.07 // fraction of the road per second

/** The strider on the road. When the stop it stands at changes it walks there along the road. */
function Strider({
  road,
  stop,
  modelUrl,
  breedId,
  motion,
}: {
  road: Road
  stop: number
  modelUrl: string | null
  breedId?: string
  motion: boolean
}) {
  const group = useRef<Group>(null)
  const current = useRef<number | null>(null)
  const target = road.nodeT[stop]
  const ready = useCallback(() => {}, [])

  useFrame((state, delta) => {
    if (!group.current) return
    const from = current.current ?? target
    const step = Math.min(delta, 0.05) * WALK_SPEED
    const moving = Math.abs(target - from) > 0.0005
    const next =
      !motion || !moving
        ? target
        : from + Math.sign(target - from) * Math.min(step, Math.abs(target - from))
    current.current = next
    const point = road.curve.getPointAt(Math.min(1, Math.max(0, next)))
    const hop = moving && motion ? Math.abs(Math.sin(state.clock.elapsedTime * 7)) * 0.12 : 0
    group.current.position.set(point.x, point.y + hop, point.z)
    if (moving) {
      const tangent = road.curve.getTangentAt(Math.min(1, Math.max(0, next)))
      group.current.rotation.y = Math.atan2(tangent.x, tangent.z) + MODEL_FORWARD_OFFSET
      state.invalidate()
    }
  })

  return (
    <group ref={group}>
      {modelUrl ? (
        <SceneBoundary key={modelUrl} fallback={<Totem />}>
          <Suspense fallback={<Totem />}>
            <group scale={0.4}>
              <CreatureModel
                url={modelUrl}
                motion={motion}
                onReady={ready}
                breathing={breedId === 'cetus'}
              />
            </group>
          </Suspense>
        </SceneBoundary>
      ) : (
        <Totem />
      )}
    </group>
  )
}

/** Stands in for the strider while its model loads, or when it has none. */
function Totem() {
  return (
    <mesh position={[0, 0.5, 0]} castShadow>
      <octahedronGeometry args={[0.32, 0]} />
      <meshStandardMaterial color={GOLD} emissive={GOLD} emissiveIntensity={0.6} flatShading />
    </mesh>
  )
}

/** The road, its lit trail, every stop and the strider, laid on whatever ground the map made. */
export function RoadLayer({
  road,
  map,
  theme,
  selected,
  onSelect,
  modelUrl,
  breedId,
  motion,
}: {
  road: Road
  map: LegMap
  theme: RoadTheme
  selected: number | null
  onSelect: (index: number | null) => void
  modelUrl: string | null
  breedId?: string
  motion: boolean
}) {
  const edge = useMemo(
    () => ribbon(road.curve, 0, 1, theme.width * 1.25, 0.04),
    [road, theme.width],
  )
  const bed = useMemo(() => ribbon(road.curve, 0, 1, theme.width, 0.07), [road, theme.width])
  const trailEnd = road.nodeT[map.position]
  const trail = useMemo(
    () => (trailEnd > 0.001 ? ribbon(road.curve, 0, trailEnd, theme.width * 0.34, 0.1) : null),
    [road, trailEnd, theme.width],
  )
  return (
    <group>
      <mesh geometry={edge} receiveShadow>
        <meshStandardMaterial
          color={theme.edge}
          roughness={1}
          polygonOffset
          polygonOffsetFactor={-1}
        />
      </mesh>
      <mesh geometry={bed} receiveShadow>
        <meshStandardMaterial
          color={theme.path}
          roughness={0.95}
          polygonOffset
          polygonOffsetFactor={-2}
        />
      </mesh>
      {trail && (
        <mesh geometry={trail}>
          <meshStandardMaterial
            color={GOLD}
            emissive={GOLD}
            emissiveIntensity={0.9}
            polygonOffset
            polygonOffsetFactor={-3}
          />
        </mesh>
      )}
      {map.nodes.map((node) => (
        <Waypoint
          key={node.index}
          node={node}
          at={road.nodes[node.index]}
          selected={selected === node.index}
          kmToGo={map.kmToGo}
          onSelect={() => onSelect(node.index)}
          motion={motion}
        />
      ))}
      <Strider
        road={road}
        stop={map.position}
        modelUrl={modelUrl}
        breedId={breedId}
        motion={motion}
      />
    </group>
  )
}
