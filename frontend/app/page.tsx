'use client'

import { useAppStore } from '@/lib/store'
import LoginPage from '@/components/LoginPage'
import Layout from '@/components/Layout'
import Dashboard from '@/components/Dashboard'
import PracticeMode from '@/components/PracticeMode'
import Leaderboard from '@/components/Leaderboard'
import ProgressHistory from '@/components/ProgressHistory'
import DataExport from '@/components/DataExport'
import LearningResources from '@/components/LearningResources'
import AdminPanel from '@/components/AdminPanel'

export default function Home() {
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
