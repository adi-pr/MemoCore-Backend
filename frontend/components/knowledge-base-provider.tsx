"use client"

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react"

import {
  apiFetch,
  type CreateKnowledgeBaseInput,
  type KnowledgeBase,
  type UpdateKnowledgeBaseInput,
} from "@/lib/api"

type KnowledgeBaseContextValue = {
  knowledgeBases: KnowledgeBase[]
  selectedKnowledgeBaseId: string | null
  selectedKnowledgeBase: KnowledgeBase | null
  isLoading: boolean
  error: string | null
  apiStatus: "checking" | "online" | "offline"
  refreshKnowledgeBases: () => Promise<void>
  createKnowledgeBase: (payload: CreateKnowledgeBaseInput) => Promise<KnowledgeBase>
  updateKnowledgeBase: (knowledgeBaseId: string, payload: UpdateKnowledgeBaseInput) => Promise<KnowledgeBase>
  deleteKnowledgeBase: (knowledgeBaseId: string) => Promise<void>
  selectKnowledgeBase: (id: string) => Promise<void>
}

const KnowledgeBaseContext = createContext<KnowledgeBaseContextValue | null>(null)

export function KnowledgeBaseProvider({ children }: { children: React.ReactNode }) {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [selectedKnowledgeBaseId, setSelectedKnowledgeBaseId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [apiStatus, setApiStatus] = useState<"checking" | "online" | "offline">("checking")

  const refreshKnowledgeBases = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      const list = await apiFetch<KnowledgeBase[]>("/knowledge-bases")
      setKnowledgeBases(list)
      setApiStatus("online")

      setSelectedKnowledgeBaseId((prev) => {
        if (!list.length) {
          return null
        }

        if (prev && list.some((kb) => kb.id === prev)) {
          return prev
        }

        return list[0].id
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load knowledge bases")
      setApiStatus("offline")
    } finally {
      setIsLoading(false)
    }
  }, [])

  const selectKnowledgeBase = useCallback(async (id: string) => {
    setError(null)

    try {
      const kb = await apiFetch<KnowledgeBase>(`/knowledge-bases/${id}`)
      setKnowledgeBases((prev) => {
        const exists = prev.some((item) => item.id === kb.id)
        if (!exists) {
          return [kb, ...prev]
        }

        return prev.map((item) => (item.id === kb.id ? kb : item))
      })
      setSelectedKnowledgeBaseId(kb.id)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to select knowledge base")
    }
  }, [])

  const createKnowledgeBase = useCallback(async (payload: CreateKnowledgeBaseInput) => {
    setError(null)

    const created = await apiFetch<KnowledgeBase>("/knowledge-bases", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        giturl: payload.giturl.trim(),
        name: payload.name.trim(),
        description: payload.description?.trim() || undefined,
      }),
    })

    setKnowledgeBases((prev) => [created, ...prev])
    setSelectedKnowledgeBaseId(created.id)
    return created
  }, [])

  const updateKnowledgeBase = useCallback(async (knowledgeBaseId: string, payload: UpdateKnowledgeBaseInput) => {
    setError(null)

    const updated = await apiFetch<KnowledgeBase>(`/knowledge-bases/${knowledgeBaseId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        giturl: payload.giturl?.trim() || undefined,
        name: payload.name?.trim() || undefined,
        description: payload.description?.trim() || undefined,
      }),
    })

    setKnowledgeBases((prev) => prev.map((item) => (item.id === updated.id ? updated : item)))
    setSelectedKnowledgeBaseId(updated.id)

    return updated
  }, [])

  const deleteKnowledgeBase = useCallback(
    async (knowledgeBaseId: string) => {
      setError(null)

      await apiFetch<void>(`/knowledge-bases/${knowledgeBaseId}`, {
        method: "DELETE",
      })

      setKnowledgeBases((prev) => {
        const remaining = prev.filter((item) => item.id !== knowledgeBaseId)
        setSelectedKnowledgeBaseId((selectedId) => {
          if (selectedId !== knowledgeBaseId) {
            return selectedId
          }

          return remaining[0]?.id ?? null
        })
        return remaining
      })
    },
    []
  )

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => {
      void refreshKnowledgeBases()
    })

    return () => window.cancelAnimationFrame(frame)
  }, [refreshKnowledgeBases])

  useEffect(() => {
    apiFetch<{ status: string }>("/health")
      .then(() => setApiStatus("online"))
      .catch(() => setApiStatus("offline"))
  }, [])

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
      apiStatus,
      refreshKnowledgeBases,
      createKnowledgeBase,
      updateKnowledgeBase,
      deleteKnowledgeBase,
      selectKnowledgeBase,
    }),
    [
      knowledgeBases,
      selectedKnowledgeBaseId,
      selectedKnowledgeBase,
      isLoading,
      error,
      apiStatus,
      refreshKnowledgeBases,
      createKnowledgeBase,
      updateKnowledgeBase,
      deleteKnowledgeBase,
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
