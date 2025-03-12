"use client"

import { useState, useEffect } from "react"
import { Coins } from "lucide-react"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

interface TokenUsage {
  total_tokens: number
  model_breakdown: {
    [key: string]: number
  }
  estimated_cost_usd: number
}

export function TokenTracker() {
  const [tokenUsage, setTokenUsage] = useState<TokenUsage | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchTokenUsage() {
      try {
        const response = await fetch("http://localhost:8000/api/token_usage/summary")
        
        if (!response.ok) {
          throw new Error("Failed to fetch token usage")
        }
        
        const data = await response.json()
        setTokenUsage(data)
      } catch (error) {
        console.error("Error loading token usage:", error)
        setError("Failed to load token usage")
      } finally {
        setLoading(false)
      }
    }

    fetchTokenUsage()
    
    // Refresh token usage every 60 seconds
    const intervalId = setInterval(fetchTokenUsage, 60000)
    
    return () => clearInterval(intervalId)
  }, [])

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="flex items-center gap-1 px-2 py-1 rounded-md bg-muted hover:bg-muted/80 cursor-help">
            <Coins className="h-4 w-4" />
            <span>
              {loading
                ? "Loading..."
                : error
                ? "Error"
                : tokenUsage
                ? `${tokenUsage.total_tokens.toLocaleString()} tokens`
                : "No data"}
            </span>
          </div>
        </TooltipTrigger>
        <TooltipContent>
          {loading ? (
            <p>Loading token usage data...</p>
          ) : error ? (
            <p>Error loading token usage: {error}</p>
          ) : tokenUsage ? (
            <div className="space-y-2">
              <p><strong>Total tokens used:</strong> {tokenUsage.total_tokens.toLocaleString()}</p>
              <p><strong>Estimated cost:</strong> ${tokenUsage.estimated_cost_usd.toFixed(4)}</p>
              <div>
                <p><strong>Model breakdown:</strong></p>
                <ul className="pl-2">
                  {Object.entries(tokenUsage.model_breakdown).map(([model, tokens]) => (
                    <li key={model}>
                      {model}: {tokens.toLocaleString()} tokens
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <p>No token usage data available</p>
          )}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
} 