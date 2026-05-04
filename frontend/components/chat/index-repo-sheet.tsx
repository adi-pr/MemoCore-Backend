import { useState } from "react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"

type RepoPayload = {
  repo_url: string
  branch?: string
}

type IndexRepoSheetProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  isIndexing: boolean
  onSubmit: (payload: RepoPayload) => Promise<void>
}

export function IndexRepoSheet({
  open,
  onOpenChange,
  isIndexing,
  onSubmit,
}: IndexRepoSheetProps) {
  const [repoUrl, setRepoUrl] = useState("")
  const [branch, setBranch] = useState("")
  const [repoUrlError, setRepoUrlError] = useState("")

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()

    const trimmedRepoUrl = repoUrl.trim()
    const trimmedBranch = branch.trim()

    if (!trimmedRepoUrl) {
      setRepoUrlError("Repository URL is required")
      return
    }

    if (!trimmedRepoUrl.startsWith("https://github.com/")) {
      setRepoUrlError("Use a valid GitHub URL starting with https://github.com/")
      return
    }

    setRepoUrlError("")

    const payload: RepoPayload = { repo_url: trimmedRepoUrl }
    if (trimmedBranch) payload.branch = trimmedBranch

    await onSubmit(payload)

    setRepoUrl("")
    setBranch("")
    onOpenChange(false)
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right">
        <SheetHeader>
          <SheetTitle>Index GitHub Repository</SheetTitle>
          <SheetDescription>
            Provide a repository URL and optional branch to ingest and index content.
          </SheetDescription>
        </SheetHeader>

        <form onSubmit={handleSubmit} className="flex h-full flex-col px-6 pb-6">
          <div className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="repo-url" className="text-sm font-medium">
                Repository URL
              </label>
              <Input
                id="repo-url"
                value={repoUrl}
                onChange={(e) => {
                  setRepoUrl(e.target.value)
                  if (repoUrlError) setRepoUrlError("")
                }}
                placeholder="https://github.com/owner/repo"
                disabled={isIndexing}
                aria-invalid={!!repoUrlError}
              />
              {repoUrlError && <p className="text-xs text-destructive">{repoUrlError}</p>}
            </div>

            <div className="space-y-2">
              <label htmlFor="repo-branch" className="text-sm font-medium">
                Branch (Optional)
              </label>
              <Input
                id="repo-branch"
                value={branch}
                onChange={(e) => setBranch(e.target.value)}
                placeholder="main"
                disabled={isIndexing}
              />
            </div>
          </div>

          <SheetFooter className="px-0">
            <Button type="button" variant="ghost" onClick={() => onOpenChange(false)} disabled={isIndexing}>
              Cancel
            </Button>
            <Button type="submit" disabled={isIndexing}>
              {isIndexing ? "Indexing..." : "Index Repository"}
            </Button>
          </SheetFooter>
        </form>
      </SheetContent>
    </Sheet>
  )
}
