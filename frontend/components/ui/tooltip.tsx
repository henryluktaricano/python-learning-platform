import * as React from "react"
import { cn } from "@/lib/utils"

export interface TooltipProviderProps {
  delayDuration?: number
  children: React.ReactNode
}

export function TooltipProvider({ delayDuration = 300, children }: TooltipProviderProps) {
  return <>{children}</>
}

export interface TooltipProps {
  children: React.ReactNode
}

export function Tooltip({ children }: TooltipProps) {
  return <div className="relative">{children}</div>
}

export interface TooltipTriggerProps {
  asChild?: boolean
  children: React.ReactNode
}

export function TooltipTrigger({ asChild = false, children }: TooltipTriggerProps) {
  return <div className="inline-block">{children}</div>
}

export interface TooltipContentProps {
  className?: string
  side?: "top" | "right" | "bottom" | "left"
  sideOffset?: number
  children: React.ReactNode
}

export function TooltipContent({ className, side = "top", sideOffset = 4, children }: TooltipContentProps) {
  return (
    <div
      className={cn(
        "z-50 overflow-hidden rounded-md bg-primary px-3 py-1.5 text-xs text-primary-foreground animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",
        className
      )}
    >
      {children}
    </div>
  )
} 