import type { Me } from '../../api/queries'

export type Destination = '/login' | '/adopt' | '/'

/** Where a visitor belongs, given what `GET /me` said: not logged in, no strider yet, or all set. */
export function destinationFor(me: Me | null): Destination {
  if (me === null) return '/login'
  return me.strider === null ? '/adopt' : '/'
}
