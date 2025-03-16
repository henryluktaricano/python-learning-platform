import React from 'react';
import PageLayout from '../components/PageLayout';

export default function AboutPage() {
  return (
    <PageLayout>
      <div className="max-w-4xl mx-auto py-8 px-4">
        <h1 className="text-3xl font-bold text-python-blue mb-6">About Python Learning Platform</h1>
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4">Our Mission</h2>
          <p className="mb-4">
            The Python Learning Platform is designed to provide an interactive and engaging way to learn Python programming.
            Our goal is to make learning Python accessible to everyone, from complete beginners to experienced developers
            looking to expand their skills.
          </p>
          <p>
            We believe in learning by doing, which is why our platform focuses on interactive exercises that allow you to
            write and execute code directly in your browser, receiving immediate feedback on your solutions.
          </p>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-python-blue">1</span>
              </div>
              <h3 className="font-bold mb-2">Browse Chapters</h3>
              <p className="text-gray-600">
                Explore our structured curriculum organized by chapters and topics.
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-python-blue">2</span>
              </div>
              <h3 className="font-bold mb-2">Complete Exercises</h3>
              <p className="text-gray-600">
                Work through interactive exercises with real-time code execution.
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-python-blue">3</span>
              </div>
              <h3 className="font-bold mb-2">Track Progress</h3>
              <p className="text-gray-600">
                Monitor your learning journey and build your Python skills step by step.
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold mb-4">Technologies Used</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-bold mb-2">Frontend</h3>
              <ul className="list-disc pl-5 space-y-1">
                <li>Next.js (React framework)</li>
                <li>TypeScript</li>
                <li>Tailwind CSS</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-bold mb-2">Backend</h3>
              <ul className="list-disc pl-5 space-y-1">
                <li>FastAPI (Python framework)</li>
                <li>Uvicorn (ASGI server)</li>
                <li>Python 3.9+</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </PageLayout>
  );
} 