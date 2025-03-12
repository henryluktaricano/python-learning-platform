"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Home, BookOpen, BarChart } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ModeToggle } from "@/components/mode-toggle"
import { TokenTracker } from "@/components/token-tracker"

export function SiteHeader() {
  const pathname = usePathname()
  
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center">
        <div className="mr-4 flex">
          <Link href="/" className="flex items-center space-x-2">
            <BookOpen className="h-6 w-6" />
            <span className="font-bold">Python Learning</span>
          </Link>
        </div>
        <div className="flex flex-1 items-center space-x-2 justify-between sm:justify-end">
          <nav className="flex items-center space-x-2">
            <Button
              variant={pathname === "/" ? "default" : "ghost"}
              size="sm"
              className="text-sm font-medium"
              asChild
            >
              <Link href="/">
                <Home className="mr-1 h-4 w-4" />
                Home
              </Link>
            </Button>
            <Button
              variant={pathname.startsWith("/exercises") ? "default" : "ghost"}
              size="sm"
              className="text-sm font-medium"
              asChild
            >
              <Link href="/exercises">
                <BookOpen className="mr-1 h-4 w-4" />
                Exercises
              </Link>
            </Button>
            <Button
              variant={pathname === "/dashboard" ? "default" : "ghost"}
              size="sm"
              className="text-sm font-medium"
              asChild
            >
              <Link href="/dashboard">
                <BarChart className="mr-1 h-4 w-4" />
                Dashboard
              </Link>
            </Button>
          </nav>
          
          <div className="flex items-center space-x-4">
            <TokenTracker />
            <ModeToggle />
          </div>
        </div>
      </div>
    </header>
  )
} 