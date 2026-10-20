import createClient from 'openapi-fetch'
import type { paths } from './schema'

export const API_URL: string = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export const api = createClient<paths>({ baseUrl: API_URL, credentials: 'include' })

/** An error response from the API, with the plain-English message the server wrote. */
export class ApiError extends Error {
  status: number
  code: string

  constructor(status: number, code: string, message: string) {
    super(message)
    this.status = status
    this.code = code
  }
}

/** Unwrap an openapi-fetch result: the data, or an ApiError carrying the server's message. */
export function unwrap<T>(result: { data?: T; error?: unknown; response: Response }): T {
  if (result.error === undefined) return result.data as T
  const body = result.error as { code?: string; message?: string }
  const message = body.message ?? 'Something went wrong'
  throw new ApiError(result.response.status, body.code ?? 'error', message)
}
