import { Bot, User } from "lucide-react"

import { cn } from "@/lib/utils"

import type { Message } from "./types"

type ChatMessagesProps = {
  messages: Message[]
  isStreaming: boolean
  bottomRef: React.RefObject<HTMLDivElement | null>
}

function getSourceLabel(metadata: Record<string, unknown> | null | undefined, index: number) {
  const candidateKeys = ["path", "source", "file_path", "file", "name"]

  for (const key of candidateKeys) {
    const value = metadata?.[key]
    if (typeof value === "string" && value.trim()) {
      return value
    }
  }

  return `Source ${index + 1}`
}

export function ChatMessages({ messages, isStreaming, bottomRef }: ChatMessagesProps) {
  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={cn(
            "flex items-start gap-3 max-w-2xl",
            msg.role === "user" ? "ml-auto flex-row-reverse" : ""
          )}
        >
          <div
            className={cn(
              "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
              msg.role === "assistant"
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground"
            )}
          >
            {msg.role === "assistant" ? (
              <Bot className="h-4 w-4" />
            ) : (
              <User className="h-4 w-4" />
            )}
          </div>
          <div
            className={cn(
              "rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
              msg.role === "assistant"
                ? "bg-muted text-foreground"
                : "bg-primary text-primary-foreground"
            )}
          >
            {msg.content}
            {isStreaming && msg.role === "assistant" && msg.id === messages[messages.length - 1].id && (
              <span className="ml-0.5 inline-block w-1.5 h-3.5 bg-current align-middle animate-pulse rounded-sm" />
            )}
            {!!msg.sources?.length && (
              <div className="mt-3 space-y-2 border-t border-border/60 pt-3">
                {msg.sources.map((source, index) => (
                  <div key={`${msg.id}-${index}`} className="rounded-xl bg-background/70 px-3 py-2 text-xs text-muted-foreground">
                    <div className="font-medium text-foreground">{getSourceLabel(source.metadata ?? undefined, index)}</div>
                    <div className="mt-1 line-clamp-4 whitespace-pre-wrap">{source.content}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
