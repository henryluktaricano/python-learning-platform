import React from 'react';
import Link from 'next/link';
import PageLayout from '../components/PageLayout';

// Define the structure of a topic
interface Topic {
  id: string;
  title: string;
  completed: boolean;
}

// Define the structure of a chapter
interface Chapter {
  id: string;
  title: string;
  topics: Topic[];
  completedCount: number;
  totalCount: number;
}

// Async function to fetch chapters data
async function getChapters() {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003/api';
  
  try {
    const response = await fetch(`${API_URL}/chapters`, { 
      next: { revalidate: 3600 } 
    });
    
    if (!response.ok) throw new Error('Failed to fetch chapters');
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching chapters:', error);
    
    // Return mock data to ensure the UI has something to display
    return mockChapters;
  }
}

// Mock chapter data for development/fallback
const mockChapters: Chapter[] = [
  {
    id: "chapter1",
    title: "Basics",
    completedCount: 4,
    totalCount: 10,
    topics: [
      { id: "variables", title: "Variables and Data Types", completed: true },
      { id: "control_flow", title: "Control Flow", completed: false },
      { id: "functions", title: "Functions", completed: false }
    ]
  },
  {
    id: "chapter2",
    title: "Data Structures",
    completedCount: 0,
    totalCount: 8,
    topics: [
      { id: "lists", title: "Lists and Tuples", completed: false },
      { id: "dictionaries", title: "Dictionaries", completed: false },
      { id: "sets", title: "Sets", completed: false }
    ]
  },
  {
    id: "chapter3",
    title: "OOP",
    completedCount: 0,
    totalCount: 6,
    topics: [
      { id: "classes", title: "Classes and Objects", completed: false },
      { id: "inheritance", title: "Inheritance", completed: false },
      { id: "polymorphism", title: "Polymorphism", completed: false }
    ]
  },
  {
    id: "chapter4",
    title: "Advanced",
    completedCount: 0,
    totalCount: 7,
    topics: [
      { id: "decorators", title: "Decorators", completed: false },
      { id: "generators", title: "Generators", completed: false },
      { id: "context_managers", title: "Context Managers", completed: false }
    ]
  },
  {
    id: "chapter5",
    title: "File Handling",
    completedCount: 0,
    totalCount: 5,
    topics: [
      { id: "file_operations", title: "File Operations", completed: false },
      { id: "csv_processing", title: "CSV Processing", completed: false },
      { id: "json_handling", title: "JSON Handling", completed: false }
    ]
  },
  {
    id: "chapter6",
    title: "APIs",
    completedCount: 0,
    totalCount: 6,
    topics: [
      { id: "rest_apis", title: "REST APIs", completed: false },
      { id: "http_methods", title: "HTTP Methods", completed: false },
      { id: "authentication", title: "Authentication", completed: false }
    ]
  }
];

export default async function ChaptersPage() {
  // Fetch chapters data
  const chaptersData = await getChapters();
  const chapters = chaptersData || [];
  
  return (
    <PageLayout>
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-center mb-8">
          <Link 
            href="/exercises" 
            className="flex items-center text-python-blue hover:underline font-medium"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Exercises
          </Link>
        </div>

        <h1 className="text-3xl font-bold text-gray-800 mb-10">Python Learning Chapters</h1>

        {chapters.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {chapters.map((chapter) => (
              <div key={chapter.id} className="bg-white rounded-lg shadow-md overflow-hidden border border-gray-200">
                <div className="p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-bold text-gray-800">
                      Chapter {chapter.id.replace(/[^0-9]/g, '')}: {chapter.title}
                    </h2>
                    <span className="text-sm bg-gray-100 px-2 py-1 rounded text-gray-600">
                      {chapter.completedCount}/{chapter.totalCount} Complete
                    </span>
                  </div>
                  
                  <ul className="space-y-3">
                    {chapter.topics.map((topic) => (
                      <li key={topic.id} className="flex items-center">
                        <div className={`w-5 h-5 rounded-full flex items-center justify-center mr-3 
                          ${topic.completed 
                            ? 'bg-green-500' 
                            : 'border-2 border-gray-300'}`}
                        >
                          {topic.completed && (
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                            </svg>
                          )}
                        </div>
                        <Link 
                          href={`/exercises/topics/${topic.id}`}
                          className="text-gray-700 hover:text-python-blue transition-colors"
                        >
                          {topic.title}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-lg text-gray-600">Loading chapters...</p>
          </div>
        )}
      </div>
      
      <div className="border-t border-gray-200 mt-12">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex flex-wrap items-center justify-between text-sm text-gray-600">
            <div className="flex space-x-6 mb-4 md:mb-0">
              <Link href="/settings" className="hover:text-python-blue">Settings</Link>
              <Link href="/help" className="hover:text-python-blue">Help Center</Link>
              <Link href="/docs" className="hover:text-python-blue">Documentation</Link>
            </div>
            <div className="flex space-x-4">
              <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="hover:text-python-blue">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
                </svg>
              </a>
              <a href="https://discord.com" target="_blank" rel="noopener noreferrer" className="hover:text-python-blue">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                  <path d="M13.545 2.907a13.227 13.227 0 0 0-3.257-1.011.05.05 0 0 0-.052.025c-.141.25-.297.577-.406.833a12.19 12.19 0 0 0-3.658 0 8.258 8.258 0 0 0-.412-.833.051.051 0 0 0-.052-.025c-1.125.194-2.22.534-3.257 1.011a.041.041 0 0 0-.021.018C.356 6.024-.213 9.047.066 12.032c.001.014.01.028.021.037a13.276 13.276 0 0 0 3.995 2.02.05.05 0 0 0 .056-.019c.308-.42.582-.863.818-1.329a.05.05 0 0 0-.01-.059.051.051 0 0 0-.018-.011 8.875 8.875 0 0 1-1.248-.595.05.05 0 0 1-.02-.066.051.051 0 0 1 .015-.019c.084-.063.168-.129.248-.195a.05.05 0 0 1 .051-.007c2.619 1.196 5.454 1.196 8.041 0a.052.052 0 0 1 .053.007c.08.066.164.132.248.195a.051.051 0 0 1-.004.085 8.254 8.254 0 0 1-1.249.594.05.05 0 0 0-.03.03.052.052 0 0 0 .003.041c.24.465.515.909.817 1.329a.05.05 0 0 0 .056.019 13.235 13.235 0 0 0 4.001-2.02.049.049 0 0 0 .021-.037c.334-3.451-.559-6.449-2.366-9.106a.034.034 0 0 0-.02-.019Zm-8.198 7.307c-.789 0-1.438-.724-1.438-1.612 0-.889.637-1.613 1.438-1.613.807 0 1.45.73 1.438 1.613 0 .888-.637 1.612-1.438 1.612Zm5.316 0c-.788 0-1.438-.724-1.438-1.612 0-.889.637-1.613 1.438-1.613.807 0 1.451.73 1.438 1.613 0 .888-.631 1.612-1.438 1.612Z"/>
                </svg>
              </a>
            </div>
          </div>
        </div>
      </div>
    </PageLayout>
  );
}
 