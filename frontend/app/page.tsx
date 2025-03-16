import React from 'react';
import Link from 'next/link';
import PageLayout from './components/PageLayout';
import Image from 'next/image';

export default function HomePage() {
  return (
    <PageLayout>
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-python-blue to-blue-700 text-white">
        <div className="max-w-6xl mx-auto px-4 py-16 md:py-24">
          <div className="flex flex-col md:flex-row items-center">
            <div className="md:w-1/2 mb-10 md:mb-0">
              <h1 className="text-4xl md:text-5xl font-bold mb-4">
                Master Python Programming
              </h1>
              <p className="text-xl mb-8 opacity-90">
                Learn Python through interactive exercises and hands-on practice.
                From beginner to advanced, all in one platform.
              </p>
              <div className="flex flex-wrap gap-4">
                <Link href="/chapters" 
                  className="px-6 py-3 bg-white text-python-blue font-semibold rounded-md hover:bg-gray-100 transition-colors">
                  Start Learning
                </Link>
                <Link href="/about" 
                  className="px-6 py-3 bg-transparent border border-white text-white font-semibold rounded-md hover:bg-white/10 transition-colors">
                  Learn More
                </Link>
              </div>
            </div>
            <div className="md:w-1/2 flex justify-center">
              <div className="relative w-full max-w-md h-72">
                <div className="absolute inset-0 bg-white/10 backdrop-blur-sm rounded-lg shadow-lg transform rotate-3"></div>
                <div className="absolute inset-0 bg-white/10 backdrop-blur-sm rounded-lg shadow-lg transform -rotate-3"></div>
                <div className="relative bg-gray-900 rounded-lg shadow-xl p-6 transform">
                  <div className="flex items-center mb-3">
                    <div className="flex space-x-2">
                      <div className="w-3 h-3 rounded-full bg-red-500"></div>
                      <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                      <div className="w-3 h-3 rounded-full bg-green-500"></div>
                    </div>
                  </div>
                  <div className="font-mono text-sm text-blue-400">
                    <div className="mb-1"># Python Learning Platform</div>
                    <div className="mb-1 text-gray-400">def <span className="text-yellow-400">hello_world</span>():</div>
                    <div className="mb-1 ml-4 text-green-400">"Hello, welcome to Python Learning!"</div>
                    <div className="mb-1 text-gray-400">for <span className="text-purple-400">skill</span> in <span className="text-yellow-400">skills_to_learn</span>:</div>
                    <div className="mb-1 ml-4 text-gray-400">print(<span className="text-green-400">f"Learning {`{skill}`}..."</span>)</div>
                    <div className="mt-4 text-white">{'>'} Ready to code!</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 bg-gray-50">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">Why Learn With Us?</h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
              <div className="w-14 h-14 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 text-python-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-800">Interactive Learning</h3>
              <p className="text-gray-600">
                Code directly in your browser with real-time feedback and guidance.
              </p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
              <div className="w-14 h-14 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 text-python-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0h10a2 2 0 012 2v6a2 2 0 01-2 2H7a2 2 0 01-2-2V9a2 2 0 012-2" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-800">Structured Curriculum</h3>
              <p className="text-gray-600">
                Well-organized chapters and exercises that build on each other.
              </p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
              <div className="w-14 h-14 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 text-python-blue" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-800">Track Progress</h3>
              <p className="text-gray-600">
                Monitor your learning journey with completion tracking.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Call to Action */}
      <div className="bg-gray-900 text-white py-16">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">Ready to Start Your Python Journey?</h2>
          <p className="text-xl mb-8 opacity-80">
            Join thousands of students who are mastering Python programming with our interactive platform.
          </p>
          <Link href="/chapters" 
            className="px-8 py-4 bg-python-blue text-white font-semibold rounded-md hover:bg-blue-700 transition-colors inline-block">
            Browse Chapters
          </Link>
        </div>
      </div>
    </PageLayout>
  );
} 