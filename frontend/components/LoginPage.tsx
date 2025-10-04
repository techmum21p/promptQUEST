'use client'

import { useState } from 'react'
import { useAppStore } from '@/lib/store'
import { toast } from 'react-hot-toast'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const { login, isLoading } = useAppStore()

  const testConnection = async () => {
    try {
      const response = await fetch('http://localhost:8000/health')
      const data = await response.json()
      console.log('Health check response:', data)
      toast.success('Backend connection successful!')
    } catch (error) {
      console.error('Connection test failed:', error)
      toast.error('Cannot connect to backend server')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    console.log('Form submitted with username:', username)
    
    if (!username.trim()) {
      toast.error('Please enter a username')
      console.log('Username empty, showing error toast')
      return
    }

    try {
      console.log('Attempting login...')
      await login(username.trim())
      console.log('Login successful, showing success toast')
      toast.success(`Welcome to PromptQuest, ${username}!`)
    } catch (error) {
      console.error('Login failed:', error)
      toast.error('Failed to login. Please try again.')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="text-6xl mb-4">🎯</div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            PromptQuest
          </h1>
          <h2 className="text-xl text-gray-600 mb-8">
            Gamified Prompt Engineering Training for Microsoft 365 Copilot
          </h2>
          <p className="text-gray-500">
            Ready to level up your prompt engineering skills?
          </p>
        </div>

        <div className="bg-white p-8 rounded-xl shadow-lg">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                Enter your username
              </label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Your username"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-colors"
                disabled={isLoading}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading || !username.trim()}
              className="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Starting Training...
                </div>
              ) : (
                'Start Training'
              )}
            </button>

            <button
              type="button"
              onClick={testConnection}
              className="w-full mt-2 bg-gray-500 hover:bg-gray-600 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
            >
              Test Backend Connection
            </button>
          </form>

          <div className="mt-6 text-center">
            <div className="text-sm text-gray-500">
              <p className="mb-2">
                <span className="font-medium">🎮 Features:</span>
              </p>
              <ul className="space-y-1 text-xs">
                <li>• AI-powered prompt evaluation</li>
                <li>• Gamified scoring & badges</li>
                <li>• Multiple difficulty levels</li>
                <li>• Progress tracking & analytics</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="text-center">
          <div className="text-sm text-gray-500">
            <p>Powered by Google ADK and Gemini AI</p>
            <p className="mt-2">
              Learn modern prompt engineering best practices for Microsoft 365 Copilot
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
