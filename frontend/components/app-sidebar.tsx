"use client"

import { useState } from "react"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { Plus, Settings, Database, BookOpen, RefreshCcw } from "lucide-react"
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
import { useKnowledgeBase } from "@/components/knowledge-base-provider"
import { toast } from "sonner"

export function AppSidebar() {
  const {
    knowledgeBases,
    selectedKnowledgeBaseId,
    selectedKnowledgeBase,
    isLoading,
    error,
    refreshKnowledgeBases,
    createKnowledgeBase,
    addGithubSource,
    selectKnowledgeBase,
  } = useKnowledgeBase()

  const [isCreateOpen, setIsCreateOpen] = useState(false)
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [repoUrl, setRepoUrl] = useState("")
  const [branch, setBranch] = useState("")
  const [isPrivate, setIsPrivate] = useState(false)
  const [formError, setFormError] = useState("")
  const [isCreating, setIsCreating] = useState(false)

  async function handleCreateKnowledgeBase(e: React.FormEvent) {
    e.preventDefault()
    const trimmedName = name.trim()
    const trimmedRepoUrl = repoUrl.trim()
    const trimmedBranch = branch.trim()

    if (!trimmedName) {
      setFormError("Name is required")
      return
    }

    if (!trimmedRepoUrl) {
      setFormError("Repository URL is required")
      return
    }

    if (!trimmedRepoUrl.startsWith("https://github.com/")) {
      setFormError("Use a valid GitHub URL starting with https://github.com/")
      return
    }

    setFormError("")
    setIsCreating(true)
    try {
      const created = await createKnowledgeBase(trimmedName, description)
      await addGithubSource(created.id, {
        repo_url: trimmedRepoUrl,
        branch: trimmedBranch || undefined,
        is_private: isPrivate,
      })

      toast.success(`Knowledge base "${trimmedName}" created`, { position: "top-right"})
      setName("")
      setDescription("")
      setRepoUrl("")
      setBranch("")
      setIsPrivate(false)
      setIsCreateOpen(false)
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to create knowledge base"
      setFormError(message)
      toast.error(message, { position: "top-right"})
    } finally {
      setIsCreating(false)
    }
  }

  return (
    <>
      <Sheet open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <SheetContent side="left">
          <SheetHeader>
            <SheetTitle>Create Knowledge Base</SheetTitle>
            <SheetDescription>
              Create a new knowledge base with the available API route.
            </SheetDescription>
          </SheetHeader>

          <form onSubmit={handleCreateKnowledgeBase} className="flex h-full flex-col px-6 pb-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="kb-name" className="text-sm font-medium">
                  Name
                </label>
                <Input
                  id="kb-name"
                  value={name}
                  onChange={(e) => {
                    setName(e.target.value)
                    if (formError) setFormError("")
                  }}
                  placeholder="Engineering Docs"
                  disabled={isCreating}
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="kb-description" className="text-sm font-medium">
                  Description (Optional)
                </label>
                <Input
                  id="kb-description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Internal runbooks and architecture notes"
                  disabled={isCreating}
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="kb-repo-url" className="text-sm font-medium">
                  Repository URL
                </label>
                <Input
                  id="kb-repo-url"
                  value={repoUrl}
                  onChange={(e) => {
                    setRepoUrl(e.target.value)
                    if (formError) setFormError("")
                  }}
                  placeholder="https://github.com/owner/repo"
                  disabled={isCreating}
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="kb-repo-branch" className="text-sm font-medium">
                  Branch (Optional)
                </label>
                <Input
                  id="kb-repo-branch"
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                  placeholder="main"
                  disabled={isCreating}
                />
              </div>

              <div className="flex items-start gap-2 rounded-lg border border-border px-3 py-2">
                <input
                  id="kb-repo-private"
                  type="checkbox"
                  checked={isPrivate}
                  onChange={(e) => setIsPrivate(e.target.checked)}
                  disabled={isCreating}
                  className="mt-0.5 h-4 w-4"
                />
                <label htmlFor="kb-repo-private" className="text-sm">
                  Private repository
                </label>
              </div>

              {formError && <p className="text-xs text-destructive">{formError}</p>}
            </div>

            <SheetFooter className="px-0">
              <Button type="button" variant="ghost" onClick={() => setIsCreateOpen(false)} disabled={isCreating}>
                Cancel
              </Button>
              <Button type="submit" disabled={isCreating}>
                {isCreating ? "Creating..." : "Create"}
              </Button>
            </SheetFooter>
          </form>
        </SheetContent>
      </Sheet>

      <Sidebar>
      <SidebarHeader className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-primary" />
            <span className="font-semibold text-base">MemoCore</span>
          </div>
          <Button variant="ghost" size="icon-sm" onClick={() => void refreshKnowledgeBases()} disabled={isLoading}>
            <RefreshCcw className="h-4 w-4" />
            <span className="sr-only">Refresh knowledge bases</span>
          </Button>
        </div>
        <Button size="sm" className="w-full mt-2 gap-2" onClick={() => setIsCreateOpen(true)}>
          <Plus className="h-4 w-4" />
          New Knowledge Base
        </Button>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="flex items-center gap-1.5">
            <Database className="h-3.5 w-3.5" />
            Knowledge Bases
          </SidebarGroupLabel>
          <SidebarGroupContent>
            {!!error && <p className="px-3 py-1 text-xs text-destructive">{error}</p>}

            <SidebarMenu>
              {knowledgeBases.map((kb) => (
                <SidebarMenuItem key={kb.id}>
                  <SidebarMenuButton
                    isActive={selectedKnowledgeBaseId === kb.id}
                    className="pr-10"
                    onClick={() => void selectKnowledgeBase(kb.id)}
                  >
                    <span className="text-sm truncate">{kb.name}</span>
                  </SidebarMenuButton>
                  <SidebarMenuBadge>{selectedKnowledgeBaseId === kb.id ? "Active" : ""}</SidebarMenuBadge>
                </SidebarMenuItem>
              ))}

              {!isLoading && !knowledgeBases.length && (
                <SidebarMenuItem>
                  <div className="px-3 py-2 text-xs text-muted-foreground">No knowledge bases yet.</div>
                </SidebarMenuItem>
              )}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="p-2">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton className="gap-2 text-muted-foreground" disabled>
              <Settings className="h-4 w-4" />
              Update/Delete unavailable in API
            </SidebarMenuButton>
          </SidebarMenuItem>
          <SidebarMenuItem>
            <SidebarMenuButton className="gap-2 text-muted-foreground" disabled>
              <Database className="h-4 w-4" />
              Current: {selectedKnowledgeBase?.name ?? "None"}
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
      </Sidebar>
    </>
  )
}