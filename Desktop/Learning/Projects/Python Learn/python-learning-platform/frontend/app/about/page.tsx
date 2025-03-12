export default function AboutPage() {
  return (
    <div className="container py-10">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">About Python Learning Platform</h1>
        
        <div className="prose dark:prose-invert max-w-none">
          <p>
            The Python Learning Platform is an interactive, notebook-style learning environment
            designed to help you master Python programming through hands-on practice and
            AI-assisted feedback.
          </p>
          
          <h2>Key Features</h2>
          
          <ul>
            <li>
              <strong>Interactive Code Execution:</strong> Write and run Python code directly
              in your browser with a notebook-like interface.
            </li>
            <li>
              <strong>Structured Learning Path:</strong> Follow a carefully organized curriculum
              with progressive chapters and exercises.
            </li>
            <li>
              <strong>AI-Powered Feedback:</strong> Get detailed, personalized feedback on your
              code using advanced AI models.
            </li>
            <li>
              <strong>Reference Material:</strong> Access helpful notes and explanations for each
              topic as you learn.
            </li>
            <li>
              <strong>Dark Mode Support:</strong> Choose between light and dark themes for
              comfortable coding in any environment.
            </li>
          </ul>
          
          <h2>Technical Stack</h2>
          
          <p>
            This platform is built using modern web technologies:
          </p>
          
          <ul>
            <li><strong>Frontend:</strong> Next.js, React, TailwindCSS, ShadcnUI</li>
            <li><strong>Backend:</strong> FastAPI, Python</li>
            <li><strong>AI Integration:</strong> OpenAI API (GPT models)</li>
            <li><strong>Data Storage:</strong> SQLite (for token usage and feedback storage)</li>
          </ul>
          
          <h2>About the Project</h2>
          
          <p>
            This platform was developed as an educational tool to make Python learning more
            interactive and feedback-driven. The aim is to provide a more engaging learning
            experience compared to traditional static tutorials or courses.
          </p>
          
          <p>
            All code execution happens in a sandboxed environment, and the AI provides
            personalized feedback to help you improve your coding skills.
          </p>
        </div>
      </div>
    </div>
  )
} 