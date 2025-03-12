"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"

interface Chapter {
  title: string
  notebooks: {
    [key: string]: {
      title: string
      exercises: string | string[]
    }
  }
}

interface ExerciseIndex {
  [key: string]: Chapter
}

export default function Exercises() {
  const [chapters, setChapters] = useState<ExerciseIndex | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchExercises() {
      try {
        const response = await fetch("http://localhost:8000/api/exercises/index")
        if (!response.ok) {
          throw new Error("Failed to fetch exercise index")
        }
        const data = await response.json()
        setChapters(data)
      } catch (error) {
        console.error("Error loading exercises:", error)
        setError("Failed to load exercises. Please try again later.")
      } finally {
        setLoading(false)
      }
    }

    fetchExercises()
  }, [])

  return (
    <div className="container py-10">
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="text-3xl font-bold">Python Learning Exercises</h1>
          <p className="text-muted-foreground mt-2">
            Select a chapter to start practicing
          </p>
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

        {chapters && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(chapters)
              .sort(([aKey], [bKey]) => {
                // Sort by chapter number
                const aNum = parseInt(aKey.replace("chapter", ""))
                const bNum = parseInt(bKey.replace("chapter", ""))
                return aNum - bNum
              })
              .map(([key, chapter]) => (
                <Link href={`/exercises/chapter/${key.replace("chapter", "")}`} key={key}>
                  <Card className="h-full transition-all hover:shadow-md hover:border-primary">
                    <CardHeader>
                      <CardTitle>Chapter {key.replace("chapter", "")}</CardTitle>
                      <CardDescription>{chapter.title}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-muted-foreground">
                        {Object.keys(chapter.notebooks).length} topic{Object.keys(chapter.notebooks).length !== 1 ? "s" : ""}
                      </p>
                    </CardContent>
                  </Card>
                </Link>
              ))}
          </div>
        )}
      </div>
    </div>
  )
} 