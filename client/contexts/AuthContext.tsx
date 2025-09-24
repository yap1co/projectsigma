'use client'

import React, { createContext, useContext, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Cookies from 'js-cookie'
import api from '@/lib/api'
import toast from 'react-hot-toast'

interface User {
  _id: string
  email: string
  firstName: string
  lastName: string
  yearGroup: string
  aLevelSubjects: string[]
  predictedGrades: Record<string, string>
  preferences: Record<string, any>
  createdAt: string
  lastLogin?: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (userData: RegisterData) => Promise<void>
  logout: () => void
  updateUser: (userData: Partial<User>) => void
}

interface RegisterData {
  email: string
  password: string
  firstName: string
  lastName: string
  yearGroup?: string
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const token = Cookies.get('access_token')
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [])

  const fetchUser = async () => {
    try {
      const response = await api.get('/student/profile')
      setUser(response.data.student)
    } catch (error) {
      console.error('Failed to fetch user:', error)
      Cookies.remove('access_token')
      delete api.defaults.headers.common['Authorization']
    } finally {
      setLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    try {
      const response = await api.post('/auth/login', { email, password })
      const { access_token, student_id } = response.data
      
      Cookies.set('access_token', access_token, { expires: 7 })
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      // Fetch user data
      await fetchUser()
      
      toast.success('Login successful!')
      router.push('/')
    } catch (error: any) {
      const message = error.response?.data?.message || 'Login failed'
      toast.error(message)
      throw new Error(message)
    }
  }

  const register = async (userData: RegisterData) => {
    try {
      const response = await api.post('/auth/register', userData)
      const { access_token, student_id } = response.data
      
      Cookies.set('access_token', access_token, { expires: 7 })
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      // Fetch user data
      await fetchUser()
      
      toast.success('Registration successful!')
      router.push('/')
    } catch (error: any) {
      const message = error.response?.data?.message || 'Registration failed'
      toast.error(message)
      throw new Error(message)
    }
  }

  const logout = () => {
    Cookies.remove('access_token')
    delete api.defaults.headers.common['Authorization']
    setUser(null)
    toast.success('Logged out successfully')
    router.push('/auth/login')
  }

  const updateUser = (userData: Partial<User>) => {
    if (user) {
      setUser({ ...user, ...userData })
    }
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, updateUser }}>
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