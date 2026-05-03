"use client"

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
import { Plus, Settings, Database, Trash2, BookOpen } from "lucide-react"
import { Button } from "@/components/ui/button"

const knowledgeBases = [
  { id: 1, name: "Product Docs", docCount: 142 },
  { id: 2, name: "Research Papers", docCount: 37 },
  { id: 3, name: "Internal Wiki", docCount: 89 },
]

export function AppSidebar() {
  return (
    <Sidebar>
      <SidebarHeader className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-primary" />
            <span className="font-semibold text-base">MemoCore</span>
          </div>
        </div>
        <Button size="sm" className="w-full mt-2 gap-2">
          <Plus className="h-4 w-4" />
          New Chat
        </Button>
      </SidebarHeader>

      <SidebarContent>

        {/* Knowledge Bases */}
        <SidebarGroup>
          <SidebarGroupLabel className="flex items-center gap-1.5">
            <Database className="h-3.5 w-3.5" />
            Knowledge Bases
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {knowledgeBases.map((kb) => (
                <SidebarMenuItem key={kb.id}>
                  <SidebarMenuButton className="flex items-center justify-between">
                    <span className="text-sm">{kb.name}</span>
                    <span className="text-xs text-muted-foreground bg-muted rounded px-1.5 py-0.5">
                      {kb.docCount}
                    </span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="p-2">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton className="gap-2 text-muted-foreground">
              <Trash2 className="h-4 w-4" />
              Clear History
            </SidebarMenuButton>
          </SidebarMenuItem>
          <SidebarMenuItem>
            <SidebarMenuButton className="gap-2 text-muted-foreground">
              <Settings className="h-4 w-4" />
              Settings
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  )
}