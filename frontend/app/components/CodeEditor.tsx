'use client';

import React, { useState, useCallback } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { python } from '@codemirror/lang-python';
import { oneDark } from '@codemirror/theme-one-dark';

interface CodeEditorProps {
  initialCode: string;
  readOnly?: boolean;
  onCodeChange?: (code: string) => void;
  height?: string;
}

export default function CodeEditor({
  initialCode,
  readOnly = false,
  onCodeChange,
  height = '300px'
}: CodeEditorProps) {
  const [code, setCode] = useState(initialCode);
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState('');
  const [apiError, setApiError] = useState<string | null>(null);

  const handleChange = useCallback((value: string) => {
    setCode(value);
    if (onCodeChange) {
      onCodeChange(value);
    }
  }, [onCodeChange]);

  const runCode = useCallback(async () => {
    if (isRunning || readOnly) return;
    
    setIsRunning(true);
    setOutput('');
    setError('');
    setApiError(null);

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
      console.log(`Calling API at ${API_URL}/execute-code`);

      const response = await fetch(`${API_URL}/execute-code`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API error response:', errorText);
        setApiError(`API Error (${response.status}): ${errorText}`);
        return;
      }

      const data = await response.json();

      if (data.error) {
        setError(data.error);
      } else {
        setOutput(data.output || 'Your code executed successfully (no output)');
      }
    } catch (err) {
      console.error('Failed to execute code:', err);
      setApiError(`Failed to connect to the server: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setIsRunning(false);
    }
  }, [code, isRunning, readOnly]);
  
  const resetCode = useCallback(() => {
    setCode(initialCode);
    setOutput('');
    setError('');
    setApiError(null);
  }, [initialCode]);

  return (
    <div className="code-editor w-full">
      {/* Editor Container */}
      <div className="mb-4">
        <div className="bg-gray-900 rounded-md overflow-hidden">
          <div className="flex items-center justify-between bg-gray-950 px-4 py-2">
            <div className="flex items-center">
              <div className="flex space-x-2 mr-2">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
              </div>
              <span className="text-xs text-gray-400">python</span>
            </div>
            <div className="text-xs text-gray-400">
              Press Ctrl+Enter or Cmd+Enter to run
            </div>
          </div>
          <CodeMirror
            value={code}
            height={height}
            extensions={[python()]}
            onChange={handleChange}
            theme={oneDark}
            readOnly={readOnly}
            basicSetup={{
              lineNumbers: true,
              highlightActiveLine: true,
              highlightActiveLineGutter: true,
              foldGutter: true,
              bracketMatching: true,
              closeBrackets: true,
              autocompletion: true,
              indentOnInput: true,
            }}
            className="font-mono text-sm"
          />
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap justify-between gap-2 mb-4">
        <button
          className="px-4 py-2 bg-python-blue text-white rounded hover:bg-blue-700 transition-colors 
                    flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
          onClick={runCode}
          disabled={isRunning || readOnly}
        >
          {isRunning ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Running...
            </>
          ) : (
            <>
              <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Run Code
            </>
          )}
        </button>

        <div className="flex space-x-2">
          <button
            className="px-4 py-2 border border-gray-300 text-gray-300 rounded hover:bg-gray-800 transition-colors
                      flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={resetCode}
            disabled={isRunning || readOnly}
          >
            <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Reset
          </button>
        </div>
      </div>

      {/* API connection error */}
      {apiError && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          <div className="flex items-center mb-2">
            <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <h3 className="font-bold">API Connection Error</h3>
          </div>
          <p className="text-sm">{apiError}</p>
          <p className="text-sm mt-2">Make sure the backend server is running on port 8000.</p>
        </div>
      )}

      {/* Output or Error Display */}
      {(output || error) && (
        <div className="rounded-md overflow-hidden border border-gray-700">
          <div className="bg-gray-800 px-4 py-2 border-b border-gray-700 flex justify-between items-center">
            <h3 className="font-medium text-gray-200">{error ? 'Error' : 'Output'}</h3>
            <button 
              onClick={() => {error ? setError('') : setOutput('')}}
              className="text-gray-400 hover:text-gray-200"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <pre className={`p-4 whitespace-pre-wrap font-mono text-sm overflow-x-auto ${
            error ? 'bg-red-900/20 text-red-300' : 'bg-gray-900 text-gray-300'
          }`}>
            {error || output}
          </pre>
        </div>
      )}
    </div>
  );
} 