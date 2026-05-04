"use client"

import { useState, useRef, useEffect } from "react"
import { ChatComposer } from "@/components/chat/chat-composer"
import { ChatMessages } from "@/components/chat/chat-messages"
import { IndexRepoSheet } from "@/components/chat/index-repo-sheet"
import type { Message } from "@/components/chat/types"

const DEMO_MESSAGES: Message[] = [
  { id: 1, role: "assistant", content: "Hello! Ask me anything about your knowledge base." },
]

export default function Page() {
  const [messages, setMessages] = useState<Message[]>(DEMO_MESSAGES)
  const [input, setInput] = useState("")
  const [isStreaming, setIsStreaming] = useState(false)
  const [isIndexing, setIsIndexing] = useState(false)
  const [isIndexSheetOpen, setIsIndexSheetOpen] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = input.trim()
    if (!trimmed || isStreaming) return

    const userMsg: Message = { id: Date.now(), role: "user", content: trimmed }
    const assistantId = Date.now() + 1

    setInput("")
    setIsStreaming(true)
    setMessages((prev) => [...prev, userMsg, { id: assistantId, role: "assistant", content: "" }])

    try {
      const res = await fetch("http://localhost:8000/ask/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmed }),
      })

      if (!res.ok || !res.body) throw new Error(`Server error: ${res.status}`)

      const reader = res.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value, { stream: true })
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId ? { ...m, content: m.content + chunk } : m
          )
        )
      }
    } catch (err) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, content: `Error: ${err instanceof Error ? err.message : "Something went wrong"}` }
            : m
        )
      )
    } finally {
      setIsStreaming(false)
    }
  }

  async function handleIndexRepo(payload: { repo_url: string; branch?: string }) {
    if (isStreaming || isIndexing) return

    const trimmedRepoUrl = payload.repo_url.trim()
    const trimmedBranch = payload.branch?.trim()

    const statusId = Date.now()
    setIsIndexing(true)
    setMessages((prev) => [
      ...prev,
      {
        id: statusId,
        role: "assistant",
          content: `Indexing repository: ${trimmedRepoUrl}${trimmedBranch ? ` (branch: ${trimmedBranch})` : ""}...`,
      },
    ])

    try {
      const res = await fetch("http://localhost:8000/ingest/github", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })

      const data = await res.json().catch(() => null)

      if (!res.ok) {
        const detail =
          data && typeof data.detail === "string"
            ? data.detail
            : `Request failed with status ${res.status}`
        throw new Error(detail)
      }

      const indexed = typeof data?.indexed === "number" ? data.indexed : 0
      setMessages((prev) =>
        prev.map((m) =>
          m.id === statusId
            ? {
                ...m,
                content: `Indexed ${indexed} document${indexed === 1 ? "" : "s"} from ${trimmedRepoUrl}.`,
              }
            : m
        )
      )

    } catch (err) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === statusId
            ? { ...m, content: `Indexing failed: ${err instanceof Error ? err.message : "Something went wrong"}` }
            : m
        )
      )
    } finally {
      setIsIndexing(false)
    }
  }

  return (
    <div className="flex flex-col h-svh w-full">
      <IndexRepoSheet
        open={isIndexSheetOpen}
        onOpenChange={setIsIndexSheetOpen}
        isIndexing={isIndexing}
        onSubmit={handleIndexRepo}
      />

      <ChatMessages messages={messages} isStreaming={isStreaming} bottomRef={bottomRef} />

      <ChatComposer
        input={input}
        onInputChange={setInput}
        onSubmit={handleSubmit}
        onOpenIndexSheet={() => setIsIndexSheetOpen(true)}
        isStreaming={isStreaming}
        isIndexing={isIndexing}
      />
    </div>
  )
}
