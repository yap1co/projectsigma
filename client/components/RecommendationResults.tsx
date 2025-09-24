'use client'

import { useState } from 'react'
import { useQuery } from 'react-query'
import api from '@/lib/api'
import toast from 'react-hot-toast'

interface RecommendationResultsProps {
  recommendations: any
  onBack: () => void
}

export default function RecommendationResults({ recommendations, onBack }: RecommendationResultsProps) {
  const [sortBy, setSortBy] = useState('matchScore')
  const [filterBy, setFilterBy] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')

  const getMatchScoreClass = (score: number) => {
    if (score >= 0.8) return 'match-excellent'
    if (score >= 0.6) return 'match-good'
    if (score >= 0.4) return 'match-fair'
    return 'match-poor'
  }

  const getMatchScoreText = (score: number) => {
    if (score >= 0.8) return 'Excellent Match'
    if (score >= 0.6) return 'Good Match'
    if (score >= 0.4) return 'Fair Match'
    return 'Poor Match'
  }

  const formatMatchScore = (score: number) => {
    return Math.round(score * 100)
  }

  const handleExport = async (format: 'csv' | 'pdf') => {
    try {
      const response = await api.get(`/export/recommendations/${recommendations.studentId}?format=${format}`)
      
      if (format === 'csv') {
        const blob = new Blob([response.data.data], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'course-recommendations.csv'
        a.click()
        window.URL.revokeObjectURL(url)
      }
      
      toast.success(`Recommendations exported as ${format.toUpperCase()}`)
    } catch (error) {
      toast.error('Failed to export recommendations')
    }
  }

  const filteredRecommendations = recommendations.recommendations
    .filter((rec: any) => {
      if (filterBy !== 'all' && rec.course.university.region !== filterBy) {
        return false
      }
      if (searchTerm && !rec.course.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
          !rec.course.university.name.toLowerCase().includes(searchTerm.toLowerCase())) {
        return false
      }
      return true
    })
    .sort((a: any, b: any) => {
      if (sortBy === 'matchScore') {
        return b.matchScore - a.matchScore
      } else if (sortBy === 'fees') {
        return a.course.fees.uk - b.course.fees.uk
      } else if (sortBy === 'ranking') {
        return (a.course.university.ranking?.overall || 999) - (b.course.university.ranking?.overall || 999)
      }
      return 0
    })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="card-header">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Your Course Recommendations
              </h2>
              <p className="mt-1 text-sm text-gray-600">
                {filteredRecommendations.length} courses found based on your profile
              </p>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => handleExport('csv')}
                className="btn-secondary"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Export CSV
              </button>
              <button
                onClick={() => handleExport('pdf')}
                className="btn-secondary"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
                Export PDF
              </button>
            </div>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="card-body border-t border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Search
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search courses or universities..."
                className="input"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Sort by
              </label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="input"
              >
                <option value="matchScore">Match Score</option>
                <option value="fees">Fees (Low to High)</option>
                <option value="ranking">University Ranking</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Filter by Region
              </label>
              <select
                value={filterBy}
                onChange={(e) => setFilterBy(e.target.value)}
                className="input"
              >
                <option value="all">All Regions</option>
                <option value="London">London</option>
                <option value="South East">South East</option>
                <option value="South West">South West</option>
                <option value="Midlands">Midlands</option>
                <option value="North West">North West</option>
                <option value="North East">North East</option>
                <option value="Scotland">Scotland</option>
                <option value="Wales">Wales</option>
              </select>
            </div>
            
            <div className="flex items-end">
              <button
                onClick={onBack}
                className="btn-secondary w-full"
              >
                Back to Profile
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="space-y-4">
        {filteredRecommendations.map((recommendation: any, index: number) => (
          <div key={index} className="card hover:shadow-lg transition-shadow">
            <div className="card-body">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {recommendation.course.name}
                    </h3>
                    <span className={`match-score ${getMatchScoreClass(recommendation.matchScore)}`}>
                      {getMatchScoreText(recommendation.matchScore)} ({formatMatchScore(recommendation.matchScore)}%)
                    </span>
                  </div>
                  
                  <p className="text-gray-600 mb-2">
                    {recommendation.course.university.name}
                  </p>
                  
                  <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                    <span>£{recommendation.course.fees.uk.toLocaleString()} per year</span>
                    <span>{recommendation.course.duration} years</span>
                    {recommendation.course.university.ranking?.overall && (
                      <span>Ranked #{recommendation.course.university.ranking.overall}</span>
                    )}
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="text-2xl font-bold text-primary-600">
                    #{index + 1}
                  </div>
                </div>
              </div>

              {/* Match Reasons */}
              {recommendation.reasons && recommendation.reasons.length > 0 && (
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Why this matches:</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {recommendation.reasons.map((reason: string, reasonIndex: number) => (
                      <li key={reasonIndex} className="text-sm text-gray-600">
                        {reason}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Entry Requirements */}
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Entry Requirements:</h4>
                <div className="text-sm text-gray-600">
                  {Object.entries(recommendation.course.entryRequirements.grades).map(([subject, grade]) => (
                    <span key={subject} className="inline-block bg-gray-100 rounded px-2 py-1 mr-2 mb-1">
                      {subject}: {grade}
                    </span>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-between items-center pt-4 border-t border-gray-200">
                <div className="flex space-x-2">
                  <button className="btn-primary">
                    View Details
                  </button>
                  <button className="btn-secondary">
                    Save to Favorites
                  </button>
                </div>
                
                <div className="text-sm text-gray-500">
                  Match Score: {formatMatchScore(recommendation.matchScore)}%
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredRecommendations.length === 0 && (
        <div className="card">
          <div className="card-body text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No courses found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your search criteria or filters.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
