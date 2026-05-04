"use client"

import { useState, useRef, useEffect } from "react"
import { ChatComposer } from "@/components/chat/chat-composer"
import { ChatMessages } from "@/components/chat/chat-messages"
import type { Message } from "@/components/chat/types"
import { useKnowledgeBase } from "@/components/knowledge-base-provider"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"

const DEMO_MESSAGES: Message[] = [
  { id: 1, role: "assistant", content: "Hello! Ask me anything about your knowledge base." },
]

export default function Page() {
  const { selectedKnowledgeBaseId, selectedKnowledgeBase } = useKnowledgeBase()
  const [messages, setMessages] = useState<Message[]>(DEMO_MESSAGES)
  const [input, setInput] = useState("")
  const [isStreaming, setIsStreaming] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const trimmed = input.trim()
    if (!trimmed || isStreaming) return

    if (!selectedKnowledgeBaseId) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          role: "assistant",
          content: "Create or select a knowledge base first.",
        },
      ])
      return
    }

    const userMsg: Message = { id: Date.now(), role: "user", content: trimmed }
    const assistantId = Date.now() + 1

    setInput("")
    setIsStreaming(true)
    setMessages((prev) => [...prev, userMsg, { id: assistantId, role: "assistant", content: "" }])

    try {
      const res = await fetch(`${API_BASE_URL}/ask/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          knowledge_base_id: selectedKnowledgeBaseId,
          question: trimmed,
        }),
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

  return (
    <div className="flex flex-col h-svh w-full">
      <div className="px-4 pb-2 text-xs text-muted-foreground">
        Active knowledge base: {selectedKnowledgeBase?.name ?? "None selected"}
      </div>

      <ChatMessages messages={messages} isStreaming={isStreaming} bottomRef={bottomRef} />

      <ChatComposer
        input={input}
        onInputChange={setInput}
        onSubmit={handleSubmit}
        isStreaming={isStreaming}
      />
    </div>
  )
}
