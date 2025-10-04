'use client'

import { useState } from 'react'
import { useAuth } from '../auth-context'

export function LoginComponent() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [isRegisterMode, setIsRegisterMode] = useState(false)
  const { login, register } = useAuth()

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)
    setError('')

    const formData = new FormData(e.currentTarget)
    const data = Object.fromEntries(formData)

    try {
      if (isRegisterMode) {
        await register(data)
      } else {
        await login(data.ldap_id as string, data.password as string)
      }
    } catch (err: any) {
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-blue-50">
      <div className="max-w-md w-full space-y-8 p-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto h-20 w-20 bg-primary-600 rounded-full flex items-center justify-center mb-4">
            <span className="text-white text-3xl font-bold">🎯</span>
          </div>
          <h2 className="text-3xl font-bold text-gray-900">
            Prompt Quest
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Gamified Prompt Engineering Training for Microsoft 365 Copilot
          </p>
          <p className="text-xs text-gray-500 mt-1">
            Powered by Google ADK and Vertex AI
          </p>
        </div>

        {/* Login/Register Form */}
        <div className="card">
          <div className="text-center mb-6">
            <h3 className="text-xl font-semibold text-gray-900">
              {isRegisterMode ? 'Create Account' : 'Sign In'}
            </h3>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-danger-50 border border-danger-200 rounded-lg">
              <p className="text-sm text-danger-600">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="ldap_id" className="label">
                LDAP ID
              </label>
              <input
                id="ldap_id"
                name="ldap_id"
                type="text"
                required
                className="input-field"
                placeholder="Enter your LDAP ID"
              />
            </div>

            {isRegisterMode && (
              <>
                <div>
                  <label htmlFor="username" className="label">
                    Display Name
                  </label>
                  <input
                    id="username"
                    name="username"
                    type="text"
                    required
                    className="input-field"
                    placeholder="Enter your display name"
                  />
                </div>

                <div>
                  <label htmlFor="email" className="label">
                    Email Address
                  </label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    required
                    className="input-field"
                    placeholder="Enter your email"
                  />
                </div>

                <div>
                  <label htmlFor="group" className="label">
                    Department/Group
                  </label>
                  <select
                    id="group"
                    name="group"
                    className="input-field"
                  >
                    <option value="">Select your department</option>
                    <option value="Engineering">Engineering</option>
                    <option value="Marketing">Marketing</option>
                    <option value="Sales">Sales</option>
                    <option value="HR">Human Resources</option>
                    <option value="Finance">Finance</option>
                    <option value="Operations">Operations</option>
                    <option value="default">Other</option>
                  </select>
                </div>
              </>
            )}

            <div>
              <label htmlFor="password" className="label">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="input-field"
                placeholder="Enter your password"
              />
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    {isRegisterMode ? 'Creating Account...' : 'Signing In...'}
                  </div>
                ) : (
                  isRegisterMode ? 'Create Account' : 'Sign In'
                )}
              </button>
            </div>

            <div className="text-center">
              <button
                type="button"
                onClick={() => setIsRegisterMode(!isRegisterMode)}
                className="text-sm text-primary-600 hover:text-primary-500 font-medium"
              >
                {isRegisterMode 
                  ? 'Already have an account? Sign in' 
                  : "Don't have an account? Sign up"
                }
              </button>
            </div>
          </form>
        </div>

        {/* Footer */}
        <div className="text-center text-xs text-gray-500">
          <p>Advanced prompt engineering skills for modern productivity</p>
          <p className="mt-1">Practice with AI-powered evaluation and compete on leaderboards!</p>
        </div>
      </div>
    </div>
  )
}
