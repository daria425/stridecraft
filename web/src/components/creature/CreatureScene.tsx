import { Suspense, useCallback, useEffect, useState } from 'react'
import { Canvas, useThree } from '@react-three/fiber'
import { ACESFilmicToneMapping, PCFShadowMap, PerspectiveCamera } from 'three'
import { CreatureModel } from './CreatureModel'
import { Platform } from './Platform'
import { Sanctuary } from './Sanctuary'
import { SceneBoundary } from './SceneBoundary'
import { useSceneMotion } from './useSceneMotion'
import type { EnvironmentId } from './environments'

function CameraFraming({ stage }: { stage: boolean }) {
  const { camera, size, invalidate } = useThree()
  useEffect(() => {
    if (!(camera instanceof PerspectiveCamera)) return
    const desktop = stage && size.width >= 992
    camera.position.set(7, 5.2, 11)
    camera.lookAt(0, 1.5, 0)
    // Three owns this mutable camera; changing projection is an imperative renderer operation.
    // oxlint-disable-next-line react/immutability
    camera.fov = stage && size.width < 600 ? 48 : 38
    // Move the composition clear of the desktop's 22rem panel column.
    camera.setViewOffset(
      size.width,
      size.height,
      desktop ? size.width * 0.12 : 0,
      0,
      size.width,
      size.height,
    )
    camera.updateProjectionMatrix()
    invalidate()
    return () => camera.clearViewOffset()
  }, [camera, size, stage, invalidate])
  return null
}

export default function CreatureScene({
  modelUrl,
  stage,
  environment,
}: {
  modelUrl: string | null
  stage: boolean
  environment: EnvironmentId
}) {
  const motion = useSceneMotion()
  const [status, setStatus] = useState(modelUrl ? 'loading' : 'missing')
  const ready = useCallback(() => setStatus('ready'), [])
  const failed = useCallback(() => setStatus('error'), [])
  const note =
    status === 'loading'
      ? 'Summoning…'
      : status === 'error'
        ? 'The model could not be loaded.'
        : status === 'missing'
          ? 'Awaiting your strider’s model'
          : null
  return (
    <>
      <Canvas
        shadows={{ type: PCFShadowMap }}
        dpr={[1, 1.5]}
        frameloop={motion ? 'always' : 'demand'}
        camera={{ fov: 38, near: 0.1, far: 100, position: [7, 5.2, 11] }}
        gl={{ antialias: true, alpha: false, toneMapping: ACESFilmicToneMapping }}
        fallback={
          <span className="creature-slot__note">3D preview is unavailable on this device.</span>
        }
      >
        <CameraFraming stage={stage} />
        <color attach="background" args={['#0b172b']} />
        <fog attach="fog" args={['#0b172b', 12, 38]} />
        <hemisphereLight args={['#99bad5', '#111526', 1.3]} />
        <directionalLight
          position={[-4, 9, 4]}
          color="#c5dcec"
          intensity={2.6}
          castShadow
          shadow-mapSize={[1024, 1024]}
          shadow-camera-left={-7}
          shadow-camera-right={7}
          shadow-camera-top={7}
          shadow-camera-bottom={-7}
          shadow-camera-far={30}
          shadow-normalBias={0.04}
        />
        <directionalLight position={[3, 5, -5]} color="#6a9fc2" intensity={3} />
        <pointLight position={[-2, 1.5, 3]} color="#e0bb77" intensity={7} distance={8} />
        {environment === 'sanctuary' && <Sanctuary motion={motion} />}
        <Platform />
        {modelUrl ? (
          <SceneBoundary key={modelUrl} fallback={null} onError={failed}>
            <Suspense fallback={null}>
              <CreatureModel url={modelUrl} motion={motion} onReady={ready} />
            </Suspense>
          </SceneBoundary>
        ) : null}
      </Canvas>
      {note && (
        <span className="creature-slot__note creature-slot__note--overlay" role="status">
          {note}
        </span>
      )}
    </>
  )
}
