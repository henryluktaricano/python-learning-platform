import React from 'react';
import Link from 'next/link';
import PageLayout from '../../../components/PageLayout';

interface PageProps {
  params: {
    topicId: string;
  };
}

// Fetch exercises for a specific topic
async function getExercises(topicId: string) {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
  
  try {
    const response = await fetch(`${API_URL}/exercises/topics/${topicId}`, { 
      next: { revalidate: 3600 } 
    });
    
    if (!response.ok) throw new Error('Failed to fetch exercises');
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(`Error fetching exercises for topic ${topicId}:`, error);
    // Return mock data as fallback
    return mockExercisesData[topicId] || [];
  }
}

// Fetch topic details
async function getTopic(topicId: string) {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
  
  try {
    const response = await fetch(`${API_URL}/chapters/topic/${topicId}`, { 
      next: { revalidate: 3600 } 
    });
    
    if (!response.ok) throw new Error('Failed to fetch topic details');
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(`Error fetching topic details for ${topicId}:`, error);
    // Return mock data as fallback
    return mockTopicData[topicId] || { title: 'Unknown Topic', chapter_title: 'Unknown Chapter' };
  }
}

export default async function TopicExercisesPage({ params }: PageProps) {
  const { topicId } = params;
  
  // Fetch exercises and topic details in parallel
  const [exercises, topic] = await Promise.all([
    getExercises(topicId),
    getTopic(topicId)
  ]);
  
  return (
    <PageLayout>
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-center mb-8">
          <Link 
            href="/chapters" 
            className="flex items-center text-python-blue hover:underline font-medium"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Chapters
          </Link>
        </div>
        
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">{topic.title || `Topic: ${topicId}`}</h1>
          <p className="text-gray-600">{topic.chapter_title ? `Chapter: ${topic.chapter_title}` : ''}</p>
        </div>
        
        {exercises.length > 0 ? (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {exercises.map((exercise: any, index: number) => (
              <Link 
                key={exercise.id} 
                href={`/exercises/exercise/${exercise.id}`}
                className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow"
              >
                <div className="p-6">
                  <div className="flex justify-between items-start mb-4">
                    <h2 className="text-lg font-bold text-gray-800">
                      {exercise.title || `Exercise ${index + 1}`}
                    </h2>
                    {exercise.difficulty && (
                      <span className={`inline-block px-2 py-1 rounded text-xs ${
                        exercise.difficulty === 'advanced' 
                          ? 'bg-red-100 text-red-800' 
                          : exercise.difficulty === 'intermediate'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-green-100 text-green-800'
                      }`}>
                        {exercise.difficulty}
                      </span>
                    )}
                  </div>
                  
                  <p className="text-gray-600 mb-4 line-clamp-2">
                    {exercise.description || exercise.instructions || 'No description available.'}
                  </p>
                  
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-500">
                      Exercise {index + 1} of {exercises.length}
                    </div>
                    <div className="text-python-blue flex items-center">
                      <span className="mr-1">Start</span>
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 bg-white rounded-lg shadow-md">
            <svg className="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-xl font-bold text-gray-700 mb-2">No exercises found</h2>
            <p className="text-gray-500">We couldn't find any exercises for this topic.</p>
          </div>
        )}
      </div>
    </PageLayout>
  );
}

// Mock data for development and fallback
const mockTopicData: Record<string, any> = {
  'variables': { 
    id: 'variables', 
    title: 'Variables and Data Types', 
    chapter_title: 'Basics',
    description: 'Learn about different data types in Python and how to use variables.'
  },
  'control_flow': { 
    id: 'control_flow', 
    title: 'Control Flow', 
    chapter_title: 'Basics',
    description: 'Master conditional statements and loops in Python.'
  },
  'lists': { 
    id: 'lists', 
    title: 'Lists and Tuples', 
    chapter_title: 'Data Structures',
    description: 'Explore sequence data types in Python: lists and tuples.'
  }
};

const mockExercisesData: Record<string, any[]> = {
  'variables': [
    { 
      id: 'var-assignment', 
      title: 'Variable Assignment', 
      difficulty: 'beginner',
      description: 'Learn how to assign values to variables in Python.' 
    },
    { 
      id: 'data-types', 
      title: 'Working with Data Types', 
      difficulty: 'beginner',
      description: 'Explore different data types like integers, floats, and strings.' 
    },
    { 
      id: 'type-conversion', 
      title: 'Type Conversion', 
      difficulty: 'intermediate',
      description: 'Convert between different data types in Python.' 
    }
  ],
  'lists': [
    { 
      id: 'list-basics', 
      title: 'List Basics', 
      difficulty: 'beginner',
      description: 'Learn how to create and manipulate lists in Python.' 
    },
    { 
      id: 'list-methods', 
      title: 'List Methods', 
      difficulty: 'beginner',
      description: 'Explore built-in methods for working with lists.' 
    },
    { 
      id: 'list-slicing', 
      title: 'List Slicing', 
      difficulty: 'intermediate',
      description: 'Extract parts of a list using slicing syntax.' 
    },
    { 
      id: 'list-comprehension', 
      title: 'List Comprehension', 
      difficulty: 'intermediate',
      description: 'Create lists using concise list comprehension syntax.' 
    }
  ]
}; 