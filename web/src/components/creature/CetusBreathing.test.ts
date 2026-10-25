import { describe, expect, it } from 'vitest'
import { BoxGeometry, Group, Mesh, MeshStandardMaterial, SkinnedMesh } from 'three'
import { CetusBreathing } from './CetusBreathing'

describe('Cetus breathing', () => {
  it('moves the ribcage while planting the feet and preserving cached geometry', () => {
    const geometry = new BoxGeometry(2, 4, 2, 8, 16, 8)
    const mesh = new Mesh(geometry, new MeshStandardMaterial())
    const scene = new Group()
    scene.add(mesh)
    const breathing = new CetusBreathing(scene)
    const positions = mesh.geometry.getAttribute('position')
    const offsets = mesh.geometry.morphAttributes.position[0]
    let movingChestVertices = 0
    for (let i = 0; i < positions.count; i++) {
      if (positions.getY(i) < -1 || positions.getY(i) > 1.5) {
        expect(offsets.getX(i)).toBeCloseTo(0)
        expect(offsets.getY(i)).toBeCloseTo(0)
        expect(offsets.getZ(i)).toBeCloseTo(0)
      }
      if (Math.abs(offsets.getZ(i)) > 0.00001) movingChestVertices++
    }
    expect(movingChestVertices).toBeGreaterThan(0)
    expect(mesh.geometry).not.toBe(geometry)
    expect(geometry.morphAttributes.position).toBeUndefined()
    breathing.update(1.6, true)
    expect(mesh.morphTargetInfluences?.[0]).toBeGreaterThan(0.5)
    breathing.update(1.6, false)
    expect(mesh.morphTargetInfluences?.[0]).toBe(0)
    breathing.dispose()
    geometry.dispose()
  })

  it('leaves skinned meshes and existing morph animation alone', () => {
    const geometry = new BoxGeometry(2, 4, 2)
    const skinned = new SkinnedMesh(geometry)
    geometry.computeBoundingBox()
    skinned.boundingBox = geometry.boundingBox!.clone()
    const existing = new Mesh(geometry)
    existing.morphTargetInfluences = [0.4]
    const scene = new Group()
    scene.add(skinned, existing)
    const breathing = new CetusBreathing(scene)
    breathing.update(2, true)
    expect(breathing.meshes).toHaveLength(0)
    expect(skinned.geometry).toBe(geometry)
    expect(existing.morphTargetInfluences).toEqual([0.4])
    geometry.dispose()
  })
})
