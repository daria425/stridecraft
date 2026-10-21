import { useEffect, useState } from 'react'

/** Stop continuous rendering in background tabs and respect changes to reduced motion. */
export function useSceneMotion() {
  const [active, setActive] = useState(() => !document.hidden)
  const [reduced, setReduced] = useState(
    () => window.matchMedia('(prefers-reduced-motion: reduce)').matches,
  )

  useEffect(() => {
    const media = window.matchMedia('(prefers-reduced-motion: reduce)')
    const visibility = () => setActive(!document.hidden)
    const preference = () => setReduced(media.matches)
    document.addEventListener('visibilitychange', visibility)
    media.addEventListener('change', preference)
    return () => {
      document.removeEventListener('visibilitychange', visibility)
      media.removeEventListener('change', preference)
    }
  }, [])

  return active && !reduced
}
