import { useEffect, useMemo } from 'react'
import { useFrame, useLoader } from '@react-three/fiber'
import { AnimationMixer, Box3, Mesh, Vector3 } from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { clone } from 'three/addons/utils/SkeletonUtils.js'

/** Clone the skeleton, preserve authored materials, and never dispose cached GLTF resources.
 * Scale a wrapper, not the imported root: animation tracks may target the root transform. */
export function CreatureModel({
  url,
  motion,
  onReady,
}: {
  url: string
  motion: boolean
  onReady: () => void
}) {
  const gltf = useLoader(GLTFLoader, url)
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
    return { scene, scale, offset: new Vector3(-center.x, -box.min.y, -center.z) }
  }, [gltf])
  const mixer = useMemo(() => new AnimationMixer(model.scene), [model])

  useEffect(onReady, [onReady])

  useEffect(() => {
    // Do not accidentally play an attack/walk just because it is the first exported clip.
    const idle = gltf.animations.find((clip) => /idle|breath|rest/i.test(clip.name))
    if (!idle) return
    const action = mixer.clipAction(idle)
    action.play()
    return () => {
      mixer.stopAllAction()
      mixer.uncacheRoot(model.scene)
    }
  }, [gltf, mixer, model])

  useFrame((_, delta) => {
    if (motion) mixer.update(Math.min(delta, 0.05))
  })

  return (
    <group position={[0, 0.33, 0]} scale={model.scale}>
      <group position={model.offset}>
        <primitive object={model.scene} dispose={null} />
      </group>
    </group>
  )
}
