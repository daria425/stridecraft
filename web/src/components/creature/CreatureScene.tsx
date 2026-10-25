import { Suspense, useCallback, useEffect, useRef, useState, type ComponentRef } from 'react'
import { OrbitControls } from '@react-three/drei'
import { Canvas, useThree } from '@react-three/fiber'
import { ACESFilmicToneMapping, MOUSE, PCFShadowMap, PerspectiveCamera, TOUCH } from 'three'
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
  breedId,
}: {
  modelUrl: string | null
  stage: boolean
  environment: EnvironmentId
  breedId?: string
}) {
  const motion = useSceneMotion()
  const controls = useRef<ComponentRef<typeof OrbitControls>>(null)
  const resetView = () => {
    const orbit = controls.current
    if (!orbit) return
    // Drain residual orbit momentum before restoring the authored view.
    const damping = orbit.enableDamping
    orbit.enableDamping = false
    orbit.update()
    orbit.object.position.set(7, 5.2, 11)
    orbit.target.set(0, 1.5, 0)
    orbit.update()
    orbit.enableDamping = damping
  }
  const zoom = (factor: number) => {
    const orbit = controls.current
    if (!orbit) return
    orbit.object.position.sub(orbit.target).multiplyScalar(factor).add(orbit.target)
    orbit.update()
  }
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
        <OrbitControls
          ref={controls}
          makeDefault
          target={[0, 1.5, 0]}
          enablePan={false}
          enableDamping={motion}
          dampingFactor={0.08}
          rotateSpeed={0.65}
          zoomSpeed={0.8}
          minDistance={5.5}
          maxDistance={22}
          minPolarAngle={0.25}
          maxPolarAngle={Math.PI / 2 - 0.08}
          mouseButtons={{ LEFT: MOUSE.ROTATE, MIDDLE: MOUSE.DOLLY, RIGHT: MOUSE.ROTATE }}
          touches={{ ONE: TOUCH.ROTATE, TWO: TOUCH.DOLLY_ROTATE }}
        />
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
              <CreatureModel
                url={modelUrl}
                motion={motion}
                onReady={ready}
                breathing={breedId === 'cetus'}
              />
            </Suspense>
          </SceneBoundary>
        ) : null}
      </Canvas>
      {stage && (
        <div className="creature-slot__camera" role="group" aria-label="Camera controls">
          <span className="creature-slot__camera-hint">
            Drag to orbit · Scroll or pinch to zoom
          </span>
          <button type="button" aria-label="Zoom in" onClick={() => zoom(0.85)}>
            +
          </button>
          <button type="button" aria-label="Zoom out" onClick={() => zoom(1.18)}>
            −
          </button>
          <button type="button" onClick={resetView}>
            Reset view
          </button>
        </div>
      )}
      {note && (
        <span className="creature-slot__note creature-slot__note--overlay" role="status">
          {note}
        </span>
      )}
    </>
  )
}
