import { Geist, Geist_Mono, Figtree } from "next/font/google"

import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"

import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { cn } from "@/lib/utils";
import { KnowledgeBaseProvider } from "@/components/knowledge-base-provider"
import { Toaster } from "@/components/ui/sonner"
import { TooltipProvider } from "@/components/ui/tooltip"

const figtree = Figtree({subsets:['latin'],variable:'--font-sans'})

const fontMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
})

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={cn("antialiased", fontMono.variable, "font-sans", figtree.variable)}
    >
      <body>
        <ThemeProvider>
          <Toaster richColors />
          <KnowledgeBaseProvider>
            <SidebarProvider>
              <TooltipProvider>
                <AppSidebar/>
                <main className="flex flex-col flex-1 min-w-0 h-svh">
                  <SidebarTrigger className="m-2 shrink-0"/>
                  {children}
                </main>
              </TooltipProvider>
            </SidebarProvider>
          </KnowledgeBaseProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
