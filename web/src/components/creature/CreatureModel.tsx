import { useEffect, useMemo, useRef } from 'react'
import { useFrame, useLoader } from '@react-three/fiber'
import { AnimationMixer, Box3, Mesh, Vector3 } from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { clone } from 'three/addons/utils/SkeletonUtils.js'
import { CetusBreathing } from './CetusBreathing'

/** Clone the skeleton, preserve authored materials, and never dispose cached GLTF resources.
 * Scale a wrapper, not the imported root: animation tracks may target the root transform. */
export function CreatureModel({
  url,
  motion,
  onReady,
  breathing = false,
}: {
  url: string
  motion: boolean
  onReady: () => void
  breathing?: boolean
}) {
  const gltf = useLoader(GLTFLoader, url)
  const idle = gltf.animations.find((clip) => /idle|breath|rest/i.test(clip.name))
  const model = useMemo(() => {
    const scene = clone(gltf.scene)
    scene.traverse((object) => {
      if (object instanceof Mesh) {
        object.castShadow = true
        object.receiveShadow = true
      }
    })
    const box = new Box3().setFromObject(scene)
    const size = box.getSize(new Vector3())
    // Long tails must fit the platform too. Per-model framing can replace this after asset review.
    const scale = Math.min(3.5 / Math.max(size.y, 0.001), 5.4 / Math.max(size.x, size.z, 0.001))
    const center = box.getCenter(new Vector3())
    const lungs = breathing && !idle ? new CetusBreathing(scene) : null
    return { scene, scale, lungs, offset: new Vector3(-center.x, -box.min.y, -center.z) }
  }, [gltf, breathing, idle])
  const mixer = useMemo(() => new AnimationMixer(model.scene), [model])
  const lungs = model.lungs
  const elapsed = useRef(0)

  useEffect(() => () => lungs?.dispose(), [lungs])
  useEffect(() => lungs?.update(elapsed.current, motion), [lungs, motion])

  useEffect(onReady, [onReady])

  useEffect(() => {
    // Do not accidentally play an attack/walk just because it is the first exported clip.
    if (!idle) return
    const action = mixer.clipAction(idle)
    action.play()
    return () => {
      mixer.stopAllAction()
      mixer.uncacheRoot(model.scene)
    }
  }, [idle, mixer, model])

  useFrame((_, delta) => {
    if (!motion) return
    const step = Math.min(delta, 0.1)
    mixer.update(step)
    elapsed.current += step
    lungs?.update(elapsed.current, true)
  })

  return (
    <group position={[0, 0.33, 0]} scale={model.scale}>
      <group position={model.offset}>
        <primitive object={model.scene} dispose={null} />
      </group>
    </group>
  )
}
