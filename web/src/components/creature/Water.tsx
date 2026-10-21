import { useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { Color, type ShaderMaterial } from 'three'

// Stylised moonlit water, without a reflection render pass or external texture downloads.
// World coordinates keep ripples fixed to the sanctuary when the viewport changes.
const vertexShader = `
  varying vec3 vWorld;
  void main() {
    vec4 world = modelMatrix * vec4(position, 1.0);
    vWorld = world.xyz;
    gl_Position = projectionMatrix * viewMatrix * world;
  }
`

const fragmentShader = `
  uniform float time;
  uniform vec3 deep;
  uniform vec3 crest;
  varying vec3 vWorld;

  void main() {
    vec2 p = vWorld.xz;
    float swell = sin(p.x * 2.7 + p.y * 1.8 + time * 0.35);
    float detail = sin(p.x * 7.0 - p.y * 4.5 - time * 0.5);
    float glint = pow(max(0.0, swell * 0.6 + detail * 0.4), 12.0);
    float moonPath = exp(-pow((p.x + p.y * 0.23 + 1.0) * 0.38, 2.0));
    float distanceToDais = length(p);
    float rings = pow(0.5 + 0.5 * sin(distanceToDais * 18.0 - time * 0.65), 18.0);
    rings *= exp(-abs(distanceToDais - 3.5) * 1.5);
    vec3 colour = deep + crest * (glint * moonPath * 0.65 + rings * 0.16);
    float mist = smoothstep(10.0, 38.0, length(p));
    colour = mix(colour, deep * 1.25, mist);
    gl_FragColor = vec4(colour, 1.0);
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
  }
`

export function Water({ motion }: { motion: boolean }) {
  const material = useRef<ShaderMaterial>(null)
  const uniforms = useMemo(
    () => ({
      time: { value: 0 },
      deep: { value: new Color('#091c2c') },
      crest: { value: new Color('#709baf') },
    }),
    [],
  )
  useFrame((_, delta) => {
    if (motion && material.current) material.current.uniforms.time.value += Math.min(delta, 0.05)
  })
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.1, 0]}>
      <planeGeometry args={[160, 160]} />
      <shaderMaterial
        ref={material}
        uniforms={uniforms}
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
      />
    </mesh>
  )
}
