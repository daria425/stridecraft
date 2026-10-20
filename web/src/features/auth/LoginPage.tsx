import { useSearchParams } from 'react-router'
import { API_URL } from '../../api/client'

const MESSAGES: Record<string, string> = {
  denied: 'Strava login was cancelled. You need to log in to play.',
  scope: 'Stridecraft needs permission to read your activities. Please allow it and try again.',
}

export function LoginPage() {
  const [params] = useSearchParams()
  const error = params.get('error')
  return (
    <main>
      <h1>Stridecraft</h1>
      <p>Turn your runs into a creature that trains with you.</p>
      {error && <p role="alert">{MESSAGES[error] ?? 'Login failed. Please try again.'}</p>}
      {/* A browser navigation, not a fetch: Strava's login page takes over the tab. */}
      <a href={`${API_URL}/auth/strava/login`}>Log in with Strava</a>
    </main>
  )
}
