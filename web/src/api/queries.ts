import { useCallback } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api, unwrap } from './client'
import type { components } from './schema'

export type Me = components['schemas']['MeOut']
export type Breed = components['schemas']['BreedOut']
export type SyncStatus = components['schemas']['SyncStatusOut']
export type Journey = components['schemas']['JourneyOut']
export type JourneyEvent = components['schemas']['JourneyEventOut']

/** `null` when nobody is logged in. */
export function useMe() {
  return useQuery({
    queryKey: ['me'],
    queryFn: async (): Promise<Me | null> => {
      const result = await api.GET('/me')
      if (result.response.status === 401) return null
      return unwrap(result)
    },
    retry: false,
  })
}

export function useBreeds() {
  return useQuery({
    queryKey: ['breeds'],
    queryFn: async () => unwrap(await api.GET('/breeds')),
    staleTime: Infinity,
  })
}

export function useRandomName() {
  const client = useQueryClient()
  return useCallback(
    () =>
      client.fetchQuery({
        queryKey: ['random-name'],
        queryFn: async () => unwrap(await api.GET('/names/random')).name,
        staleTime: 0,
      }),
    [client],
  )
}

export function useAdopt() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: async (body: { breed: string; name: string | null; waypoint_spacing_km: number }) =>
      unwrap(await api.POST('/me/strider', { body })),
    // Also on failure: a 409 (already adopted) means /me now has a strider and the gate should move on.
    onSettled: () => client.invalidateQueries({ queryKey: ['me'] }),
  })
}

export function useLogout() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      await api.POST('/auth/logout')
    },
    onSuccess: () => client.setQueryData(['me'], null),
  })
}

export const SYNC_POLL_MS = 2000

export function useSyncStatus() {
  return useQuery({
    queryKey: ['sync'],
    queryFn: async () => unwrap(await api.GET('/me/sync')),
    refetchInterval: (query) => (query.state.data?.state === 'running' ? SYNC_POLL_MS : false),
  })
}

/** Start an import. "Already running" is the state we wanted, so it is not an error. */
export function useStartSync() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      const result = await api.POST('/me/sync')
      if (result.response.status === 409) return
      unwrap(result)
    },
    onSettled: () => client.invalidateQueries({ queryKey: ['sync'] }),
  })
}

export function useJourney() {
  return useQuery({
    queryKey: ['journey'],
    queryFn: async () => unwrap(await api.GET('/me/journey')),
  })
}

/** Tell the server the crossings up to `waypointNumber` have been shown, so they are not shown
 * again on any device. The cache moves at once: the banner must not flash back while it saves. */
export function useMarkJourneySeen() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: async (waypointNumber: number) =>
      unwrap(await api.POST('/me/journey/seen', { body: { waypoint_number: waypointNumber } })),
    onMutate: (waypointNumber) => {
      client.setQueryData<Journey>(
        ['journey'],
        (journey) =>
          journey && { ...journey, seen_waypoint: Math.max(journey.seen_waypoint, waypointNumber) },
      )
    },
  })
}
