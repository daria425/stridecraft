import { Navigate, Outlet } from 'react-router'
import { useMe } from '../../api/queries'
import { SceneMessage } from '../../components/SceneMessage'
import { destinationFor, type Destination } from './destination'

/** Renders its child routes only for visitors who belong on `page`; everyone else is sent to
 * where they do belong (login, adoption or the dashboard). */
export function Gate({ page }: { page: Destination }) {
  const me = useMe()
  if (me.isPending) return <SceneMessage>Loading...</SceneMessage>
  if (me.isError)
    return <SceneMessage>Could not reach the server. Try again in a moment.</SceneMessage>
  const home = destinationFor(me.data)
  return home === page ? <Outlet /> : <Navigate to={home} replace />
}
