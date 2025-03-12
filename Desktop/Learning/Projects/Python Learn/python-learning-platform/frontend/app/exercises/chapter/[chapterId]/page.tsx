"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { ArrowLeft } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import React from "react"

interface Notebook {
  title: string
  exercises: string | string[]
}

interface Chapter {
  title: string
  notebooks: {
    [key: string]: Notebook
  }
}

interface ChapterDetailProps {
  params: {
    chapterId: string
  }
}

export default function ChapterDetail({ params }: ChapterDetailProps) {
  // Get chapterId directly to avoid React.use() warning
  // This is a workaround until Next.js 15 stabilizes the params API
  const chapterId = params.chapterId

  const [chapter, setChapter] = useState<Chapter | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchChapter() {
      try {
        const response = await fetch(`http://localhost:8000/api/exercises/index`)
        if (!response.ok) {
          throw new Error("Failed to fetch chapter data")
        }
        
        const data = await response.json()
        const chapterKey = `chapter${chapterId}`
        
        if (!data[chapterKey]) {
          throw new Error(`Chapter ${chapterId} not found`)
        }
        
        setChapter(data[chapterKey])
      } catch (error) {
        console.error("Error loading chapter:", error)
        setError(`Failed to load chapter ${chapterId}. Please try again later.`)
      } finally {
        setLoading(false)
      }
    }

    fetchChapter()
  }, [chapterId])

  return (
    <div className="container py-10">
      <div className="flex flex-col gap-6">
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon" asChild>
            <Link href="/exercises">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          
          {loading ? (
            <Skeleton className="h-8 w-64" />
          ) : (
            <h1 className="text-3xl font-bold">
              Chapter {chapterId}: {chapter?.title}
            </h1>
          )}
        </div>

        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array(6).fill(0).map((_, i) => (
              <Card key={i} className="h-48">
                <CardHeader>
                  <Skeleton className="h-6 w-1/2 mb-2" />
                  <Skeleton className="h-4 w-3/4" />
                </CardHeader>
                <CardContent>
                  <Skeleton className="h-4 w-full mb-2" />
                  <Skeleton className="h-4 w-2/3" />
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {error && (
          <div className="rounded-lg border p-4 bg-muted">
            <p className="text-red-500">{error}</p>
            <p className="mt-2">
              Make sure the backend server is running at http://localhost:8000
            </p>
          </div>
        )}

        {chapter && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(chapter.notebooks).map(([notebookKey, notebook]) => {
              // Handle both single exercise and array of exercises
              const exercises = Array.isArray(notebook.exercises) 
                ? notebook.exercises 
                : [notebook.exercises]
              
              return (
                <Card key={notebookKey} className="h-full">
                  <CardHeader>
                    <CardTitle>{notebook.title}</CardTitle>
                    <CardDescription>
                      {exercises.length} exercise{exercises.length !== 1 ? 's' : ''}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-col gap-2">
                      {exercises.map((exercise, index) => {
                        // Extract the exercise name from the file name
                        const exerciseName = exercise.replace('.json', '')
                        
                        return (
                          <Button 
                            key={exercise} 
                            variant="outline" 
                            className="justify-start"
                            asChild
                          >
                            <Link href={`/exercises/exercise/${exerciseName}`}>
                              Exercise {index + 1}
                            </Link>
                          </Button>
                        )
                      })}
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
} 