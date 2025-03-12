import Link from "next/link"
import { ArrowRight, BookOpen, Code, LucideZap } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function Home() {
  return (
    <div className="flex flex-col min-h-[calc(100vh-4rem)]">
      {/* Hero Section */}
      <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48">
        <div className="container px-4 md:px-6">
          <div className="grid gap-6 lg:grid-cols-2 lg:gap-12 xl:grid-cols-2">
            <div className="flex flex-col justify-center space-y-4">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none">
                  Learn Python Interactively
                </h1>
                <p className="max-w-[600px] text-muted-foreground md:text-xl">
                  Practice Python programming with instant execution and AI-powered feedback to accelerate your learning
                </p>
              </div>
              <div className="flex flex-col gap-2 min-[400px]:flex-row">
                <Button asChild size="lg">
                  <Link href="/exercises">
                    Start Learning
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button variant="outline" size="lg" asChild>
                  <Link href="/about">
                    Learn More
                  </Link>
                </Button>
              </div>
            </div>
            <div className="flex items-center justify-center">
              <div className="rounded-xl border bg-card p-8 shadow-sm">
                <div className="flex flex-col space-y-2">
                  <div className="rounded-md bg-muted p-2 text-sm text-muted-foreground">
                    <pre><code>{'def hello_world():\n    print("Hello, Python Learning Platform!")\n\nhello_world()'}</code></pre>
                  </div>
                  <div className="rounded-md bg-muted/50 p-2 text-sm">
                    <p>Output:</p>
                    <p className="text-green-600 dark:text-green-400">Hello, Python Learning Platform!</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="w-full py-12 md:py-24 lg:py-32 bg-muted/40">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col items-center justify-center space-y-4 text-center">
            <div className="space-y-2">
              <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">Key Features</h2>
              <p className="max-w-[900px] text-muted-foreground md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                Everything you need to learn Python effectively
              </p>
            </div>
          </div>
          <div className="mx-auto grid max-w-5xl grid-cols-1 gap-6 py-12 md:grid-cols-3">
            <div className="flex flex-col items-center space-y-2 rounded-lg p-4">
              <div className="rounded-full border bg-background p-2.5">
                <Code className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">Interactive Coding</h3>
              <p className="text-center text-muted-foreground">
                Write and execute Python code directly in your browser with instant feedback
              </p>
            </div>
            <div className="flex flex-col items-center space-y-2 rounded-lg p-4">
              <div className="rounded-full border bg-background p-2.5">
                <LucideZap className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">AI Evaluation</h3>
              <p className="text-center text-muted-foreground">
                Get detailed feedback and suggestions from AI to improve your code
              </p>
            </div>
            <div className="flex flex-col items-center space-y-2 rounded-lg p-4">
              <div className="rounded-full border bg-background p-2.5">
                <BookOpen className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-bold">Structured Learning</h3>
              <p className="text-center text-muted-foreground">
                Follow a comprehensive curriculum with organized chapters and exercises
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="w-full py-12 md:py-24 lg:py-32">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col items-center justify-center space-y-4 text-center">
            <div className="space-y-2">
              <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">Ready to Start Learning?</h2>
              <p className="max-w-[600px] text-muted-foreground md:text-xl">
                Jump into our interactive Python exercises and start coding right away
              </p>
            </div>
            <div className="flex flex-col gap-2 min-[400px]:flex-row">
              <Button asChild size="lg">
                <Link href="/exercises">
                  Start Learning
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
