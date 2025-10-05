// Example component showing LDAP ID integration
// This shows how frontend components would need to be updated

import React, { useState } from 'react'
import { useAppStore } from '../lib/store-postgres'

interface LoginFormProps {
  onLogin: (ldapId: string, username: string) => void
}

export const LoginForm: React.FC<LoginFormProps> = ({ onLogin }) => {
  const [ldapId, setLdapId] = useState('')
  const [username, setUsername] = useState('')
  const [isRegistering, setIsRegistering] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!ldapId.trim() || !username.trim()) return
    
    if (isRegistering) {
      // Register new user
      await useAppStore.getState().addUser(ldapId, username)
    }
    
    // Set as current user
    useAppStore.getState().setCurrentUser(ldapId, username)
    onLogin(ldapId, username)
  }

  return (
    <div className="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-center">
        {isRegistering ? 'Register New User' : 'Login'}
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="ldapId" className="block text-sm font-medium text-gray-700">
            LDAP ID *
          </label>
          <input
            type="text"
            id="ldapId"
            value={ldapId}
            onChange={(e) => setLdapId(e.target.value)}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter your LDAP ID"
            required
          />
          <p className="mt-1 text-xs text-gray-500">
            Your unique organizational identifier
          </p>
        </div>

        <div>
          <label htmlFor="username" className="block text-sm font-medium text-gray-700">
            Display Name *
          </label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter your display name"
            required
          />
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="register"
            checked={isRegistering}
            onChange={(e) => setIsRegistering(e.target.checked)}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="register" className="ml-2 block text-sm text-gray-700">
            Register as new user
          </label>
        </div>

        <button
          type="submit"
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          {isRegistering ? 'Register & Login' : 'Login'}
        </button>
      </form>

      <div className="mt-4 text-center">
        <button
          onClick={() => setIsRegistering(!isRegistering)}
          className="text-sm text-blue-600 hover:text-blue-500"
        >
          {isRegistering 
            ? 'Already have an account? Login' 
            : 'Need an account? Register'
          }
        </button>
      </div>
    </div>
  )
}

// Example of how to update existing components
export const UserProfile: React.FC = () => {
  const { currentUser, currentUsername, userStats, fetchUserStats } = useAppStore()

  React.useEffect(() => {
    if (currentUser) {
      fetchUserStats()
    }
  }, [currentUser, fetchUserStats])

  if (!currentUser) {
    return <div>Please login first</div>
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-semibold mb-4">User Profile</h3>
      
      <div className="space-y-2">
        <div>
          <span className="font-medium">LDAP ID:</span> {currentUser}
        </div>
        <div>
          <span className="font-medium">Display Name:</span> {currentUsername}
        </div>
        
        {userStats && (
          <>
            <div>
              <span className="font-medium">Total Score:</span> {userStats.total_score}
            </div>
            <div>
              <span className="font-medium">Attempts:</span> {userStats.attempts}
            </div>
            <div>
              <span className="font-medium">Skill Level:</span> {userStats.skill_level}
            </div>
            <div>
              <span className="font-medium">Badges:</span> {userStats.badges.length}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

// Example of how to update the leaderboard component
export const Leaderboard: React.FC = () => {
  const { leaderboard, fetchLeaderboard } = useAppStore()

  React.useEffect(() => {
    fetchLeaderboard()
  }, [fetchLeaderboard])

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-semibold mb-4">Leaderboard</h3>
      
      <div className="space-y-2">
        {leaderboard.map((entry, index) => (
          <div key={entry.ldap_id} className="flex justify-between items-center p-2 bg-gray-50 rounded">
            <div className="flex items-center space-x-3">
              <span className="font-bold text-lg">#{index + 1}</span>
              <div>
                <div className="font-medium">{entry.username}</div>
                <div className="text-sm text-gray-500">ID: {entry.ldap_id}</div>
              </div>
            </div>
            <div className="text-right">
              <div className="font-medium">{entry.avg_score.toFixed(1)} avg</div>
              <div className="text-sm text-gray-500">{entry.total_attempts} attempts</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
