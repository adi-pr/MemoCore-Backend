import { Database, Send } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

type ChatComposerProps = {
  input: string
  onInputChange: (value: string) => void
  onSubmit: (e: React.FormEvent) => void
  onOpenIndexSheet: () => void
  isStreaming: boolean
  isIndexing: boolean
}

export function ChatComposer({
  input,
  onInputChange,
  onSubmit,
  onOpenIndexSheet,
  isStreaming,
  isIndexing,
}: ChatComposerProps) {
  return (
    <div className="border-t bg-background px-4 py-4">
      <form onSubmit={onSubmit} className="flex gap-2 max-w-2xl mx-auto">
        <Button
          type="button"
          variant="outline"
          onClick={onOpenIndexSheet}
          disabled={isStreaming || isIndexing}
          className="shrink-0"
        >
          <Database className="h-4 w-4" />
          {isIndexing ? "Indexing..." : "Index Repo"}
        </Button>
        <Input
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          placeholder="Ask a question..."
          disabled={isStreaming || isIndexing}
          className="flex-1 tab-index-0"
        />
        <Button type="submit" disabled={!input.trim() || isStreaming || isIndexing} size="icon">
          <Send className="h-4 w-4" />
        </Button>
      </form>
    </div>
  )
}
