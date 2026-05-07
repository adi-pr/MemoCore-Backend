"use client"

import { useState, useRef, useEffect } from "react"
import { ChatComposer } from "@/components/chat/chat-composer"
import { ChatMessages } from "@/components/chat/chat-messages"
import type { Message } from "@/components/chat/types"
import { useKnowledgeBase } from "@/components/knowledge-base-provider"
import { apiFetch, apiStream, type QueryResponse } from "@/lib/api"

const DEMO_MESSAGES: Message[] = [
  {
    id: 1,
    role: "assistant",
    content:
      "Hello. Select a knowledge base, then ask a question with either the standard or streaming query route.",
  },
]

export default function Page() {
  const { selectedKnowledgeBaseId, selectedKnowledgeBase } = useKnowledgeBase()
  const [messages, setMessages] = useState<Message[]>(DEMO_MESSAGES)
  const [input, setInput] = useState("")
  const [isStreaming, setIsStreaming] = useState(false)
  const [topK, setTopK] = useState(4)
  const [responseMode, setResponseMode] = useState<"stream" | "standard">("stream")
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  useEffect(() => {
    setMessages((prev) => {
      if (!selectedKnowledgeBase) {
        return DEMO_MESSAGES
      }

      if (prev.length > 1) {
        return prev
      }

      return [
        DEMO_MESSAGES[0],
        {
          id: Date.now(),
          role: "assistant",
          content: `Using knowledge base "${selectedKnowledgeBase.name}".`,
        },
      ]
    })
  }, [selectedKnowledgeBase])

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
      if (responseMode === "stream") {
        const res = await apiStream("/ask/stream", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            knowledge_base_id: selectedKnowledgeBaseId,
            question: trimmed,
            top_k: topK,
          }),
        })

        const body = res.body
        if (!body) {
          throw new Error("Streaming response body is not available")
        }

        const reader = body.getReader()
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
      } else {
        const result = await apiFetch<QueryResponse>("/ask", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            knowledge_base_id: selectedKnowledgeBaseId,
            question: trimmed,
            top_k: topK,
          }),
        })

        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantId
              ? { ...m, content: result.answer, sources: result.sources ?? [] }
              : m
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
        {selectedKnowledgeBase?.giturl ? ` · ${selectedKnowledgeBase.giturl}` : ""}
      </div>

      <ChatMessages messages={messages} isStreaming={isStreaming} bottomRef={bottomRef} />

      <ChatComposer
        input={input}
        onInputChange={setInput}
        onSubmit={handleSubmit}
        isStreaming={isStreaming}
        topK={topK}
        onTopKChange={setTopK}
        responseMode={responseMode}
        onResponseModeChange={setResponseMode}
      />
    </div>
  )
}
