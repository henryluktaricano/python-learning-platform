"use client"

import React, { useCallback, useState, useRef, useEffect } from "react"
import { cn } from "@/lib/utils"
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { ChevronDown, Lightbulb } from 'lucide-react'
import { useTheme } from 'next-themes'
import { search } from '@codemirror/search'
import { EditorView, KeyBinding } from '@codemirror/view'
import { keymap } from '@codemirror/view'
import { Extension } from '@codemirror/state'
import { autocompletion } from '@codemirror/autocomplete'

// Import themes
import { dracula } from '@uiw/codemirror-theme-dracula'
import { materialDark } from '@uiw/codemirror-theme-material'
import { sublime } from '@uiw/codemirror-theme-sublime'
import { githubLight } from '@uiw/codemirror-theme-github'
import { xcodeLight } from '@uiw/codemirror-theme-xcode'
import { nord } from '@uiw/codemirror-theme-nord'

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

// Theme options
const themes = {
  'dracula': dracula,
  'material-dark': materialDark,
  'sublime': sublime,
  'github-light': githubLight,
  'xcode-light': xcodeLight,
  'nord': nord,
}

// Storage key for persisting themes
const EDITOR_THEME_STORAGE_KEY = 'python-learning-platform-editor-theme'
const RECOMMENDATIONS_STORAGE_KEY = 'python-learning-platform-recommendations-enabled'

// Function to load theme from localStorage
const loadStoredTheme = (): string | null => {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(EDITOR_THEME_STORAGE_KEY)
}

// Function to load recommendations setting from localStorage
const loadStoredRecommendationsSetting = (): boolean | null => {
  if (typeof window === 'undefined') return null
  const stored = localStorage.getItem(RECOMMENDATIONS_STORAGE_KEY)
  return stored ? JSON.parse(stored) : null
}

interface CodeEditorProps {
  value: string
  onChange: (value: string) => void
  onExecute?: () => void
  height?: string
  className?: string
  editorTheme?: string
  onThemeChange?: (theme: string) => void
}

export function CodeEditor({
  value,
  onChange,
  onExecute,
  height = "200px",
  className,
  editorTheme: externalEditorTheme,
  onThemeChange,
}: CodeEditorProps) {
  const { theme } = useTheme()
  const systemTheme = theme === 'dark' ? 'dracula' : 'github-light'
  
  // Initialize from localStorage or props or system theme
  const [internalEditorTheme, setInternalEditorTheme] = useState<string>(() => {
    const storedTheme = loadStoredTheme()
    return externalEditorTheme || storedTheme || systemTheme
  })

  // Use either the external theme (if provided) or the internal theme
  const currentEditorTheme = externalEditorTheme || internalEditorTheme

  const [showSearch, setShowSearch] = useState<boolean>(false)
  const [recommendationsEnabled, setRecommendationsEnabled] = useState<boolean>(() => {
    const storedSetting = loadStoredRecommendationsSetting()
    return storedSetting !== null ? storedSetting : true
  })
  const [editorView, setEditorView] = useState<EditorView | null>(null)
  const editorRef = useRef<HTMLDivElement>(null)

  // Update state when external theme changes
  useEffect(() => {
    if (externalEditorTheme) {
      setInternalEditorTheme(externalEditorTheme)
    }
  }, [externalEditorTheme])

  // Save theme to localStorage when it changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(EDITOR_THEME_STORAGE_KEY, currentEditorTheme)
    }
  }, [currentEditorTheme])

  // Save recommendations setting to localStorage when it changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(RECOMMENDATIONS_STORAGE_KEY, JSON.stringify(recommendationsEnabled))
    }
  }, [recommendationsEnabled])

  // Create a custom keymap for Shift+Enter with prevention of default behavior
  const createShiftEnterKeymap = useCallback(() => {
    const shiftEnterBinding: KeyBinding = {
      key: "Shift-Enter",
      run: (view) => {
        onExecute?.()
        return true
      },
      preventDefault: true, // This is crucial for preventing the default behavior
      stopPropagation: true // Also stop propagation
    }

    return keymap.of([shiftEnterBinding])
  }, [onExecute])

  // Apply global event listener to capture Shift+Enter at DOM level
  useEffect(() => {
    const handleGlobalKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && e.shiftKey && editorRef.current?.contains(e.target as Node)) {
        e.preventDefault()
        e.stopPropagation()
        onExecute?.()
      }
      
      // Add keyboard shortcut for search (still available via keyboard)
      if ((e.key === 'f' || e.key === 'F') && (e.ctrlKey || e.metaKey) && editorRef.current?.contains(e.target as Node)) {
        e.preventDefault()
        setShowSearch(true)
      }
      
      // Close search with Escape
      if (e.key === 'Escape' && showSearch && editorRef.current?.contains(e.target as Node)) {
        setShowSearch(false)
      }
    }
    
    window.addEventListener('keydown', handleGlobalKeyDown, true)
    return () => window.removeEventListener('keydown', handleGlobalKeyDown, true)
  }, [onExecute, showSearch])

  // Determine which extensions to use
  const getExtensions = useCallback(() => {
    const extensions: Extension[] = [
      python(), 
      createShiftEnterKeymap()
    ]
    
    if (showSearch) {
      extensions.push(search({ top: true }))
    }

    // Add autocompletion extension only if recommendations are enabled
    if (recommendationsEnabled) {
      extensions.push(autocompletion())
    }
    
    return extensions
  }, [showSearch, createShiftEnterKeymap, recommendationsEnabled])

  const handleChange = useCallback((value: string) => {
    onChange(value)
  }, [onChange])

  // This handles other keyboard shortcuts not covered by the keymap extension
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    // Additional check for Shift+Enter with more aggressive prevention
    if (e.key === 'Enter' && e.shiftKey) {
      e.preventDefault()
      e.stopPropagation()
      onExecute?.()
      return false
    }
  }, [onExecute])

  // Handle editor creation
  const handleEditorCreation = useCallback((view: EditorView) => {
    setEditorView(view)
  }, [])

  // Toggle recommendations
  const toggleRecommendations = useCallback(() => {
    setRecommendationsEnabled(prev => !prev)
  }, [])

  // Handle theme changes
  const handleThemeChange = useCallback((newTheme: string) => {
    if (onThemeChange) {
      onThemeChange(newTheme)
    } else {
      setInternalEditorTheme(newTheme)
    }
  }, [onThemeChange])

  return (
    <div 
      ref={editorRef}
      className={cn("relative rounded-md border overflow-hidden", className)}
      style={{ height }}
      onKeyDown={handleKeyDown}
    >
      <CodeMirror
        value={value}
        onChange={handleChange}
        height={height}
        theme={themes[currentEditorTheme as keyof typeof themes]}
        extensions={getExtensions()}
        basicSetup={{
          lineNumbers: true,
          highlightActiveLineGutter: true,
          highlightSpecialChars: true,
          foldGutter: true,
          dropCursor: true,
          allowMultipleSelections: true,
          indentOnInput: true,
          syntaxHighlighting: true,
          bracketMatching: true,
          closeBrackets: true,
          autocompletion: recommendationsEnabled, // Use the state to control autocompletion
          rectangularSelection: true,
          crosshairCursor: true,
          highlightActiveLine: true,
          highlightSelectionMatches: true,
          closeBracketsKeymap: true,
          searchKeymap: true,
          foldKeymap: true,
          completionKeymap: recommendationsEnabled, // Also control the keymaps
          lintKeymap: true,
        }}
        placeholder="# Write your Python code here"
        onKeyDown={handleKeyDown}
        onCreateEditor={handleEditorCreation}
      />
      
      <div className="absolute top-2 right-2 flex gap-2">
        <TooltipProvider delayDuration={300}>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button 
                variant="ghost" 
                size="icon" 
                className={cn(
                  "h-6 w-6 rounded-full bg-background text-muted-foreground hover:bg-muted hover:text-foreground",
                  recommendationsEnabled && "text-amber-500 hover:text-amber-600"
                )}
                onClick={toggleRecommendations}
              >
                <Lightbulb className="h-3.5 w-3.5" />
              </Button>
            </TooltipTrigger>
            <TooltipContent side="bottom">
              {recommendationsEnabled ? 'Disable recommendations' : 'Enable recommendations'}
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
        
        <TooltipProvider delayDuration={300}>
          <Tooltip>
            <TooltipTrigger asChild>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-6 w-6 rounded-full bg-background text-muted-foreground hover:bg-muted hover:text-foreground" 
                  >
                    <ChevronDown className="h-3.5 w-3.5" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent 
                  align="end" 
                  className="w-40 rounded-md border bg-popover/95 p-1 text-popover-foreground shadow-md backdrop-blur-sm"
                  side="top"
                  sideOffset={5}
                >
                  <DropdownMenuItem 
                    onClick={() => handleThemeChange('dracula')}
                    className="rounded-sm hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
                  >
                    Dracula
                  </DropdownMenuItem>
                  <DropdownMenuItem 
                    onClick={() => handleThemeChange('material-dark')}
                    className="rounded-sm hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
                  >
                    Material Dark
                  </DropdownMenuItem>
                  <DropdownMenuItem 
                    onClick={() => handleThemeChange('sublime')}
                    className="rounded-sm hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
                  >
                    Sublime
                  </DropdownMenuItem>
                  <DropdownMenuItem 
                    onClick={() => handleThemeChange('github-light')}
                    className="rounded-sm hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
                  >
                    GitHub Light
                  </DropdownMenuItem>
                  <DropdownMenuItem 
                    onClick={() => handleThemeChange('xcode-light')}
                    className="rounded-sm hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
                  >
                    Xcode Light
                  </DropdownMenuItem>
                  <DropdownMenuItem 
                    onClick={() => handleThemeChange('nord')}
                    className="rounded-sm hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
                  >
                    Nord
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </TooltipTrigger>
            <TooltipContent side="bottom">
              Change theme
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
    </div>
  )
}