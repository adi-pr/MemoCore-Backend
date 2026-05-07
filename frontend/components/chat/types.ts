import type { Source } from "@/lib/api"

export type Message = {
  id: number
  role: "user" | "assistant"
  content: string
  sources?: Source[] | null
}
