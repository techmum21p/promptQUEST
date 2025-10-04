'use client'

import { useState } from 'react'
import { useAppStore } from '@/lib/store'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const { currentUser, userStats, logout, fetchUserStats, navigateTo, currentPage } = useAppStore()

  const handleLogout = () => {
    logout()
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-80' : 'w-16'} bg-white shadow-lg transition-all duration-300 flex flex-col`}>
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            {sidebarOpen && (
              <div className="text-center">
                <div className="text-2xl mb-1">🎯</div>
                <h1 className="text-sm font-bold text-gray-900">PromptQuest</h1>
              </div>
            )}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1 rounded hover:bg-gray-100 transition-colors"
            >
              {sidebarOpen ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <div className="space-y-2">
            <NavigationItem 
              text="Dashboard" 
              icon="📊" 
              page="dashboard" 
              active={currentPage === 'dashboard'} 
              sidebarOpen={sidebarOpen} 
              onClick={() => navigateTo('dashboard')} 
            />
            <NavigationItem 
              text="Practice Mode" 
              icon="📝" 
              page="practice" 
              sidebarOpen={sidebarOpen} 
              onClick={() => navigateTo('practice')} 
            />
            <NavigationItem 
              text="Leaderboard" 
              icon="🏆" 
              page="leaderboard" 
              sidebarOpen={sidebarOpen} 
              onClick={() => navigateTo('leaderboard')} 
            />
            <NavigationItem 
              text="Progress History" 
              icon="📈" 
              page="progress" 
              sidebarOpen={sidebarOpen} 
              onClick={() => navigateTo('progress')} 
            />
            <NavigationItem 
              text="Data Export" 
              icon="📊" 
              page="export" 
              sidebarOpen={sidebarOpen} 
              onClick={() => navigateTo('export')} 
            />
            <NavigationItem 
              text="Learning Resources" 
              icon="📚" 
              page="resources" 
              sidebarOpen={sidebarOpen} 
              onClick={() => navigateTo('resources')} 
            />
            <NavigationItem 
              text="Admin Panel" 
              icon="⚙️" 
              page="admin" 
              sidebarOpen={sidebarOpen} 
              onClick={() => navigateTo('admin')} 
            />
          </div>
        </nav>

        {/* User Stats */}
        {userStats && sidebarOpen && (
          <div className="p-4 border-t border-gray-200">
            <h3 className="text-sm font-medium text-gray-700 mb-3">📊 Quick Stats</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Attempts:</span>
                <span className="font-medium">{userStats.attempts}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Avg Score:</span>
                <span className="font-medium">
                  {userStats.attempts > 0 
                    ? (userStats.total_score / userStats.attempts).toFixed(1)
                    : '0.0'
                  }
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Skill:</span>
                <span className="font-medium capitalize">{userStats.skill_level}</span>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex flex-col space-y-2">
            {sidebarOpen && (
              <div className="text-xs text-gray-500 mb-2">
                <p className="font-medium">Welcome back, {currentUser}! 👋</p>
                <p className="mt-1">Learn & improve your prompt skills</p>
              </div>
            )}
            <button
              onClick={handleLogout}
              className="w-full bg-red-500 hover:bg-red-600 text-white text-sm font-medium py-2 px-3 rounded-lg transition-colors duration-200"
            >
              🚪 Logout
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Main Header */}
        <header className="bg-white shadow-sm border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">
                Welcome back, {currentUser}! 👋
              </h1>
              <p className="text-sm text-gray-600">
                Ready to practice your prompt engineering skills?
              </p>
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}

interface NavigationItemProps {
  text: string
  icon: string
  page: string
  active?: boolean
  sidebarOpen: boolean
  onClick: () => void
}

function NavigationItem({ text, icon, page, active = false, sidebarOpen, onClick }: NavigationItemProps) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200 w-full text-left ${
        active
          ? 'bg-primary-100 text-primary-700'
          : 'text-gray-700 hover:bg-gray-100'
      }`}
    >
      <span className="mr-3">{icon}</span>
      {sidebarOpen && text}
    </button>
  )
}
