import { Line } from '@react-three/drei'

/** A real floor engraving: perspective and occlusion follow the camera and character. */
export function Platform() {
  const gold = '#9c8552'
  return (
    <group>
      <mesh position={[0, -0.08, 0]} receiveShadow>
        <cylinderGeometry args={[3.55, 3.9, 0.35, 64]} />
        <meshStandardMaterial color="#182b3b" roughness={0.65} metalness={0.15} />
      </mesh>
      <mesh position={[0, 0.16, 0]} receiveShadow>
        <cylinderGeometry args={[3.15, 3.4, 0.32, 64]} />
        <meshStandardMaterial color="#344352" roughness={0.48} metalness={0.18} />
      </mesh>
      {[2.48, 2.68, 2.96].map((radius) => (
        <mesh key={radius} position={[0, 0.325, 0]} rotation={[-Math.PI / 2, 0, 0]}>
          <ringGeometry args={[radius, radius + 0.012, 128]} />
          <meshStandardMaterial color={gold} emissive={gold} emissiveIntensity={0.12} />
        </mesh>
      ))}
      {Array.from({ length: 48 }, (_, i) => {
        const angle = (i / 48) * Math.PI * 2
        const radius = i % 4 === 0 ? 2.73 : 2.82
        return (
          <Line
            key={i}
            points={[
              [Math.cos(angle) * radius, 0.329, Math.sin(angle) * radius],
              [Math.cos(angle) * 2.92, 0.329, Math.sin(angle) * 2.92],
            ]}
            color={gold}
            lineWidth={0.7}
          />
        )
      })}
      {[0, Math.PI].map((offset) => (
        <Line
          key={offset}
          points={Array.from({ length: 4 }, (_, i) => {
            const angle = offset + (i / 3) * Math.PI * 2
            return [Math.sin(angle) * 2.43, 0.33, Math.cos(angle) * 2.43] as [
              number,
              number,
              number,
            ]
          })}
          color={gold}
          lineWidth={0.7}
        />
      ))}
    </group>
  )
}
