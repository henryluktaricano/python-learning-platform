'use client';

import Link from 'next/link';
import React from 'react';

const Navbar: React.FC = () => {
  return (
    <nav className="bg-python-blue text-white shadow-md">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <Link href="/" className="flex items-center space-x-2">
          <span className="text-python-yellow font-bold text-2xl">Python</span>
          <span className="font-medium text-xl">Learning Platform</span>
        </Link>
        
        <div className="hidden md:flex space-x-6">
          <Link href="/" className="hover:text-python-yellow transition-colors">
            Home
          </Link>
          <Link href="/chapters" className="hover:text-python-yellow transition-colors">
            Chapters
          </Link>
          <Link href="/about" className="hover:text-python-yellow transition-colors">
            About
          </Link>
        </div>
        
        <div className="flex items-center space-x-4">
          <button className="md:hidden">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="h-6 w-6">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 