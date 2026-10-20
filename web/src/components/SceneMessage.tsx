import '../components/scene.css'

/** A full-screen status line (loading, error, empty) in the scene's world. */
export function SceneMessage({ children }: { children: string }) {
  return (
    <main className="scene scene--message">
      <p>{children}</p>
    </main>
  )
}
