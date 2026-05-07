export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"

export type Source = {
  content: string
  metadata?: Record<string, unknown> | null
}

export type QueryResponse = {
  answer: string
  sources?: Source[] | null
}

export type KnowledgeBase = {
  id: string
  giturl: string
  name: string
  description?: string | null
  created_at: string
  updated_at: string
}

export type CreateKnowledgeBaseInput = {
  giturl: string
  name: string
  description?: string
}

export type UpdateKnowledgeBaseInput = {
  giturl?: string
  name?: string
  description?: string
}

async function parseErrorMessage(response: Response): Promise<string> {
  const data = await response.json().catch(() => null)
  if (data && typeof data.detail === "string") {
    return data.detail
  }

  return `Request failed with status ${response.status}`
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init)
  if (!response.ok) {
    throw new Error(await parseErrorMessage(response))
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

export async function apiStream(path: string, init?: RequestInit): Promise<Response> {
  const response = await fetch(`${API_BASE_URL}${path}`, init)
  if (!response.ok) {
    throw new Error(await parseErrorMessage(response))
  }

  if (!response.body) {
    throw new Error("Streaming response body is not available")
  }

  return response
}