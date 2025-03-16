'use client';

import React, { useState, useEffect, useRef } from 'react';
import { EditorView, basicSetup } from 'codemirror';
import { EditorState, Compartment } from '@codemirror/state';
import { python } from '@codemirror/lang-python';
import { keymap } from '@codemirror/view';
import { defaultKeymap, indentWithTab } from '@codemirror/commands';
import { oneDark } from '@codemirror/theme-one-dark';
import { dracula } from '@uiw/codemirror-theme-dracula';
import { material } from '@uiw/codemirror-theme-material';
import { sublime } from '@uiw/codemirror-theme-sublime';
import { githubLight } from '@uiw/codemirror-theme-github';
import { xcodeLight } from '@uiw/codemirror-theme-xcode';
import { nord } from '@uiw/codemirror-theme-nord';
import { search } from '@codemirror/search';
import { autocompletion } from '@codemirror/autocomplete';
import { Button } from './ui/button';
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from './ui/dropdown-menu';
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from './ui/tooltip';
import { cn } from '../lib/utils';

interface EnhancedCodeEditorProps {
  initialCode: string;
  onChange: (code: string) => void;
  onExecute?: () => void;
  height?: string;
  editorTheme?: string;
  onThemeChange?: (theme: string) => void;
  className?: string;
}

const themeMap: Record<string, any> = {
  'one-dark': oneDark,
  'dracula': dracula,
  'material-dark': material,
  'sublime': sublime,
  'github-light': githubLight,
  'xcode-light': xcodeLight,
  'nord': nord
};

const DEFAULT_THEME = 'one-dark';

const EnhancedCodeEditor: React.FC<EnhancedCodeEditorProps> = ({
  initialCode = '',
  onChange,
  onExecute,
  height = '400px',
  editorTheme,
  onThemeChange,
  className
}) => {
  const editorRef = useRef<HTMLDivElement>(null);
  const [code, setCode] = useState(initialCode);
  const [currentTheme, setCurrentTheme] = useState(editorTheme || DEFAULT_THEME);
  const [showRecommendations, setShowRecommendations] = useState(true);
  const [isExecuting, setIsExecuting] = useState(false);
  const viewRef = useRef<EditorView | null>(null);
  const themeCompartmentRef = useRef(new Compartment());
  const completionCompartmentRef = useRef(new Compartment());

  // Load preferences from localStorage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedTheme = localStorage.getItem('editor-theme');
      const savedRecommendations = localStorage.getItem('editor-recommendations');
      
      if (savedTheme && themeMap[savedTheme]) {
        setCurrentTheme(savedTheme);
        onThemeChange?.(savedTheme);
      }
      
      if (savedRecommendations !== null) {
        setShowRecommendations(savedRecommendations === 'true');
      }
    }
  }, [onThemeChange]);

  // Initialize CodeMirror editor
  useEffect(() => {
    if (!editorRef.current) return;

    // Extensions to use
    const extensions = [
      basicSetup,
      python(),
      keymap.of([
        ...defaultKeymap,
        indentWithTab,
        { key: 'Shift-Enter', run: () => { onExecute?.(); return true; } }
      ]),
      search(),
      EditorView.updateListener.of(update => {
        if (update.docChanged) {
          const newCode = update.state.doc.toString();
          setCode(newCode);
          onChange(newCode);
        }
      }),
      themeCompartmentRef.current.of(themeMap[currentTheme] || themeMap[DEFAULT_THEME]),
      completionCompartmentRef.current.of(showRecommendations ? autocompletion() : [])
    ];

    // Create the editor state
    const state = EditorState.create({
      doc: initialCode,
      extensions
    });

    // Create the editor view
    const view = new EditorView({
      state,
      parent: editorRef.current
    });

    // Save reference for cleanup
    viewRef.current = view;

    // Cleanup on unmount
    return () => {
      view.destroy();
    };
  }, [initialCode]);

  // Update editor theme when it changes
  useEffect(() => {
    if (viewRef.current && currentTheme) {
      const theme = themeMap[currentTheme] || themeMap[DEFAULT_THEME];
      viewRef.current.dispatch({
        effects: themeCompartmentRef.current.reconfigure(theme)
      });
    }
  }, [currentTheme]);

  // Update autocompletion when recommendations setting changes
  useEffect(() => {
    if (viewRef.current) {
      viewRef.current.dispatch({
        effects: completionCompartmentRef.current.reconfigure(
          showRecommendations ? autocompletion() : []
        )
      });
    }
  }, [showRecommendations]);

  // Handle theme change
  const handleThemeChange = (theme: string) => {
    setCurrentTheme(theme);
    localStorage.setItem('editor-theme', theme);
    onThemeChange?.(theme);
  };

  // Toggle recommendations
  const toggleRecommendations = () => {
    const newValue = !showRecommendations;
    setShowRecommendations(newValue);
    localStorage.setItem('editor-recommendations', String(newValue));
  };

  // Handle code execution
  const handleExecute = async () => {
    if (onExecute) {
      setIsExecuting(true);
      try {
        await onExecute();
      } catch (error) {
        console.error('Error executing code:', error);
      } finally {
        setIsExecuting(false);
      }
    }
  };

  // Handle reset to initial code
  const handleReset = () => {
    setCode(initialCode);
    onChange(initialCode);
    
    if (viewRef.current) {
      viewRef.current.dispatch({
        changes: {
          from: 0,
          to: viewRef.current.state.doc.length,
          insert: initialCode
        }
      });
    }
  };

  return (
    <TooltipProvider>
      <div className={cn("flex flex-col", className)}>
        <div className="flex justify-between items-center mb-2 border-b pb-2">
          <div className="flex space-x-2">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={toggleRecommendations}
                  className="px-2"
                >
                  <span className={`w-5 h-5 ${showRecommendations ? 'text-yellow-500' : 'text-gray-400'}`}>
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M10 1a6 6 0 0 0-6 6v1h12V7a6 6 0 0 0-6-6Zm8 8H2a2 2 0 0 0-2 2v1a2 2 0 0 0 2 2h2v3a3 3 0 0 0 3 3h6a3 3 0 0 0 3-3v-3h2a2 2 0 0 0 2-2v-1a2 2 0 0 0-2-2Z" />
                    </svg>
                  </span>
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                {showRecommendations ? 'Disable Recommendations' : 'Enable Recommendations'}
              </TooltipContent>
            </Tooltip>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="px-2">
                  <span className="flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5 mr-1">
                      <path d="M12.24 8.365A2.993 2.993 0 0 0 14 9a3 3 0 1 0-3-3c0 .463.108.902.3 1.293L7.36 11.233A2.995 2.995 0 0 0 5 11a3 3 0 1 0 3 3 2.99 2.99 0 0 0-.236-1.160L12.24 8.363Z" />
                    </svg>
                    Theme
                  </span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start">
                <DropdownMenuItem onClick={() => handleThemeChange('one-dark')}>One Dark</DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleThemeChange('dracula')}>Dracula</DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleThemeChange('material-dark')}>Material Dark</DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleThemeChange('sublime')}>Sublime</DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleThemeChange('github-light')}>GitHub Light</DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleThemeChange('xcode-light')}>Xcode Light</DropdownMenuItem>
                <DropdownMenuItem onClick={() => handleThemeChange('nord')}>Nord</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          <div className="flex space-x-2">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={handleReset}
                  className="px-2"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
                    <path fillRule="evenodd" d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16ZM6.75 9.25a.75.75 0 0 0 0 1.5h4.59l-2.1 1.95a.75.75 0 1 0 1.02 1.1l3.5-3.25a.75.75 0 0 0 0-1.1l-3.5-3.25a.75.75 0 1 0-1.02 1.1l2.1 1.95H6.75Z" clipRule="evenodd" />
                  </svg>
                </Button>
              </TooltipTrigger>
              <TooltipContent>Reset to Original Code</TooltipContent>
            </Tooltip>

            <Tooltip>
              <TooltipTrigger asChild>
                <Button 
                  variant="default" 
                  size="sm" 
                  onClick={handleExecute}
                  disabled={isExecuting}
                  className="bg-python-blue hover:bg-python-blue-dark"
                >
                  {isExecuting ? (
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  ) : (
                    <svg className="w-5 h-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  )}
                  Run Code
                </Button>
              </TooltipTrigger>
              <TooltipContent>Run Code (Shift+Enter)</TooltipContent>
            </Tooltip>
          </div>
        </div>
        
        <div 
          ref={editorRef} 
          className="overflow-auto border rounded-md" 
          style={{ height }}
        />
        
        <div className="text-xs text-gray-500 mt-2">
          <span>Press <kbd className="px-1 py-0.5 bg-gray-100 border rounded">Ctrl</kbd>+<kbd className="px-1 py-0.5 bg-gray-100 border rounded">F</kbd> to search</span>
          <span className="mx-2">|</span>
          <span>Press <kbd className="px-1 py-0.5 bg-gray-100 border rounded">Shift</kbd>+<kbd className="px-1 py-0.5 bg-gray-100 border rounded">Enter</kbd> to run code</span>
        </div>
      </div>
    </TooltipProvider>
  );
};

export default EnhancedCodeEditor; 