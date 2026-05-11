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
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { Plus, Pencil, Trash2, Database, BookOpen, RefreshCcw, Activity } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
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

import type { CreateKnowledgeBaseInput, KnowledgeBase } from "@/lib/api"

type EditorMode = "create" | "edit"

type KnowledgeBaseDraft = {
  name: string
  giturl: string
  description: string
}

const EMPTY_DRAFT: KnowledgeBaseDraft = {
  name: "",
  giturl: "",
  description: "",
}

function getDraftFromKnowledgeBase(knowledgeBase: KnowledgeBase | null): KnowledgeBaseDraft {
  if (!knowledgeBase) {
    return EMPTY_DRAFT
  }

  return {
    name: knowledgeBase.name,
    giturl: knowledgeBase.giturl,
    description: knowledgeBase.description ?? "",
  }
}

export function AppSidebar() {
  const {
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
  } = useKnowledgeBase()

  const [isEditorOpen, setIsEditorOpen] = useState(false)
  const [editorMode, setEditorMode] = useState<EditorMode>("create")
  const [draft, setDraft] = useState<KnowledgeBaseDraft>(EMPTY_DRAFT)
  const [formError, setFormError] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  function openCreateSheet() {
    setEditorMode("create")
    setDraft(EMPTY_DRAFT)
    setFormError("")
    setIsEditorOpen(true)
  }

  function openEditSheet() {
    setEditorMode("edit")
    setDraft(getDraftFromKnowledgeBase(selectedKnowledgeBase))
    setFormError("")
    setIsEditorOpen(true)
  }

  function updateDraft<K extends keyof KnowledgeBaseDraft>(key: K, value: KnowledgeBaseDraft[K]) {
    setDraft((current) => ({ ...current, [key]: value }))
    if (formError) {
      setFormError("")
    }
  }

  async function handleSubmitKnowledgeBase(e: React.FormEvent) {
    e.preventDefault()

    const payload: CreateKnowledgeBaseInput = {
      name: draft.name.trim(),
      giturl: draft.giturl.trim(),
      description: draft.description.trim() || undefined,
    }

    if (!payload.name) {
      setFormError("Name is required")
      return
    }

    if (!payload.giturl) {
      setFormError("Repository URL is required")
      return
    }

    if (!payload.giturl.startsWith("https://github.com/")) {
      setFormError("Use a valid GitHub URL starting with https://github.com/")
      return
    }

    setFormError("")
    setIsSubmitting(true)

    try {
      if (editorMode === "create") {
        const created = await createKnowledgeBase(payload)
        toast.success(`Knowledge base "${created.name}" created`, { position: "top-right" })
      } else if (selectedKnowledgeBase) {
        const updated = await updateKnowledgeBase(selectedKnowledgeBase.id, payload)
        toast.success(`Knowledge base "${updated.name}" updated`, { position: "top-right" })
      }

      setDraft(EMPTY_DRAFT)
      setIsEditorOpen(false)
    } catch (err) {
      const message = err instanceof Error ? err.message : `Failed to ${editorMode} knowledge base`
      setFormError(message)
      toast.error(message, { position: "top-right" })
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleDeleteKnowledgeBase() {
    if (!selectedKnowledgeBase) {
      return
    }

    const confirmed = window.confirm(`Delete knowledge base "${selectedKnowledgeBase.name}"?`)
    if (!confirmed) {
      return
    }

    setIsDeleting(true)
    try {
      await deleteKnowledgeBase(selectedKnowledgeBase.id)
      toast.success(`Knowledge base "${selectedKnowledgeBase.name}" deleted`, { position: "top-right" })
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to delete knowledge base"
      toast.error(message, { position: "top-right" })
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <>
      <Sheet open={isEditorOpen} onOpenChange={setIsEditorOpen}>
        <SheetContent side="left">
          <SheetHeader>
            <SheetTitle>{editorMode === "create" ? "Create Knowledge Base" : "Edit Knowledge Base"}</SheetTitle>
            <SheetDescription>
              {editorMode === "create"
                ? "Create a knowledge base using the backend create route."
                : "Update the selected knowledge base using the backend update route."}
            </SheetDescription>
          </SheetHeader>

          <form onSubmit={handleSubmitKnowledgeBase} className="flex h-full flex-col px-6 pb-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="kb-name" className="text-sm font-medium">
                  Name
                </label>
                <Input
                  id="kb-name"
                  value={draft.name}
                  onChange={(e) => updateDraft("name", e.target.value)}
                  placeholder="Engineering Docs"
                  disabled={isSubmitting}
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="kb-description" className="text-sm font-medium">
                  Description (Optional)
                </label>
                <Input
                  id="kb-description"
                  value={draft.description}
                  onChange={(e) => updateDraft("description", e.target.value)}
                  placeholder="Internal runbooks and architecture notes"
                  disabled={isSubmitting}
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="kb-giturl" className="text-sm font-medium">
                  Repository URL
                </label>
                <Input
                  id="kb-giturl"
                  value={draft.giturl}
                  onChange={(e) => updateDraft("giturl", e.target.value)}
                  placeholder="https://github.com/owner/repo"
                  disabled={isSubmitting}
                />
              </div>

              {formError && <p className="text-xs text-destructive">{formError}</p>}
            </div>

            <SheetFooter className="px-0">
              <Button type="button" variant="ghost" onClick={() => setIsEditorOpen(false)} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? (editorMode === "create" ? "Creating..." : "Saving...") : editorMode === "create" ? "Create" : "Save Changes"}
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
              <span className="text-base font-semibold">MemoCore</span>
            </div>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon-sm" onClick={() => void refreshKnowledgeBases()} disabled={isLoading}>
                  <RefreshCcw className="h-4 w-4" />
                  <span className="sr-only">Refresh knowledge bases</span>
                </Button>
              </TooltipTrigger>
              <TooltipContent side="right">Refresh knowledge bases</TooltipContent>
            </Tooltip>
          </div>

          <div className="mt-3 flex items-center gap-2 rounded-full border border-border/60 bg-background/70 px-3 py-2 text-xs text-muted-foreground">
            <Activity className="h-3.5 w-3.5" />
            API {apiStatus === "checking" ? "checking" : apiStatus}
          </div>

          <Button size="sm" className="mt-2 w-full gap-2" onClick={openCreateSheet}>
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
                    <div className="flex items-start gap-2 px-1">
                      <SidebarMenuButton
                        isActive={selectedKnowledgeBaseId === kb.id}
                        className={`h-auto min-h-12 flex-1 items-start py-2 ${
                          selectedKnowledgeBaseId === kb.id
                            ? "rounded-md border border-emerald-500/35 bg-emerald-500/12"
                            : ""
                        }`}
                        onClick={() => void selectKnowledgeBase(kb.id)}
                      >
                        <div className="min-w-0 text-left">
                          <div className="truncate text-sm font-medium">{kb.name}</div>
                          <div className="truncate text-xs text-muted-foreground">{kb.giturl}</div>
                        </div>
                      </SidebarMenuButton>
                    </div>
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
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1 gap-2"
                  onClick={openEditSheet}
                  disabled={!selectedKnowledgeBase || isDeleting}
                >
                  <Pencil className="h-4 w-4" />
                  Edit
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  className="flex-1 gap-2"
                  onClick={() => void handleDeleteKnowledgeBase()}
                  disabled={!selectedKnowledgeBase || isDeleting}
                >
                  <Trash2 className="h-4 w-4" />
                  {isDeleting ? "Deleting..." : "Delete"}
                </Button>
              </div>
            </SidebarMenuItem>
            <SidebarMenuItem>
              <SidebarMenuButton className="gap-2 text-muted-foreground" disabled>
                <Database className="h-4 w-4" />
                Current: {selectedKnowledgeBase?.name ?? "None"}
              </SidebarMenuButton>
            </SidebarMenuItem>
            {selectedKnowledgeBase?.description && (
              <SidebarMenuItem>
                <div className="px-2 text-xs leading-relaxed text-muted-foreground">
                  {selectedKnowledgeBase.description}
                </div>
              </SidebarMenuItem>
            )}
          </SidebarMenu>
        </SidebarFooter>
      </Sidebar>
    </>
  )
}