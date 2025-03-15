'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import PageLayout from '../../../components/PageLayout';

// Import CodeEditor with dynamic loading to avoid SSR issues with CodeMirror
const CodeEditor = dynamic(
  () => import('../../../../components/code-editor').then(mod => ({ default: mod.CodeEditor })),
  { ssr: false }
);

// Constants for localStorage keys
const EDITOR_THEME_STORAGE_KEY = 'python-learning-platform-editor-theme';

// Function to load theme from localStorage
const loadStoredTheme = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(EDITOR_THEME_STORAGE_KEY);
};

// API URL configuration
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003/api';
const EXECUTE_ENDPOINT = `${API_URL}/execute-code`;

// Output theme styles mapping to match editor themes
const outputThemeStyles = {
  'dracula': {
    background: 'bg-[#282a36]',
    text: 'text-[#f8f8f2]',
    border: 'border-[#44475a]'
  },
  'material-dark': {
    background: 'bg-[#263238]',
    text: 'text-[#EEFFFF]',
    border: 'border-[#37474F]'
  },
  'sublime': {
    background: 'bg-[#272822]', 
    text: 'text-[#f8f8f2]',
    border: 'border-[#3e3d32]'
  },
  'github-light': {
    background: 'bg-[#ffffff]',
    text: 'text-[#24292e]',
    border: 'border-[#e1e4e8]'
  },
  'xcode-light': {
    background: 'bg-[#ffffff]',
    text: 'text-[#1F1F24]',
    border: 'border-[#d9d9d9]'
  },
  'nord': {
    background: 'bg-[#2e3440]',
    text: 'text-[#d8dee9]',
    border: 'border-[#3b4252]'
  }
};

// Default output theme for fallback
const defaultOutputTheme = {
  background: 'bg-gray-900',
  text: 'text-white',
  border: 'border-gray-700'
};

interface PageProps {
  params: {
    exerciseId: string;
  };
}

// Fetch a specific exercise by ID
async function getExercise(exerciseId: string) {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003/api';
  
  try {
    const response = await fetch(`${API_URL}/exercises/exercise/${exerciseId}`, { 
      next: { revalidate: 3600 } 
    });
    
    if (!response.ok) throw new Error('Failed to fetch exercise');
    return response.json();
  } catch (error) {
    console.error(`Error fetching exercise ${exerciseId}:`, error);
    return null;
  }
}

// Fetch all exercises for a topic to enable navigation between exercises
async function getExercisesForTopic(topicId: string) {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003/api';
  
  try {
    const response = await fetch(`${API_URL}/exercises/topics/${topicId}`, { 
      next: { revalidate: 3600 } 
    });
    
    if (!response.ok) throw new Error('Failed to fetch exercises for topic');
    return response.json();
  } catch (error) {
    console.error(`Error fetching exercises for topic ${topicId}:`, error);
    return [];
  }
}

// Mock data for development and fallback
const mockExercise = {
  id: "list-comprehension",
  title: "List Comprehension",
  topic_id: "lists",
  topic_title: "Lists and Tuples",
  chapter_title: "Data Structures",
  exercise_number: 4,
  total_exercises: 12,
  difficulty: "intermediate",
  instructions: "Create a list comprehension that generates a list of squares for numbers from 1 to 10.",
  starterCode: "squares = [x**2 for x in range(1, 11)]",
  solution: "squares = [x**2 for x in range(1, 11)]",
  description: "List comprehensions provide a concise way to create lists based on existing lists or other iterables.",
  notes: `
    <h2>Python List Comprehension Notes</h2>
    <p>List comprehension provides a concise way to create lists based on existing lists or other sequences.</p>
    
    <div class="code-sample">
      new_list = [expression for item in iterable
      if condition]
    </div>
    
    <ul>
      <li>expression: the operation to perform on each item</li>
      <li>item: the variable name for each element</li>
      <li>iterable: the sequence to iterate over</li>
      <li>condition: optional filtering criteria</li>
    </ul>
  `
};

const mockTopicExercises = [
  { id: "list-basics", title: "List Basics", exercise_number: 1 },
  { id: "list-methods", title: "List Methods", exercise_number: 2 },
  { id: "list-slicing", title: "List Slicing", exercise_number: 3 },
  { id: "list-comprehension", title: "List Comprehension", exercise_number: 4 },
  { id: "tuple-basics", title: "Tuple Basics", exercise_number: 5 }
];

export default function ExercisePage({ params }: PageProps) {
  const { exerciseId } = params;
  const [exercise, setExercise] = useState(mockExercise);
  const [activeTab, setActiveTab] = useState<'main' | 'scratchbook'>('main');
  const [code, setCode] = useState(exercise.starterCode || "");
  const [scratchCode, setScratchCode] = useState("");
  const [output, setOutput] = useState('');
  const [showNotes, setShowNotes] = useState(false);
  const [executeLoading, setExecuteLoading] = useState(false);
  
  // Initialize editorTheme from localStorage or fall back to a default
  const [editorTheme, setEditorTheme] = useState<string>(() => {
    const storedTheme = loadStoredTheme();
    return storedTheme || 'dracula';
  });
  
  // Save theme to localStorage whenever it changes
  useEffect(() => {
    if (typeof window !== 'undefined' && editorTheme) {
      localStorage.setItem(EDITOR_THEME_STORAGE_KEY, editorTheme);
    }
  }, [editorTheme]);
  
  // Handle theme changes
  const handleThemeChange = (newTheme: string) => {
    setEditorTheme(newTheme);
  };
  
  // Effect to fetch the exercise data when the ID changes
  useEffect(() => {
    const fetchExerciseData = async () => {
      try {
        const data = await getExercise(exerciseId);
        if (data) {
          setExercise(data);
          // Clean any placeholder comments from the starter code
          const cleanedCode = data.starterCode 
            ? data.starterCode.replace(/^#.*Your code here.*$/m, "").replace(/^#.*[Ww]rite.*code.*$/m, "")
            : "";
          setCode(cleanedCode);
        }
      } catch (error) {
        console.error("Failed to fetch exercise:", error);
      }
    };
    
    fetchExerciseData();
  }, [exerciseId]);
  
  // Get all exercises for this topic to enable next/previous navigation
  const topicExercises = mockTopicExercises;
  
  // Find the current exercise index in the topic exercises
  const currentIndex = topicExercises.findIndex((ex: any) => ex.id === exerciseId);
  const prevExercise = currentIndex > 0 ? topicExercises[currentIndex - 1] : null;
  const nextExercise = currentIndex < topicExercises.length - 1 ? topicExercises[currentIndex + 1] : null;
  
  const executeCode = async () => {
    setExecuteLoading(true);
    setOutput('');  // Clear output immediately to show something is happening
    
    try {
      let codeToRun = activeTab === 'main' ? code : scratchCode;
      
      // Process code to handle Jupyter-like behavior (auto-printing variables on their own line)
      codeToRun = processPythonCodeJupyterStyle(codeToRun);
      
      // Use a direct fetch with the predefined endpoint for faster execution
      const response = await fetch(EXECUTE_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code: codeToRun }),
      });
      
      if (!response.ok) {
        throw new Error(`Error ${response.status}: Failed to execute code`);
      }
      
      const data = await response.json();
      if (data.error) {
        setOutput(data.error);
      } else {
        setOutput(data.output || 'Code executed successfully (no output)');
      }
    } catch (error) {
      console.error('Error executing code:', error);
      setOutput('Error executing code: ' + (error instanceof Error ? error.message : String(error)));
    } finally {
      setExecuteLoading(false);
    }
  };
  
  // Function to process Python code to mimic Jupyter notebook behavior
  const processPythonCodeJupyterStyle = (code: string): string => {
    // Split code into lines and remove empty lines
    const lines = code.split('\n').filter(line => line.trim().length > 0);
    
    if (lines.length === 0) return code;
    
    // Get the last line
    const lastLine = lines[lines.length - 1].trim();
    
    // Check if the last line is just a variable name (no assignment, no function calls)
    // This regex matches a valid Python variable name that's not part of an assignment or function call
    const variableNameRegex = /^[a-zA-Z_][a-zA-Z0-9_]*$/;
    
    if (variableNameRegex.test(lastLine)) {
      // Replace the last line with a print statement
      lines[lines.length - 1] = `print(${lastLine})`;
      return lines.join('\n');
    }
    
    // Also handle expressions with semicolons (like `result;`)
    const semicolonRegex = /^([a-zA-Z_][a-zA-Z0-9_]*);$/;
    const semicolonMatch = lastLine.match(semicolonRegex);
    
    if (semicolonMatch) {
      // Replace the last line with a print statement (remove the semicolon)
      lines[lines.length - 1] = `print(${semicolonMatch[1]})`;
      return lines.join('\n');
    }
    
    return code;
  };
  
  return (
    <PageLayout>
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Header with Back Button */}
        <div className="flex justify-between items-center mb-8">
          <Link
            href={`/exercises/topics/${exercise.topic_id}`}
            className="flex items-center text-gray-700 hover:text-python-blue transition-colors font-medium"
          >
            <svg className="w-5 h-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Exercise List
          </Link>
        </div>
        
        {/* Exercise Navigation */}
        <div className="flex justify-between items-center mb-6">
          <Link
            href={prevExercise ? `/exercises/exercise/${prevExercise.id}` : '#'}
            className={`px-4 py-2 border border-gray-300 rounded flex items-center ${!prevExercise ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-100'}`}
            onClick={(e) => !prevExercise && e.preventDefault()}
          >
            <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Previous
          </Link>
          
          <div className="text-gray-700 font-medium">
            Exercise {exercise.exercise_number} of {exercise.total_exercises}
          </div>
          
          <Link
            href={nextExercise ? `/exercises/exercise/${nextExercise.id}` : '#'}
            className={`px-4 py-2 border border-gray-300 rounded flex items-center ${!nextExercise ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-100'}`}
            onClick={(e) => !nextExercise && e.preventDefault()}
          >
            Next
            <svg className="w-4 h-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content - Exercise and Editor */}
          <div className="lg:col-span-2">
            {/* Exercise Title and Description */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <p className="text-lg text-gray-800 mb-0 leading-relaxed">{exercise.instructions}</p>
            </div>
            
            {/* Editor Tabs */}
            <div className="flex border-b border-gray-200 mb-2">
              <button
                className={`px-4 py-2 font-medium text-sm focus:outline-none ${
                  activeTab === 'main'
                    ? 'border-b-2 border-python-blue text-python-blue'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
                onClick={() => setActiveTab('main')}
              >
                Main Editor
              </button>
              <button
                className={`px-4 py-2 font-medium text-sm focus:outline-none ${
                  activeTab === 'scratchbook'
                    ? 'border-b-2 border-python-blue text-python-blue'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
                onClick={() => setActiveTab('scratchbook')}
              >
                Scratchbook
              </button>
            </div>
            
            {/* Code Editor */}
            <div className="bg-white rounded-lg shadow-md overflow-hidden p-4">
              {activeTab === 'main' ? (
                <CodeEditor 
                  value={code}
                  onChange={setCode}
                  onExecute={executeCode}
                  height="400px"
                  editorTheme={editorTheme}
                  onThemeChange={handleThemeChange}
                  className="border-0"
                />
              ) : (
                <CodeEditor 
                  value={scratchCode}
                  onChange={setScratchCode}
                  onExecute={executeCode}
                  height="400px"
                  editorTheme={editorTheme}
                  onThemeChange={handleThemeChange}
                  className="border-0"
                />
              )}
              
              {/* Run Code Button with Loading State */}
              <div className="mt-4 flex justify-end">
                <button
                  onClick={executeCode}
                  disabled={executeLoading}
                  className={`px-4 py-2 rounded font-medium text-white transition-colors ${
                    executeLoading ? 'bg-gray-500 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'
                  }`}
                >
                  {executeLoading ? (
                    <>
                      <span className="inline-block animate-spin mr-2">⟳</span>
                      Running...
                    </>
                  ) : (
                    'Run Code (Shift+Enter)'
                  )}
                </button>
              </div>
            </div>
            
            {/* Output Display */}
            <div className={`mt-6 p-4 rounded-lg overflow-hidden shadow-md border ${
              !output && !executeLoading ? 'hidden' : ''
            } ${
              outputThemeStyles[editorTheme as keyof typeof outputThemeStyles]?.background || defaultOutputTheme.background
            } ${
              outputThemeStyles[editorTheme as keyof typeof outputThemeStyles]?.text || defaultOutputTheme.text
            } ${
              outputThemeStyles[editorTheme as keyof typeof outputThemeStyles]?.border || defaultOutputTheme.border
            }`}>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-semibold">Output</h3>
                <button 
                  onClick={() => setOutput('')}
                  className={`${
                    outputThemeStyles[editorTheme as keyof typeof outputThemeStyles]?.text || 'text-gray-300'
                  } hover:opacity-70`}
                  disabled={executeLoading}
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              {executeLoading && !output ? (
                <div className="animate-pulse opacity-70">
                  Executing code...
                </div>
              ) : (
                <pre className="whitespace-pre-wrap font-mono text-sm mt-2">{output}</pre>
              )}
            </div>
          </div>
          
          {/* Sidebar - Notes and Help */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-4 mb-6">
              <div className="flex justify-between items-center mb-4">
                <button
                  onClick={() => setShowNotes(!showNotes)}
                  className="w-full px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-700 transition-colors mb-2"
                >
                  {showNotes ? 'Hide Notes' : 'Show Notes'}
                </button>
              </div>
              
              <button
                className="w-full px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors flex items-center justify-center"
              >
                <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Mark with AI
              </button>
            </div>
            
            {/* Notes Section (conditionally shown) */}
            {showNotes && (
              <div className="notes-section">
                <h2 className="text-xl font-bold text-gray-800 mb-3">
                  Python List Comprehension Notes
                </h2>
                <p className="text-gray-700 mb-3">
                  List comprehension provides a concise way to create lists based on existing lists or other sequences.
                </p>
                
                <div className="code-sample">
                  new_list = [expression for item in iterable<br />
                  if condition]
                </div>
                
                <ul className="list-disc pl-5 space-y-1 text-gray-700">
                  <li>expression: the operation to perform on each item</li>
                  <li>item: the variable name for each element</li>
                  <li>iterable: the sequence to iterate over</li>
                  <li>condition: optional filtering criteria</li>
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    </PageLayout>
  );
} 