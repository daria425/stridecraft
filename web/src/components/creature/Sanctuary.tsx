import { Water } from './Water'

function Column({
  x,
  z,
  height,
  lean = 0,
}: {
  x: number
  z: number
  height: number
  lean?: number
}) {
  return (
    <group position={[x, -0.15, z]} rotation={[0, 0, lean]}>
      <mesh position={[0, 0.18, 0]} receiveShadow>
        <boxGeometry args={[1.3, 0.4, 1.3]} />
        <meshStandardMaterial color="#263e4b" roughness={0.85} />
      </mesh>
      <mesh position={[0, height / 2 + 0.35, 0]} castShadow receiveShadow>
        <cylinderGeometry args={[0.39, 0.51, height, 12]} />
        <meshStandardMaterial color="#354955" roughness={0.78} flatShading />
      </mesh>
      <mesh position={[0, height + 0.45, 0]} castShadow>
        <boxGeometry args={[1.18, 0.25, 1.18]} />
        <meshStandardMaterial color="#415663" roughness={0.7} />
      </mesh>
    </group>
  )
}

/** Self-contained habitat. No creature-specific logic or model loading belongs here. */
export function Sanctuary({ motion }: { motion: boolean }) {
  return (
    <group>
      <Water motion={motion} />
      <Column x={-5.5} z={-3} height={6.5} lean={0.04} />
      <Column x={4.8} z={-4} height={5.8} lean={-0.06} />
      <Column x={-3.4} z={-7} height={4.5} />
      <Column x={3.3} z={-8.5} height={7} />
      <Column x={-7.5} z={-10} height={8} />
      <Column x={7.5} z={-13} height={6.2} />
      <Column x={-5} z={5} height={2.2} lean={0.18} />
      <mesh position={[-4.4, 6.9, -3]} rotation={[0, 0.12, -0.08]} castShadow>
        <boxGeometry args={[4, 0.55, 1.05]} />
        <meshStandardMaterial color="#2e4352" roughness={0.78} />
      </mesh>
      {Array.from({ length: 9 }, (_, i) => (
        <mesh
          key={i}
          position={[Math.sin(i * 4.3) * 7, -0.03, -3.5 - i * 1.1]}
          rotation={[i * 0.7, i * 1.3, 0.4]}
          scale={[0.7 + (i % 3) * 0.25, 0.35, 0.8]}
          receiveShadow
        >
          <dodecahedronGeometry args={[1, 0]} />
          <meshStandardMaterial color="#253b49" roughness={0.85} flatShading />
        </mesh>
      ))}
    </group>
  )
}
