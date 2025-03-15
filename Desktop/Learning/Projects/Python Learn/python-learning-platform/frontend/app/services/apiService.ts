/**
 * API Service for the Python Learning Platform
 * Handles all API requests to the backend server
 */
import axios from 'axios';

// Get API URL from environment variable or use default
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Log all requests in development
api.interceptors.request.use(config => {
  console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

// Helper function to handle API requests
const fetchAPI = async <T>(url: string, options?: RequestInit): Promise<T> => {
  try {
    const response = await api.get(url);
    return response.data as T;
  } catch (error) {
    console.error(`API Error (${url}):`, error);
    throw error;
  }
};

// API functions for chapters
export const fetchChapters = async () => {
  return fetchAPI<any[]>('/chapters');
};

export const fetchChapter = async (chapterId: string) => {
  return fetchAPI<any>(`/chapters/${chapterId}`);
};

export const fetchChapterTopics = async (chapterId: string) => {
  const chapter = await fetchChapter(chapterId);
  return chapter.topics || [];
};

// API functions for exercises
export const fetchExercisesByTopic = async (topicId: string) => {
  return fetchAPI<any[]>(`/exercises/topics/${topicId}`);
};

export const fetchExercisesByChapter = async (chapterId: string) => {
  return fetchAPI<any[]>(`/exercises/chapter/${chapterId}`);
};

export const fetchExercise = async (exerciseId: string) => {
  return fetchAPI<any>(`/exercises/exercise/${exerciseId}`);
};

// API functions for token tracking
export const fetchTokenUsage = async () => {
  return fetchAPI<any>('/tokens');
};

export const updateTokenUsage = async (tokenData: any) => {
  try {
    const response = await api.post('/tokens', tokenData);
    return response.data;
  } catch (error) {
    console.error('Error updating token usage:', error);
    throw error;
  }
};

// API function for executing code
export const executeCode = async (code: string) => {
  try {
    const response = await api.post('/execute', { code });
    return response.data;
  } catch (error) {
    console.error('Error executing code:', error);
    throw error;
  }
};

export default {
  fetchChapters,
  fetchChapter,
  fetchChapterTopics,
  fetchExercisesByTopic,
  fetchExercisesByChapter,
  fetchExercise,
  fetchTokenUsage,
  updateTokenUsage,
  executeCode,
}; 