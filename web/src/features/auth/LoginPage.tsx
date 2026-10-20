import { useSearchParams } from 'react-router'
import { API_URL } from '../../api/client'
import { Banner } from '../../components/Banner'
import { SigilRing } from '../../components/SigilRing'
import '../../components/scene.css'
import './login.css'

const MESSAGES: Record<string, string> = {
  denied: 'Strava login was cancelled. You need to log in to play.',
  scope: 'Stridecraft needs permission to read your activities. Please allow it and try again.',
}

export function LoginPage() {
  const [params] = useSearchParams()
  const error = params.get('error')
  return (
    <main className="scene login">
      <section className="login__banner">
        <Banner
          level={1}
          title="Stridecraft"
          subtitle="Turn your runs into a creature that trains with you."
        />
      </section>
      <div className="login__seal">
        <SigilRing />
        {/* A browser navigation, not a fetch: Strava's login page takes over the tab. */}
        <a className="primary login__cta" href={`${API_URL}/auth/strava/login`}>
          Log in with Strava
        </a>
      </div>
      {error && (
        <p role="alert" className="login__error">
          {MESSAGES[error] ?? 'Login failed. Please try again.'}
        </p>
      )}
    </main>
  )
}
