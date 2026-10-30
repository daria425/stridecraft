import { useEffect, type ReactNode } from 'react'
import { OrbitControls } from '@react-three/drei'
import { Canvas, useThree } from '@react-three/fiber'
import { ACESFilmicToneMapping, MOUSE, PCFShadowMap, PerspectiveCamera, TOUCH } from 'three'

/** Portrait screens need a wider lens to keep the whole road in view. */
function ResponsiveLens({ wide, narrow }: { wide: number; narrow: number }) {
  const { camera, size, invalidate } = useThree()
  useEffect(() => {
    if (!(camera instanceof PerspectiveCamera)) return
    // Three owns this mutable camera; changing projection is an imperative renderer operation.
    // oxlint-disable-next-line react/immutability
    camera.fov = size.width / size.height < 0.9 ? narrow : wide
    camera.updateProjectionMatrix()
    invalidate()
  }, [camera, size, wide, narrow, invalidate])
  return null
}

/** The canvas every map shares: bounded orbit camera, shadows, fog. A map adds its own lights
 * and scenery as children. Clicking empty space reports a miss so the selection can clear. */
export function MapCanvas({
  motion,
  camera,
  target,
  background,
  fog,
  distance,
  lens = [36, 52],
  maxPolar = Math.PI / 2 - 0.12,
  onMiss,
  children,
}: {
  motion: boolean
  camera: [number, number, number]
  target: [number, number, number]
  background: string
  fog: [string, number, number]
  distance: [number, number]
  lens?: [number, number]
  maxPolar?: number // how far below the horizon the camera may go; 'up to' the ground by default
  onMiss: () => void
  children: ReactNode
}) {
  return (
    <Canvas
      shadows={{ type: PCFShadowMap }}
      dpr={[1, 1.5]}
      frameloop={motion ? 'always' : 'demand'}
      camera={{ fov: lens[0], near: 0.1, far: 200, position: camera }}
      gl={{ antialias: true, alpha: false, toneMapping: ACESFilmicToneMapping }}
      onPointerMissed={onMiss}
      fallback={
        <span className="creature-slot__note">3D preview is unavailable on this device.</span>
      }
    >
      <ResponsiveLens wide={lens[0]} narrow={lens[1]} />
      <OrbitControls
        makeDefault
        target={target}
        enablePan={false}
        enableDamping={motion}
        dampingFactor={0.08}
        rotateSpeed={0.6}
        zoomSpeed={0.8}
        minDistance={distance[0]}
        maxDistance={distance[1]}
        minPolarAngle={0.35}
        maxPolarAngle={maxPolar}
        mouseButtons={{ LEFT: MOUSE.ROTATE, MIDDLE: MOUSE.DOLLY, RIGHT: MOUSE.ROTATE }}
        touches={{ ONE: TOUCH.ROTATE, TWO: TOUCH.DOLLY_ROTATE }}
      />
      <color attach="background" args={[background]} />
      <fog attach="fog" args={fog} />
      {children}
    </Canvas>
  )
}
