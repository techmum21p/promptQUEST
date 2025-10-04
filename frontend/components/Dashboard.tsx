'use client'

import { useAppStore } from '@/lib/store'
import { useEffect } from 'react'

export default function Dashboard() {
  const { userStats, fetchUserStats } = useAppStore()

  useEffect(() => {
    fetchUserStats()
  }, [fetchUserStats])

  if (!userStats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const avgScore = userStats.attempts > 0 
    ? (userStats.total_score / userStats.attempts).toFixed(1)
    : '0.0'

  return (
    <div className="p-6">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🚀 Ready to practice?
        </h1>
        <p className="text-gray-600">
          Use the sidebar to navigate to <strong>Practice Mode</strong> and start improving your prompt engineering skills!
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="score-card">
          <h2 className="text-3xl font-bold mb-1">{userStats.attempts}</h2>
          <p className="text-sm opacity-90">Total Attempts</p>
        </div>
        
        <div className="score-card">
          <h2 className="text-3xl font-bold mb-1">{avgScore}</h2>
          <p className="text-sm opacity-90">Average Score</p>
        </div>
        
        <div className="score-card">
          <h2 className="text-3xl font-bold mb-1 capitalize">{userStats.skill_level}</h2>
          <p className="text-sm opacity-90">Skill Level</p>
        </div>
        
        <div className="score-card">
          <h2 className="text-3xl font-bold mb-1">{userStats.badges.length}</h2>
          <p className="text-sm opacity-90">Badges Earned</p>
        </div>
      </div>

      {/* Badges */}
      {userStats.badges.length > 0 && (
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">🏆 Your Badges</h3>
          <div className="flex flex-wrap gap-2">
            {userStats.badges.map((badge, index) => (
              <span key={index} className="badge">{badge}</span>
            ))}
          </div>
        </div>
      )}

      {/* Quick Start Guide */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Start Guide</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">1️⃣</span>
            </div>
            <h3 className="font-medium text-gray-900 mb-2">Choose Level</h3>
            <p className="text-sm text-gray-600">
              Select your skill level: Beginner, Intermediate, or Advanced
            </p>
          </div>
          
          <div className="text-center">
            <div className="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">2️⃣</span>
            </div>
            <h3 className="font-medium text-gray-900 mb-2">Write Prompt</h3>
            <p className="text-sm text-gray-600">
              Craft a prompt for the given scenario
            </p>
          </div>
          
          <div className="text-center">
            <div className="bg-primary-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">3️⃣</span>
            </div>
            <h3 className="font-medium text-gray-900 mb-2">Get Feedback</h3>
            <p className="text-sm text-gray-600">
              Receive AI-powered evaluation and improve
            </p>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      {userStats.history.length > 0 && (
        <div className="mt-8 bg-white rounded-xl shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
          
          <div className="space-y-3">
            {userStats.history
              .slice(-3)
              .reverse()
              .map((attempt, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <span className={`text-sm font-medium px-2 py-1 rounded-full ${
                      attempt.score >= 85 ? 'bg-green-100 text-green-800' :
                      attempt.score >= 70 ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {attempt.score}/100
                    </span>
                    <span className="text-sm text-gray-600">{attempt.scenario_id}</span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(attempt.timestamp).toLocaleDateString()}
                  </span>
                </div>
              ))
            }
          </div>
          
          {userStats.history.length > 3 && (
            <p className="text-sm text-gray-500 mt-3 text-center">
              And {userStats.history.length - 3} more attempts...
            </p>
          )}
        </div>
      )}

      {/* Call to Action */}
      <div className="mt-8 text-center">
        <a
          href="/practice"
          className="inline-flex items-center px-6 py-3 btn-primary text-lg"
        >
          🚀 Start Practicing Now
        </a>
      </div>
    </div>
  )
}
