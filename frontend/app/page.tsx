'use client'

import { useEffect, useState } from 'react'
import { useAppStore } from '@/lib/store'
import dynamic from 'next/dynamic'

// Dynamically import components to prevent hydration issues
const LoginPage = dynamic(() => import('@/components/LoginPage'), { ssr: false })
const Layout = dynamic(() => import('@/components/Layout'), { ssr: false })
const Dashboard = dynamic(() => import('@/components/Dashboard'), { ssr: false })
const PracticeMode = dynamic(() => import('@/components/PracticeMode'), { ssr: false })
const Leaderboard = dynamic(() => import('@/components/Leaderboard'), { ssr: false })
const ProgressHistory = dynamic(() => import('@/components/ProgressHistory'), { ssr: false })
const DataExport = dynamic(() => import('@/components/DataExport'), { ssr: false })
const LearningResources = dynamic(() => import('@/components/LearningResources'), { ssr: false })
const AdminPanel = dynamic(() => import('@/components/AdminPanel'), { ssr: false })

export default function Home() {
  const [isHydrated, setIsHydrated] = useState(false)

  // Ensure hydration is complete before rendering
  useEffect(() => {
    setIsHydrated(true)
  }, [])

  // Show loading state until hydration is complete
  if (!isHydrated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-2xl mb-4">🎯</div>
          <h1 className="text-xl font-semibold text-gray-900 mb-2">PromptQuest</h1>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  return <ClientApp />
}

function ClientApp() {
  const { currentUser } = useAppStore()

  if (!currentUser) {
    return <LoginPage />
  }

  return (
    <Layout>
      <MainContent />
    </Layout>
  )
}

function MainContent() {
  const { currentPage } = useAppStore()
  
  switch (currentPage) {
    case 'dashboard':
      return <Dashboard />
    case 'practice':
      return <PracticeMode />
    case 'leaderboard':
      return <Leaderboard />
    case 'progress':
      return <ProgressHistory />
    case 'export':
      return <DataExport />
    case 'resources':
      return <LearningResources />
    case 'admin':
      return <AdminPanel />
    default:
      return <Dashboard />
  }
}
