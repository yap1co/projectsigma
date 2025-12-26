'use client'

import { useState } from 'react'
import { useQuery } from 'react-query'
import api from '@/lib/api'
import toast from 'react-hot-toast'
import CourseDetailsModal from './CourseDetailsModal'

interface RecommendationResultsProps {
  recommendations: any
  onBack: () => void
}

export default function RecommendationResults({ recommendations, onBack }: RecommendationResultsProps) {
  const [sortBy, setSortBy] = useState('matchScore')
  const [filterBy, setFilterBy] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCourse, setSelectedCourse] = useState<any>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [feedbackStates, setFeedbackStates] = useState<Record<string, 'positive' | 'negative' | null>>({})

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
      // For PDF, we need to request as blob. For CSV, we can use JSON response
      const config = format === 'pdf' 
        ? { responseType: 'blob' as const }
        : { responseType: 'json' as const }
      
      const response = await api.get(
        `/export/recommendations/${recommendations.studentId}?format=${format}`,
        config
      )
      
      if (format === 'csv') {
        // CSV is returned as JSON with data field
        const blob = new Blob([response.data.data], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'course-recommendations.csv'
        a.click()
        window.URL.revokeObjectURL(url)
      } else if (format === 'pdf') {
        // PDF is returned as binary blob
        const blob = new Blob([response.data], { type: 'application/pdf' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'course-recommendations.pdf'
        a.click()
        window.URL.revokeObjectURL(url)
      }
      
      toast.success(`Recommendations exported as ${format.toUpperCase()}`)
    } catch (error: any) {
      console.error('Export error:', error)
      const errorMessage = error?.response?.data?.message || 'Failed to export recommendations'
      toast.error(errorMessage)
    }
  }

  const handleFeedback = async (courseId: string, feedbackType: 'positive' | 'negative', matchScore: number) => {
    try {
      // Update local state immediately for responsive UI
      setFeedbackStates(prev => ({
        ...prev,
        [courseId]: feedbackType
      }))

      // Submit feedback to backend
      await api.post('/recommendations/feedback', {
        courseId: courseId,
        feedbackType: feedbackType,
        matchScore: matchScore,
        searchCriteria: {
          sortBy,
          filterBy,
          searchTerm
        }
      })

      toast.success(`Feedback submitted! This helps improve your future recommendations.`)
    } catch (error: any) {
      // Revert state on error
      setFeedbackStates(prev => ({
        ...prev,
        [courseId]: null
      }))
      
      const errorMessage = error?.response?.data?.message || 'Failed to submit feedback'
      toast.error(errorMessage)
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
      // First, prioritize courses that meet all requirements
      if (a.meetsRequirements !== b.meetsRequirements) {
        return a.meetsRequirements ? -1 : 1
      }
      
      // Then sort by selected criteria
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
                      {recommendation.course.courseUrl ? (
                        <a 
                          href={recommendation.course.courseUrl} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-primary-600 hover:text-primary-800 hover:underline"
                        >
                          {recommendation.course.name}
                        </a>
                      ) : (
                        recommendation.course.name
                      )}
                    </h3>
                    {recommendation.meetsRequirements === false && (
                      <span className="px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 border border-yellow-300" title="You don't meet all entry requirements for this course">
                        ⚠ Requirements Not Met
                      </span>
                    )}
                    <span className={`match-score ${getMatchScoreClass(recommendation.matchScore)}`}>
                      {getMatchScoreText(recommendation.matchScore)} ({formatMatchScore(recommendation.matchScore)}%)
                    </span>
                  </div>
                  
                  <p className="text-gray-600 mb-2">
                    {recommendation.course.university.websiteUrl ? (
                      <a 
                        href={recommendation.course.university.websiteUrl} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-primary-600 hover:text-primary-800 hover:underline font-medium inline-flex items-center gap-1"
                      >
                        {recommendation.course.university.name}
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                      </a>
                    ) : (
                      recommendation.course.university.name
                    )}
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
                      {subject}: {String(grade)}
                    </span>
                  ))}
                </div>
              </div>

              {/* Employment Outcomes */}
              {recommendation.course.employmentOutcomes && (
                <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Graduate Employment Outcomes:</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    {recommendation.course.employmentOutcomes.employed !== null && (
                      <div>
                        <div className="text-gray-600">Employed</div>
                        <div className="font-semibold text-green-700">
                          {recommendation.course.employmentOutcomes.employed?.toLocaleString() || 'N/A'}
                        </div>
                      </div>
                    )}
                    {recommendation.course.employmentOutcomes.studying !== null && (
                      <div>
                        <div className="text-gray-600">Studying</div>
                        <div className="font-semibold text-blue-700">
                          {recommendation.course.employmentOutcomes.studying?.toLocaleString() || 'N/A'}
                        </div>
                      </div>
                    )}
                    {recommendation.course.employmentOutcomes.unemployed !== null && (
                      <div>
                        <div className="text-gray-600">Unemployed</div>
                        <div className="font-semibold text-red-700">
                          {recommendation.course.employmentOutcomes.unemployed?.toLocaleString() || 'N/A'}
                        </div>
                      </div>
                    )}
                    {recommendation.course.employmentOutcomes.totalGraduates !== null && (
                      <div>
                        <div className="text-gray-600">Total Graduates</div>
                        <div className="font-semibold text-gray-700">
                          {recommendation.course.employmentOutcomes.totalGraduates?.toLocaleString() || 'N/A'}
                        </div>
                      </div>
                    )}
                  </div>
                  {recommendation.course.employmentOutcomes.responseRate !== null && (
                    <div className="mt-2 text-xs text-gray-500">
                      Response Rate: {recommendation.course.employmentOutcomes.responseRate}%
                    </div>
                  )}
                </div>
              )}

              {/* Salary & Earnings Data */}
              {(recommendation.course.salaryData || recommendation.course.earningsData) && (
                <div className="mb-4 p-3 bg-green-50 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Graduate Earnings:</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    {recommendation.course.salaryData?.medianSalary && (
                      <div>
                        <div className="text-gray-600">Starting Salary (Median)</div>
                        <div className="font-semibold text-green-700">
                          £{recommendation.course.salaryData.medianSalary.toLocaleString()}
                        </div>
                        {recommendation.course.salaryData.lowerQuartile && recommendation.course.salaryData.upperQuartile && (
                          <div className="text-xs text-gray-500 mt-1">
                            Range: £{recommendation.course.salaryData.lowerQuartile.toLocaleString()} - £{recommendation.course.salaryData.upperQuartile.toLocaleString()}
                          </div>
                        )}
                      </div>
                    )}
                    {recommendation.course.earningsData?.median3Years && (
                      <div>
                        <div className="text-gray-600">Earnings After 3 Years (Median)</div>
                        <div className="font-semibold text-green-700">
                          £{recommendation.course.earningsData.median3Years.toLocaleString()}
                        </div>
                        {recommendation.course.earningsData.lowerQuartile3Years && recommendation.course.earningsData.upperQuartile3Years && (
                          <div className="text-xs text-gray-500 mt-1">
                            Range: £{recommendation.course.earningsData.lowerQuartile3Years.toLocaleString()} - £{recommendation.course.earningsData.upperQuartile3Years.toLocaleString()}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Common Job Types */}
              {recommendation.course.commonJobTypes && recommendation.course.commonJobTypes.length > 0 && (
                <div className="mb-4 p-3 bg-purple-50 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Common Job Types for Graduates:</h4>
                  <div className="space-y-1">
                    {recommendation.course.commonJobTypes.map((job: any, idx: number) => (
                      <div key={idx} className="flex justify-between items-center text-sm">
                        <span className="text-gray-700">{job.job}</span>
                        <span className="font-semibold text-purple-700">{job.percentage}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Entry Statistics */}
              {recommendation.course.entryStatistics && (
                <div className="mb-4 p-3 bg-yellow-50 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Student Entry Profile:</h4>
                  <div className="text-sm text-gray-600">
                    {recommendation.course.entryStatistics.aLevelStudents !== null && (
                      <div className="mb-1">
                        <span className="font-medium">A-Level Students:</span>{' '}
                        {recommendation.course.entryStatistics.aLevelStudents.toLocaleString()}
                        {recommendation.course.entryStatistics.totalEntryPopulation && (
                          <span className="text-gray-500">
                            {' '}({Math.round((recommendation.course.entryStatistics.aLevelStudents / recommendation.course.entryStatistics.totalEntryPopulation) * 100)}%)
                          </span>
                        )}
                      </div>
                    )}
                    {recommendation.course.entryStatistics.totalEntryPopulation !== null && (
                      <div className="text-xs text-gray-500 mt-1">
                        Total Entry Population: {recommendation.course.entryStatistics.totalEntryPopulation.toLocaleString()} students
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* University's Best Course */}
              {recommendation.universityBestCourse && (
                <div className="mb-4 p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-200">
                  <div className="flex items-center mb-3">
                    <svg className="w-5 h-5 text-indigo-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                    </svg>
                    <h4 className="text-sm font-semibold text-gray-900">
                      {recommendation.course.university.name}'s Best Course (Highest Employability)
                    </h4>
                  </div>
                  
                  <div className="bg-white rounded-lg p-3 shadow-sm">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <h5 className="font-semibold text-gray-900 text-base">
                          {recommendation.universityBestCourse.courseUrl ? (
                            <a 
                              href={recommendation.universityBestCourse.courseUrl} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-indigo-700 hover:text-indigo-900 hover:underline"
                            >
                              {recommendation.universityBestCourse.name}
                            </a>
                          ) : (
                            recommendation.universityBestCourse.name
                          )}
                        </h5>
                        {recommendation.universityBestCourse.employability?.employmentRate && (
                          <div className="mt-1">
                            <span className="text-xs text-gray-600">Employability Score: </span>
                            <span className="font-bold text-indigo-700 text-sm">
                              {recommendation.universityBestCourse.employability.employmentRate}%
                            </span>
                          </div>
                        )}
                      </div>
                      {recommendation.universityBestCourse.fees?.uk && (
                        <div className="text-right">
                          <div className="text-xs text-gray-600">Annual Fee</div>
                          <div className="font-semibold text-gray-900">
                            £{recommendation.universityBestCourse.fees.uk.toLocaleString()}
                          </div>
                        </div>
                      )}
                    </div>
                    
                    {recommendation.universityBestCourse.entryRequirements?.grades && 
                     Object.keys(recommendation.universityBestCourse.entryRequirements.grades).length > 0 && (
                      <div className="mt-2 pt-2 border-t border-gray-200">
                        <div className="text-xs text-gray-600 mb-1">Entry Requirements:</div>
                        <div className="flex flex-wrap gap-1">
                          {Object.entries(recommendation.universityBestCourse.entryRequirements.grades)
                            .slice(0, 3)
                            .map(([subject, grade]) => (
                            <span key={subject} className="inline-block bg-indigo-100 text-indigo-800 rounded px-2 py-0.5 text-xs font-medium">
                              {subject}: {String(grade)}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {recommendation.universityBestCourse.employmentOutcomes && (
                      <div className="mt-2 pt-2 border-t border-gray-200">
                        <div className="grid grid-cols-3 gap-2 text-xs">
                          {recommendation.universityBestCourse.employmentOutcomes.employed !== null && (
                            <div>
                              <div className="text-gray-600">Employed</div>
                              <div className="font-semibold text-green-700">
                                {recommendation.universityBestCourse.employmentOutcomes.employed?.toLocaleString() || 'N/A'}
                              </div>
                            </div>
                          )}
                          {recommendation.universityBestCourse.salaryData?.medianSalary && (
                            <div>
                              <div className="text-gray-600">Median Salary</div>
                              <div className="font-semibold text-green-700">
                                £{recommendation.universityBestCourse.salaryData.medianSalary.toLocaleString()}
                              </div>
                            </div>
                          )}
                          {recommendation.universityBestCourse.earningsData?.median3Years && (
                            <div>
                              <div className="text-gray-600">3yr Earnings</div>
                              <div className="font-semibold text-green-700">
                                £{recommendation.universityBestCourse.earningsData.median3Years.toLocaleString()}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <p className="text-xs text-gray-600 mt-2 italic">
                    This is the course with the highest employability score at{' '}
                    {recommendation.course.university.websiteUrl ? (
                      <a 
                        href={recommendation.course.university.websiteUrl} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-indigo-700 hover:text-indigo-900 hover:underline"
                      >
                        {recommendation.course.university.name}
                      </a>
                    ) : (
                      recommendation.course.university.name
                    )}, 
                    representing their strongest program.
                  </p>
                </div>
              )}

              {/* Feedback Section */}
              <div className="mb-4 pt-4 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 font-medium">Was this recommendation helpful?</span>
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={() => handleFeedback(
                        recommendation.course.course_id || recommendation.course.courseId,
                        'positive',
                        recommendation.matchScore
                      )}
                      className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg transition-all ${
                        feedbackStates[recommendation.course.course_id || recommendation.course.courseId] === 'positive'
                          ? 'bg-green-100 text-green-700 border-2 border-green-500'
                          : 'bg-gray-100 text-gray-600 hover:bg-green-50 hover:text-green-600 border-2 border-transparent'
                      }`}
                      title="This recommendation is helpful"
                    >
                      <span className="text-xl">👍</span>
                      <span className="text-sm font-medium">Helpful</span>
                    </button>
                    <button
                      onClick={() => handleFeedback(
                        recommendation.course.course_id || recommendation.course.courseId,
                        'negative',
                        recommendation.matchScore
                      )}
                      className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg transition-all ${
                        feedbackStates[recommendation.course.course_id || recommendation.course.courseId] === 'negative'
                          ? 'bg-red-100 text-red-700 border-2 border-red-500'
                          : 'bg-gray-100 text-gray-600 hover:bg-red-50 hover:text-red-600 border-2 border-transparent'
                      }`}
                      title="This recommendation is not helpful"
                    >
                      <span className="text-xl">👎</span>
                      <span className="text-sm font-medium">Not Helpful</span>
                    </button>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-between items-center pt-2 border-t border-gray-200">
                <div className="flex space-x-2">
                  <button 
                    className="btn-primary"
                    onClick={() => {
                      setSelectedCourse(recommendation)
                      setIsModalOpen(true)
                    }}
                  >
                    View Details
                  </button>
                  <button 
                    className="btn-secondary"
                    onClick={() => toast('Save to Favorites feature coming soon!', { icon: 'ℹ️' })}
                  >
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

      {/* Course Details Modal */}
      <CourseDetailsModal
        course={selectedCourse}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedCourse(null)
        }}
      />
    </div>
  )
}
