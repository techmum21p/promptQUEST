'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import Cookies from 'js-cookie'
import axios from 'axios'

interface User {
  ldap_id: string
  username: string
  email: string
  group: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (ldap_id: string, password: string) => Promise<void>
  register: (userData: any) => Promise<void>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check for existing token in cookies
    const savedToken = Cookies.get('auth_token')
    if (savedToken) {
      setToken(savedToken)
      // Set default headers for axios
      axios.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`
      // Fetch user profile
      fetchUserProfile(savedToken)
    } else {
      setIsLoading(false)
    }
  }, [])

  const fetchUserProfile = async (authToken: string) => {
    try {
      const { data } = await axios.get('/api/user/profile', {
        headers: { Authorization: `Bearer ${authToken}` }
      })
      setUser(data)
    } catch (error) {
      console.error('Failed to fetch user profile:', error)
      logout()
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (ldap_id: string, password: string) => {
    try {
      const response = await axios.post('/api/auth/login', {
        ldap_id,
        password
      })
      
      const { token: newToken, user: userData } = response.data
      
      // Save token to cookies
      Cookies.set('auth_token', newToken, { expires: 7 }) // 7 days
      
      // Update state
      setToken(newToken)
      setUser(userData)
      
      // Set default headers for axios
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
      
    } catch (error: any) {
      console.error('Login failed:', error)
      throw new Error(error.response?.data?.detail || 'Login failed')
    }
  }

  const register = async (userData: any) => {
    try {
      await axios.post('/api/auth/register', userData)
      // After registration, login the user
      await login(userData.ldap_id, userData.password)
    } catch (error: any) {
      console.error('Registration failed:', error)
      throw new Error(error.response?.data?.detail || 'Registration failed')
    }
  }

  const logout = () => {
    // Clear token from cookies
    Cookies.remove('auth_token')
    
    // Clear axios headers
    delete axios.defaults.headers.common['Authorization']
    
    // Clear state
    setToken(null)
    setUser(null)

    setIsLoading(false)
  }

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
