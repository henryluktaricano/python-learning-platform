"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

interface TokenUsageRecord {
  id: number
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
  model: string
  endpoint: string
  timestamp: string
}

interface TokenUsageData {
  total_tokens: number
  usage_history: TokenUsageRecord[]
}

export default function Dashboard() {
  const [tokenData, setTokenData] = useState<TokenUsageData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchTokenUsage() {
      try {
        const response = await fetch("http://localhost:8000/api/token_usage")
        
        if (!response.ok) {
          throw new Error("Failed to fetch token usage data")
        }
        
        const data = await response.json()
        setTokenData(data)
      } catch (error) {
        console.error("Error loading token usage data:", error)
        setError("Failed to load token usage data. Please try again later.")
      } finally {
        setLoading(false)
      }
    }

    fetchTokenUsage()
  }, [])

  // Format timestamp to a readable date
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleString()
  }

  return (
    <div className="container py-10">
      <div className="flex flex-col gap-8">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            Track your OpenAI API token usage
          </p>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle>Total Tokens</CardTitle>
              <CardDescription>All-time token usage</CardDescription>
            </CardHeader>
            <CardContent>
              {loading ? (
                <Skeleton className="h-10 w-1/2" />
              ) : error ? (
                <p className="text-red-500">Error loading data</p>
              ) : (
                <p className="text-3xl font-bold">
                  {tokenData?.total_tokens?.toLocaleString() || "0"}
                </p>
              )}
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Token Usage History</CardTitle>
            <CardDescription>
              Recent API calls and their token usage
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-2">
                <Skeleton className="h-5 w-full" />
                <Skeleton className="h-5 w-full" />
                <Skeleton className="h-5 w-full" />
              </div>
            ) : error ? (
              <p className="text-red-500">{error}</p>
            ) : tokenData?.usage_history && tokenData.usage_history.length > 0 ? (
              <div className="rounded-md border">
                <div className="grid grid-cols-6 gap-2 p-4 font-medium border-b">
                  <div>Timestamp</div>
                  <div>Endpoint</div>
                  <div>Model</div>
                  <div>Prompt Tokens</div>
                  <div>Completion Tokens</div>
                  <div>Total Tokens</div>
                </div>
                {tokenData.usage_history.map((record) => (
                  <div key={record.id} className="grid grid-cols-6 gap-2 p-4 border-b last:border-0 text-sm">
                    <div>{formatTimestamp(record.timestamp)}</div>
                    <div>{record.endpoint || "N/A"}</div>
                    <div>{record.model}</div>
                    <div>{record.prompt_tokens.toLocaleString()}</div>
                    <div>{record.completion_tokens.toLocaleString()}</div>
                    <div>{record.total_tokens.toLocaleString()}</div>
                  </div>
                ))}
              </div>
            ) : (
              <p>No token usage data available yet.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
} 