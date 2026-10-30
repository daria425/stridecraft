import { useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import type { Group } from 'three'
import { seeded } from './noise'

type Bank = {
  radius: number // distance from the isle's centre
  angle: number
  height: number
  size: number
  speed: number // radians per second around the isle
  puffs: [number, number, number, number][] // x, y, z, radius within the bank
}

/** Where the banks of cloud sit. Low, wide banks form a sea beneath the isle; smaller ones drift
 * around its rim. All stay below the camera's line of sight to the island. */
function layout(): Bank[] {
  const random = seeded(8)
  const banks: Bank[] = []
  const add = (
    count: number,
    radius: [number, number],
    height: [number, number],
    size: [number, number],
  ) => {
    for (let i = 0; i < count; i++) {
      const puffCount = 4 + Math.floor(random() * 3)
      banks.push({
        radius: radius[0] + random() * (radius[1] - radius[0]),
        angle: random() * Math.PI * 2,
        height: height[0] + random() * (height[1] - height[0]),
        size: size[0] + random() * (size[1] - size[0]),
        speed: (0.012 + random() * 0.018) * (random() < 0.5 ? 1 : -1),
        puffs: Array.from({ length: puffCount }, (_, p) => [
          (p - puffCount / 2) * 0.9 + random() * 0.4,
          random() * 0.5,
          (random() - 0.5) * 1.2,
          0.7 + random() * 0.6,
        ]),
      })
    }
  }
  add(10, [3, 22], [-15, -11], [1.2, 1.9]) // the sea of cloud beneath
  add(8, [14, 24], [-5, 0], [0.7, 1.2]) // banks drifting past the rim
  add(4, [22, 30], [3, 7], [1, 1.5]) // a few far off, higher
  return banks
}

function Bank({ bank, motion }: { bank: Bank; motion: boolean }) {
  const group = useRef<Group>(null)
  const angle = useRef(bank.angle)
  useFrame(({ clock }, delta) => {
    if (!group.current) return
    if (motion) angle.current += Math.min(delta, 0.05) * bank.speed
    group.current.position.set(
      Math.cos(angle.current) * bank.radius,
      bank.height + (motion ? Math.sin(clock.elapsedTime * 0.3 + bank.angle) * 0.25 : 0),
      Math.sin(angle.current) * bank.radius,
    )
    group.current.rotation.y = -angle.current // keep the long axis along the drift
  })
  return (
    <group ref={group} scale={bank.size}>
      {bank.puffs.map(([x, y, z, r], i) => (
        <mesh key={i} position={[x, y, z]} scale={[1.5, 0.8, 1.1]}>
          <icosahedronGeometry args={[r, 1]} />
          <meshStandardMaterial
            color="#f4fbff"
            emissive="#9fc3cc"
            emissiveIntensity={0.3}
            roughness={1}
            flatShading
            transparent
            opacity={0.93}
          />
        </mesh>
      ))}
    </group>
  )
}

/** Slow, flat-shaded clouds around and beneath the floating isle. */
export function Clouds({ motion }: { motion: boolean }) {
  const banks = useMemo(() => layout(), [])
  return (
    <group>
      {banks.map((bank, i) => (
        <Bank key={i} bank={bank} motion={motion} />
      ))}
    </group>
  )
}
