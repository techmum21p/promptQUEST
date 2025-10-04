'use client'

import { LoginComponent } from './components/LoginComponent'
import { HomePage } from './components/Layout'
import { useAuth } from './auth-context'

export default function RootPage() {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!user) {
    return <LoginComponent />
  }

  return <HomePage />
}
