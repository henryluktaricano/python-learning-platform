"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { CodeEditor } from "@/components/code-editor"
import { Skeleton } from "@/components/ui/skeleton"
import React from "react"

interface Exercise {
  id: string
  title: string
  description: string
  difficulty: string
  instructions: string
  hint?: string
  starterCode?: string
  expectedOutput?: string
  notebook_ref?: string
}

interface ExerciseDetailProps {
  params: {
    exerciseId: string
  }
}

export default function ExerciseDetail({ params }: ExerciseDetailProps) {
  // Get exerciseId directly to avoid React.use() warning
  // This is a workaround until Next.js 15 stabilizes the params API
  const exerciseId = params.exerciseId

  const [exercise, setExercise] = useState<Exercise | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [code, setCode] = useState<string>("")
  const [output, setOutput] = useState<string>("")
  const [draftCode, setDraftCode] = useState<string>("")
  const [draftOutput, setDraftOutput] = useState<string>("")
  const [executeLoading, setExecuteLoading] = useState(false)
  const [markLoading, setMarkLoading] = useState(false)
  const [feedback, setFeedback] = useState<any | null>(null)
  const [notesVisible, setNotesVisible] = useState(false)
  const [notes, setNotes] = useState<string>("")
  const [notesLoading, setNotesLoading] = useState(false)
  const [feedbackVisible, setFeedbackVisible] = useState(false)
  const [editorTheme, setEditorTheme] = useState<string>("")

  useEffect(() => {
    async function fetchExercise() {
      try {
        const response = await fetch(`http://localhost:8000/api/exercises/${exerciseId}`)
        
        if (!response.ok) {
          throw new Error("Failed to fetch exercise")
        }
        
        const data = await response.json()
        setExercise(data)
        
        // If there is starter code, set it
        if (data.starterCode) {
          setCode(data.starterCode)
          setDraftCode(data.starterCode)
        }
      } catch (error) {
        console.error("Error loading exercise:", error)
        setError(`Failed to load exercise ${exerciseId}. Please try again later.`)
      } finally {
        setLoading(false)
      }
    }

    fetchExercise()
  }, [exerciseId])

  const executeCode = async () => {
    setExecuteLoading(true)
    setOutput("")
    
    try {
      const response = await fetch("http://localhost:8000/api/execute_code", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          code: code,
        }),
      })
      
      if (!response.ok) {
        throw new Error("Failed to execute code")
      }
      
      const data = await response.json()
      
      // Check the status field to determine if there was an error
      if (data.status === "error") {
        setOutput(`Error: ${data.error}`)
      } else if (data.jupyter_display && data.expression && data.expression_value) {
        // Format the output to include both regular output and expression value
        const formattedOutput = [
          data.output ? data.output : "",
          data.output && data.output.trim() ? "\n" : "",
          `${data.expression} = ${data.expression_value}`
        ].join('')
        
        setOutput(formattedOutput || "No output generated.")
      } else {
        setOutput(data.output || "No output generated.")
      }
    } catch (error) {
      console.error("Error executing code:", error)
      setOutput("Error: Failed to execute code. Please try again later.")
    } finally {
      setExecuteLoading(false)
    }
  }

  const executeDraftCode = async () => {
    setExecuteLoading(true)
    setDraftOutput("")
    
    try {
      const response = await fetch("http://localhost:8000/api/execute_code", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          code: draftCode,
        }),
      })
      
      if (!response.ok) {
        throw new Error("Failed to execute draft code")
      }
      
      const data = await response.json()
      
      // Check the status field to determine if there was an error
      if (data.status === "error") {
        setDraftOutput(`Error: ${data.error}`)
      } else if (data.jupyter_display && data.expression && data.expression_value) {
        // Format the output to include both regular output and expression value
        const formattedOutput = [
          data.output ? data.output : "",
          data.output && data.output.trim() ? "\n" : "",
          `${data.expression} = ${data.expression_value}`
        ].join('')
        
        setDraftOutput(formattedOutput || "No output generated.")
      } else {
        setDraftOutput(data.output || "No output generated.")
      }
    } catch (error) {
      console.error("Error executing draft code:", error)
      setDraftOutput("Error: Failed to execute code. Please try again later.")
    } finally {
      setExecuteLoading(false)
    }
  }

  const markExercise = async () => {
    if (!exercise) return
    
    setMarkLoading(true)
    
    try {
      const response = await fetch("http://localhost:8000/api/mark_exercise", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          exercise_id: exerciseId,
          code: code,
          expected_output: exercise.expectedOutput,
          question: exercise.instructions,
          metadata: {
            title: exercise.title,
            difficulty: exercise.difficulty,
          },
        }),
      })
      
      if (!response.ok) {
        throw new Error("Failed to mark exercise")
      }
      
      const data = await response.json()
      setFeedback(data.feedback)
      setFeedbackVisible(true)
      setNotesVisible(false)
    } catch (error) {
      console.error("Error marking exercise:", error)
      setError("Failed to mark exercise. Please try again later.")
    } finally {
      setMarkLoading(false)
    }
  }

  const loadNotes = async () => {
    if (!exercise?.notebook_ref) {
      setError("No notes available for this exercise")
      return
    }
    
    setNotesLoading(true)
    
    try {
      const response = await fetch(`http://localhost:8000/api/notes/${exercise.notebook_ref}`)
      
      if (!response.ok) {
        throw new Error("Failed to load notes")
      }
      
      const data = await response.json()
      setNotes(data.markdown)
      setNotesVisible(true)
      setFeedbackVisible(false)
    } catch (error) {
      console.error("Error loading notes:", error)
      setError("Failed to load notes. Please try again later.")
    } finally {
      setNotesLoading(false)
    }
  }

  return (
    <div className="container py-6">
      <div className="flex flex-col gap-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Button variant="outline" size="icon" asChild>
              <Link href="/exercises">
                <ArrowLeft className="h-4 w-4" />
              </Link>
            </Button>
            
            {loading ? (
              <Skeleton className="h-8 w-64" />
            ) : (
              <h1 className="text-2xl font-bold">
                {exercise?.title}
              </h1>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={() => {
              setNotesVisible(!notesVisible);
              if (!notesVisible) setFeedbackVisible(false);
            }} disabled={notesLoading}>
              {notesVisible ? "Hide Notes" : "Show Notes"}
            </Button>
            <Button variant="outline" onClick={markExercise} disabled={markLoading}>
              {markLoading ? "Evaluating..." : "Mark with AI"}
            </Button>
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 gap-6">
            <Card>
              <CardHeader>
                <Skeleton className="h-6 w-1/2" />
                <Skeleton className="h-4 w-3/4" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-4 w-full mb-2" />
                <Skeleton className="h-4 w-full mb-2" />
                <Skeleton className="h-4 w-3/4" />
              </CardContent>
            </Card>
          </div>
        ) : (
          <>
            {error ? (
              <div className="rounded-lg border p-4 bg-muted">
                <p className="text-red-500">{error}</p>
                <p className="mt-2">
                  Make sure the backend server is running at http://localhost:8000
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="md:col-span-2">
                  <Card>
                    <CardHeader>
                      <CardTitle>Exercise: {exercise?.title}</CardTitle>
                      <CardDescription>
                        Difficulty: {exercise?.difficulty}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <p className="font-medium">Instructions</p>
                        <p>{exercise?.instructions}</p>
                      </div>
                      
                      {exercise?.hint && (
                        <div>
                          <p className="font-medium">Hint</p>
                          <p>{exercise?.hint}</p>
                        </div>
                      )}
                      
                      {exercise?.expectedOutput && (
                        <div>
                          <p className="font-medium">Expected Output</p>
                          <pre className="p-2 bg-muted rounded-md overflow-auto">
                            {exercise?.expectedOutput}
                          </pre>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                  
                  <div className="mt-6">
                    <Tabs defaultValue="code">
                      <TabsList>
                        <TabsTrigger value="code">Main Code</TabsTrigger>
                        <TabsTrigger value="draft">Draft/Test Code</TabsTrigger>
                      </TabsList>
                      
                      <TabsContent value="code" className="space-y-4">
                        <Card>
                          <CardHeader>
                            <CardTitle>Your Code</CardTitle>
                            <CardDescription>
                              Write your solution here and run it with Shift+Enter
                            </CardDescription>
                          </CardHeader>
                          <CardContent>
                            <CodeEditor
                              value={code}
                              onChange={setCode}
                              onExecute={executeCode}
                              height="300px"
                              editorTheme={editorTheme}
                              onThemeChange={setEditorTheme}
                            />
                            
                            <div className="mt-4">
                              <p className="font-medium">Output</p>
                              <pre className="p-2 bg-muted rounded-md overflow-auto h-[100px]">
                                {executeLoading ? "Running..." : output || "No output yet. Run your code to see results."}
                              </pre>
                            </div>
                          </CardContent>
                        </Card>
                      </TabsContent>
                      
                      <TabsContent value="draft">
                        <Card>
                          <CardHeader>
                            <CardTitle>Draft Code</CardTitle>
                            <CardDescription>
                              Test your ideas here without affecting your main solution
                            </CardDescription>
                          </CardHeader>
                          <CardContent>
                            <CodeEditor
                              value={draftCode}
                              onChange={setDraftCode}
                              onExecute={executeDraftCode}
                              height="200px"
                              editorTheme={editorTheme}
                              onThemeChange={setEditorTheme}
                            />
                            
                            <div className="mt-4">
                              <p className="font-medium">Output</p>
                              <pre className="p-2 bg-muted rounded-md overflow-auto h-[100px]">
                                {executeLoading ? "Running..." : draftOutput || "No output yet. Run your code to see results."}
                              </pre>
                            </div>
                          </CardContent>
                        </Card>
                      </TabsContent>
                    </Tabs>
                  </div>
                </div>
                
                {notesVisible && (
                  <div className="md:col-span-1">
                    <Card>
                      <CardHeader>
                        <CardTitle>Reference Notes</CardTitle>
                      </CardHeader>
                      <CardContent>
                        {notesLoading ? (
                          <div className="space-y-2">
                            <Skeleton className="h-4 w-full" />
                            <Skeleton className="h-4 w-full" />
                            <Skeleton className="h-4 w-3/4" />
                          </div>
                        ) : (
                          <div className="prose dark:prose-invert max-w-none">
                            {notes ? (
                              <div dangerouslySetInnerHTML={{ __html: notes }} />
                            ) : (
                              <p>No notes available. Click "Show Notes" to load them.</p>
                            )}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                )}

                {feedbackVisible && feedback && (
                  <div className="md:col-span-1">
                    <Card>
                      <CardHeader>
                        <CardTitle>
                          AI Feedback: {feedback.correctness === "CORRECT" ? "✅ Correct" : "❌ Incorrect"}
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div>
                          <p className="font-medium">Overall Feedback</p>
                          <p>{feedback.overall_feedback}</p>
                        </div>
                        
                        <div>
                          <p className="font-medium">Detailed Feedback</p>
                          <p>{feedback.detailed_feedback}</p>
                        </div>
                        
                        {feedback.mistakes && feedback.mistakes.length > 0 && (
                          <div>
                            <p className="font-medium">Mistakes</p>
                            <ul className="list-disc pl-6">
                              {feedback.mistakes.map((mistake: any, i: number) => (
                                <li key={i}>
                                  <p><strong>{mistake.description}</strong></p>
                                  <p>{mistake.suggestion}</p>
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                        
                        {feedback.alternative_solutions && feedback.alternative_solutions.length > 0 && (
                          <div>
                            <p className="font-medium">Alternative Solutions</p>
                            {feedback.alternative_solutions.map((solution: string, i: number) => (
                              <pre key={i} className="p-2 bg-muted rounded-md overflow-auto mt-2">
                                {solution}
                              </pre>
                            ))}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
} 