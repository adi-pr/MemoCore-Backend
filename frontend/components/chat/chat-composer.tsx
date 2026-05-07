import { Send } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

type ChatComposerProps = {
  input: string
  onInputChange: (value: string) => void
  onSubmit: (e: React.FormEvent) => void
  isStreaming: boolean
  topK: number
  onTopKChange: (value: number) => void
  responseMode: "stream" | "standard"
  onResponseModeChange: (value: "stream" | "standard") => void
}

export function ChatComposer({
  input,
  onInputChange,
  onSubmit,
  isStreaming,
  topK,
  onTopKChange,
  responseMode,
  onResponseModeChange,
}: ChatComposerProps) {
  return (
    <div className="border-t bg-background px-4 py-4">
      <form onSubmit={onSubmit} className="mx-auto flex max-w-3xl flex-col gap-3">
        <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
          <div className="inline-flex rounded-full border border-border p-1">
            <Button
              type="button"
              variant={responseMode === "stream" ? "default" : "ghost"}
              size="xs"
              onClick={() => onResponseModeChange("stream")}
              disabled={isStreaming}
            >
              Stream
            </Button>
            <Button
              type="button"
              variant={responseMode === "standard" ? "default" : "ghost"}
              size="xs"
              onClick={() => onResponseModeChange("standard")}
              disabled={isStreaming}
            >
              Standard
            </Button>
          </div>

          <label className="flex items-center gap-2">
            <span>Top K</span>
            <Input
              type="number"
              min={1}
              max={12}
              value={topK}
              onChange={(e) => onTopKChange(Number(e.target.value) || 4)}
              disabled={isStreaming}
              className="h-8 w-20"
            />
          </label>
        </div>

        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => onInputChange(e.target.value)}
            placeholder="Ask a question about the selected knowledge base..."
            disabled={isStreaming}
            className="flex-1 tab-index-0"
          />
          <Button type="submit" disabled={!input.trim() || isStreaming} size="icon">
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </form>
    </div>
  )
}
