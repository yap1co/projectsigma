'use client'

import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { useQuery } from 'react-query'
import api from '@/lib/api'
import ProfileSetup from './ProfileSetup'
import RecommendationResults from './RecommendationResults'
import Header from './Header'

export default function Dashboard() {
  const { user } = useAuth()
  const [currentStep, setCurrentStep] = useState<'profile' | 'recommendations'>('profile')
  const [recommendations, setRecommendations] = useState(null)

  const { data: coursesData } = useQuery(
    'courses',
    async () => {
      const response = await api.get('/courses?limit=10')
      return response.data
    }
  )

  const handleGetRecommendations = async (criteria: any) => {
    try {
      const response = await api.post('/recommendations', criteria)
      setRecommendations(response.data)
      setCurrentStep('recommendations')
    } catch (error) {
      console.error('Failed to get recommendations:', error)
    }
  }

  const isProfileComplete = user && 
    user.aLevelSubjects.length > 0 && 
    Object.keys(user.predictedGrades).length > 0 && 
    Object.keys(user.preferences).length > 0

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome, {user?.firstName}!
          </h1>
          <p className="mt-2 text-gray-600">
            {isProfileComplete 
              ? "Your profile is complete. Ready to find your perfect course?"
              : "Let's set up your profile to get personalized recommendations."
            }
          </p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center">
            <div className={`flex items-center ${isProfileComplete ? 'text-primary-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                isProfileComplete ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-600'
              }`}>
                {isProfileComplete ? (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  <span className="text-sm font-medium">1</span>
                )}
              </div>
              <span className="ml-2 font-medium">Profile Setup</span>
            </div>
            
            <div className="flex-1 h-0.5 bg-gray-200 mx-4"></div>
            
            <div className={`flex items-center ${currentStep === 'recommendations' ? 'text-primary-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                currentStep === 'recommendations' ? 'bg-primary-600 text-white' : 'bg-gray-200 text-gray-600'
              }`}>
                <span className="text-sm font-medium">2</span>
              </div>
              <span className="ml-2 font-medium">Get Recommendations</span>
            </div>
          </div>
        </div>

        {/* Main Content */}
        {currentStep === 'profile' && (
          <ProfileSetup 
            onComplete={handleGetRecommendations}
            isComplete={isProfileComplete}
          />
        )}

        {currentStep === 'recommendations' && recommendations && (
          <RecommendationResults 
            recommendations={recommendations}
            onBack={() => setCurrentStep('profile')}
          />
        )}

        {/* Quick Stats */}
        {coursesData && (
          <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card">
              <div className="card-body text-center">
                <div className="text-2xl font-bold text-primary-600">
                  {coursesData.total || 0}
                </div>
                <div className="text-sm text-gray-600">Available Courses</div>
              </div>
            </div>
            
            <div className="card">
              <div className="card-body text-center">
                <div className="text-2xl font-bold text-success-600">
                  95%
                </div>
                <div className="text-sm text-gray-600">Match Accuracy</div>
              </div>
            </div>
            
            <div className="card">
              <div className="card-body text-center">
                <div className="text-2xl font-bold text-secondary-600">
                  150+
                </div>
                <div className="text-sm text-gray-600">Universities</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}