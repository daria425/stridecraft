import {
  Box3,
  Float32BufferAttribute,
  MathUtils,
  Mesh,
  Object3D,
  SkinnedMesh,
  Vector3,
} from 'three'

/** GPU morph for the unrigged Cetus: expand the ribcage, lift shoulders slightly, plant feet.
 * Work only on cloned geometry so cached GLBs and other instances stay untouched. */
export class CetusBreathing {
  meshes: Mesh[] = []

  constructor(scene: Object3D) {
    scene.updateMatrixWorld(true)
    const bounds = new Box3().setFromObject(scene)
    const size = bounds.getSize(new Vector3())
    if (Math.min(size.x, size.y, size.z) < 0.00001) return
    const center = bounds.getCenter(new Vector3())
    const torsoZ = bounds.min.z + size.z * 0.65
    const point = new Vector3()

    scene.traverse((mesh) => {
      if (
        !(mesh instanceof Mesh) ||
        mesh instanceof SkinnedMesh ||
        mesh.morphTargetInfluences?.length
      )
        return
      const geometry = mesh.geometry.clone()
      if (!geometry.hasAttribute('normal')) geometry.computeVertexNormals()
      const positions = geometry.getAttribute('position')
      const offsets = new Float32Array(positions.count * 3)
      const inverse = mesh.matrixWorld.clone().invert()

      for (let i = 0; i < positions.count; i++) {
        point.fromBufferAttribute(positions, i).applyMatrix4(mesh.matrixWorld)
        const height = (point.y - bounds.min.y) / size.y
        const chest =
          MathUtils.smoothstep(height, 0.3, 0.49) * (1 - MathUtils.smoothstep(height, 0.7, 0.84))
        const width = Math.exp(-Math.pow((point.x - center.x) / (size.x * 0.2), 4))
        const depth = Math.exp(-Math.pow((point.z - torsoZ) / (size.z * 0.36), 4))
        const weight = chest * width * depth
        point.x += (point.x - center.x) * 0.055 * weight
        point.z += (point.z - torsoZ) * 0.085 * weight
        point.y += size.y * 0.005 * weight
        point.applyMatrix4(inverse)
        offsets.set(
          [point.x - positions.getX(i), point.y - positions.getY(i), point.z - positions.getZ(i)],
          i * 3,
        )
      }

      // Generate matching normals once; only the morph weight changes on animation frames.
      const expanded = geometry.clone()
      expanded.computeVertexNormals()
      const restNormals = expanded.getAttribute('normal').clone()
      const expandedPositions = expanded.getAttribute('position')
      for (let i = 0; i < positions.count; i++) {
        expandedPositions.setXYZ(
          i,
          positions.getX(i) + offsets[i * 3],
          positions.getY(i) + offsets[i * 3 + 1],
          positions.getZ(i) + offsets[i * 3 + 2],
        )
      }
      expanded.computeVertexNormals()
      const expandedNormals = expanded.getAttribute('normal')
      const normalOffsets = new Float32Array(positions.count * 3)
      for (let i = 0; i < positions.count; i++) {
        normalOffsets.set(
          [
            expandedNormals.getX(i) - restNormals.getX(i),
            expandedNormals.getY(i) - restNormals.getY(i),
            expandedNormals.getZ(i) - restNormals.getZ(i),
          ],
          i * 3,
        )
      }
      expanded.dispose()
      geometry.morphTargetsRelative = true
      geometry.morphAttributes.position = [new Float32BufferAttribute(offsets, 3)]
      geometry.morphAttributes.normal = [new Float32BufferAttribute(normalOffsets, 3)]
      geometry.computeBoundingBox()
      geometry.computeBoundingSphere()
      mesh.geometry = geometry
      mesh.updateMorphTargets()
      mesh.name ||= 'Cetus'
      this.meshes.push(mesh)
    })
  }

  update(seconds: number, enabled: boolean) {
    // A relaxed 4.8-second cycle: gentle inhale, longer exhale, no whole-body scaling.
    const phase = (seconds / 4.8) % 1
    const breath = Math.pow(Math.sin(Math.PI * Math.pow(phase, 0.8)), 2)
    for (const mesh of this.meshes) {
      if (mesh.morphTargetInfluences) mesh.morphTargetInfluences[0] = enabled ? breath : 0
    }
  }

  dispose() {
    for (const mesh of this.meshes) mesh.geometry.dispose()
  }
}
