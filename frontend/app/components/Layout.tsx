'use client'

import { useState } from 'react'
import { useAuth } from '../auth-context'
import { Dashboard } from './Dashboard'
import { PracticeMode } from './PracticeMode'
import { Leaderboard } from './Leaderboard'
import { ProgressHistory } from './ProgressHistory'
import { AdminPanel } from './AdminPanel'

type Page = 'dashboard' | 'practice' | 'leaderboard' | 'progress' | 'admin'

export function HomePage() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard')
  const { user, logout } = useAuth()

  const Sidebar = () => (
    <div className="h-full bg-white border-r border-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="h-10 w-10 bg-primary-600 rounded-lg flex items-center justify-center">
            <span className="text-white text-lg font-bold">🎯</span>
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900">Prompt Quest</h1>
            <p className="text-sm text-gray-500">Database Edition</p>
          </div>
        </div>
      </div>

      {/* User Info */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 bg-gray-200 rounded-full flex items-center justify-center">
            <span className="text-gray-600 text-sm font-medium">
              {user?.username?.charAt(0)?.toUpperCase()}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {user?.username}
            </p>
            <p className="text-xs text-gray-500 truncate">
              {user?.group}
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        <button
          onClick={() => setCurrentPage('dashboard')}
          className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
            currentPage === 'dashboard'
              ? 'bg-primary-50 text-primary-700 border border-primary-200'
              : 'text-gray-700 hover:bg-gray-50'
          }`}
        >
          <span>📊</span>
          <span className="font-medium">Dashboard</span>
        </button>

        <button
          onClick={() => setCurrentPage('practice')}
          className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
            currentPage === 'practice'
              ? 'bg-primary-50 text-primary-700 border border-primary-200'
              : 'text-gray-700 hover:bg-gray-50'
          }`}
        >
          <span>🎮</span>
          <span className="font-medium">Practice Mode</span>
        </button>

        <button
          onClick={() => setCurrentPage('leaderboard')}
          className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
            currentPage === 'leaderboard'
              ? 'bg-primary-50 text-primary-700 border border-primary-200'
              : 'text-gray-700 hover:bg-gray-50'
          }`}
        >
          <span>🏆</span>
          <span className="font-medium">Leaderboard</span>
        </button>

        <button
          onClick={() => setCurrentPage('progress')}

          className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
            currentPage === 'progress'
              ? 'bg-primary-50 text-primary-700 border border-primary-200'
              : 'text-gray-700 hover:bg-gray-50'
          }`}
        >
          <span>📈</span>
          <span className="font-medium">Progress History</span>
        </button>

        {/* Admin Panel - conditionally show */}
        {(user?.group === 'admin' || user?.username === 'admin') && (
          <button
            onClick={() => setCurrentPage('admin')}
            className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors ${
              currentPage === 'admin'
                ? 'bg-primary-50 text-primary-700 border border-primary-200'
                : 'text-gray-700 hover:bg-gray-50'
            }`}
          >
            <span>⚙️</span>
            <span className="font-medium">Admin Panel</span>
          </button>
        )}
      </nav>

      {/* Quick Stats */}
      <div className="p-4 border-t border-gray-200">
        <div className="bg-gray-50 rounded-lg p-3">
          <h3 className="text-sm font-medium text-gray-900 mb-2">Quick Stats</h3>
          <UserQuickStats />
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="text-center space-y-2">
          <button
            onClick={logout}
            className="w-full btn-secondary text-sm"
          >
            Sign Out
          </button>
          <p className="text-xs text-gray-500">
            Powered by Google ADK and Vertex AI
          </p>
        </div>
      </div>
    </div>
  )

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />
      case 'practice':
        return <PracticeMode />
      case 'leaderboard':
        return <Leaderboard />
      case 'progress':
        return <ProgressHistory />
      case 'admin':
        return <AdminPanel />
      default:
        return <Dashboard />
    }
  }

  return (
    <div className="h-screen flex bg-gray-50">
      {/* Sidebar */}
      <div className="w-80 flex-shrink-0">
        <Sidebar />
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        {renderCurrentPage()}
      </div>
    </div>
  )
}

function UserQuickStats() {
  const { user } = useAuth()
  // TODO: Fetch actual user stats
  const stats = {
    attempts: 0,
    avgScore: 0,
    skillLevel: user?.username === 'admin' ? 'Advanced' : 'Beginner'
  }

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-gray-600">Attempts:</span>
        <span className="font-medium">{stats.attempts}</span>
      </div>
      <div className="flex justify-between text-sm">
        <span className="text-gray-600">Avg Score:</span>
        <span className="font-medium">{stats.avgScore > 0 ? `${stats.avgScore.toFixed(1)}%` : 'N/A'}</span>
      </div>
      <div className="flex justify-between text-sm">
        <span className="text-gray-600">Skill Level:</span>
        <span className={`font-medium ${getSkillLevelColor(stats.skillLevel)}`}>
          {stats.skillLevel}
        </span>
      </div>
    </div>
  )
}

function getSkillLevelColor(level: string): string {
  switch (level.toLowerCase()) {
    case 'beginner':
      return 'text-red-600'
    case 'intermediate':
      return 'text-yellow-600'
    case 'advanced':
      return 'text-green-600'
    default:
      return 'text-gray-600'
  }
}
