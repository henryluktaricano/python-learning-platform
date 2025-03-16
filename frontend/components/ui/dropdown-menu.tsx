import * as React from "react"
import { cn } from "@/lib/utils"

export interface DropdownMenuProps {
  children: React.ReactNode
}

export function DropdownMenu({ children }: DropdownMenuProps) {
  return <div className="relative">{children}</div>
}

export interface DropdownMenuTriggerProps {
  asChild?: boolean
  children: React.ReactNode
  onClick?: () => void
}

export function DropdownMenuTrigger({ asChild = false, children, onClick }: DropdownMenuTriggerProps) {
  return (
    <div 
      className="cursor-pointer" 
      onClick={(e) => {
        e.stopPropagation()
        onClick && onClick()
      }}
    >
      {children}
    </div>
  )
}

export interface DropdownMenuContentProps {
  align?: "start" | "end" | "center"
  side?: "top" | "right" | "bottom" | "left"
  sideOffset?: number
  className?: string
  children: React.ReactNode
  open?: boolean
}

export function DropdownMenuContent({
  align = "center",
  side = "bottom",
  sideOffset = 4,
  className,
  children,
  open = false
}: DropdownMenuContentProps) {
  if (!open) return null;
  
  return (
    <div 
      className={cn(
        "z-[100] min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md absolute",
        side === "top" && "bottom-full mb-2",
        side === "bottom" && "top-full mt-2",
        align === "start" && "left-0",
        align === "center" && "left-1/2 -translate-x-1/2",
        align === "end" && "right-0",
        className
      )}
    >
      {children}
    </div>
  )
}

export interface DropdownMenuItemProps {
  className?: string
  onClick?: () => void
  children: React.ReactNode
}

export function DropdownMenuItem({
  className,
  onClick,
  children,
}: DropdownMenuItemProps) {
  return (
    <div
      className={cn(
        "relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-accent hover:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
        className
      )}
      onClick={(e) => {
        e.stopPropagation()
        onClick && onClick()
      }}
    >
      {children}
    </div>
  )
} 