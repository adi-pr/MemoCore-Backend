"use client"

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"

export type KnowledgeBase = {
  id: string
  name: string
  description?: string | null
  created_at: string
  updated_at: string
}

export type GithubSourcePayload = {
  repo_url: string
  branch?: string
  is_private: boolean
}

type KnowledgeBaseContextValue = {
  knowledgeBases: KnowledgeBase[]
  selectedKnowledgeBaseId: string | null
  selectedKnowledgeBase: KnowledgeBase | null
  isLoading: boolean
  error: string | null
  refreshKnowledgeBases: () => Promise<void>
  createKnowledgeBase: (name: string, description?: string) => Promise<KnowledgeBase>
  addGithubSource: (knowledgeBaseId: string, payload: GithubSourcePayload) => Promise<void>
  selectKnowledgeBase: (id: string) => Promise<void>
}

const KnowledgeBaseContext = createContext<KnowledgeBaseContextValue | null>(null)

async function parseErrorMessage(res: Response): Promise<string> {
  const data = await res.json().catch(() => null)
  if (data && typeof data.detail === "string") return data.detail
  return `Request failed with status ${res.status}`
}

export function KnowledgeBaseProvider({ children }: { children: React.ReactNode }) {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [selectedKnowledgeBaseId, setSelectedKnowledgeBaseId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refreshKnowledgeBases = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      const res = await fetch(`${API_BASE_URL}/knowledge-bases`)
      if (!res.ok) throw new Error(await parseErrorMessage(res))

      const list: KnowledgeBase[] = await res.json()
      setKnowledgeBases(list)

      setSelectedKnowledgeBaseId((prev) => {
        if (!list.length) return null
        if (prev && list.some((kb) => kb.id === prev)) return prev
        return list[0].id
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load knowledge bases")
    } finally {
      setIsLoading(false)
    }
  }, [])

  const selectKnowledgeBase = useCallback(async (id: string) => {
    setError(null)
    try {
      const res = await fetch(`${API_BASE_URL}/knowledge-bases/${id}`)
      if (!res.ok) throw new Error(await parseErrorMessage(res))

      const kb: KnowledgeBase = await res.json()
      setKnowledgeBases((prev) => {
        const exists = prev.some((item) => item.id === kb.id)
        if (!exists) return [kb, ...prev]
        return prev.map((item) => (item.id === kb.id ? kb : item))
      })
      setSelectedKnowledgeBaseId(kb.id)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to select knowledge base")
    }
  }, [])

  const createKnowledgeBase = useCallback(async (name: string, description?: string) => {
    setError(null)

    const res = await fetch(`${API_BASE_URL}/knowledge-bases`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: name.trim(), description: description?.trim() || undefined }),
    })

    if (!res.ok) {
      throw new Error(await parseErrorMessage(res))
    }

    const created: KnowledgeBase = await res.json()
    setKnowledgeBases((prev) => [created, ...prev])
    setSelectedKnowledgeBaseId(created.id)
    return created
  }, [])

  const addGithubSource = useCallback(async (knowledgeBaseId: string, payload: GithubSourcePayload) => {
    const res = await fetch(`${API_BASE_URL}/knowledge-bases/${knowledgeBaseId}/sources/github`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        repo_url: payload.repo_url.trim(),
        branch: payload.branch?.trim() || undefined,
        is_private: payload.is_private,
      }),
    })

    if (!res.ok) {
      throw new Error(await parseErrorMessage(res))
    }
  }, [])

  useEffect(() => {
    void refreshKnowledgeBases()
  }, [refreshKnowledgeBases])

  const selectedKnowledgeBase = useMemo(
    () => knowledgeBases.find((kb) => kb.id === selectedKnowledgeBaseId) ?? null,
    [knowledgeBases, selectedKnowledgeBaseId]
  )

  const value = useMemo<KnowledgeBaseContextValue>(
    () => ({
      knowledgeBases,
      selectedKnowledgeBaseId,
      selectedKnowledgeBase,
      isLoading,
      error,
      refreshKnowledgeBases,
      createKnowledgeBase,
      addGithubSource,
      selectKnowledgeBase,
    }),
    [
      knowledgeBases,
      selectedKnowledgeBaseId,
      selectedKnowledgeBase,
      isLoading,
      error,
      refreshKnowledgeBases,
      createKnowledgeBase,
      addGithubSource,
      selectKnowledgeBase,
    ]
  )

  return <KnowledgeBaseContext.Provider value={value}>{children}</KnowledgeBaseContext.Provider>
}

export function useKnowledgeBase() {
  const context = useContext(KnowledgeBaseContext)
  if (!context) {
    throw new Error("useKnowledgeBase must be used within KnowledgeBaseProvider")
  }
  return context
}
