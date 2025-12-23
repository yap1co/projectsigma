'use client'

import React, { Fragment, useState } from 'react'
import { Dialog, Transition } from '@headlessui/react'
import api from '@/lib/api'
import toast from 'react-hot-toast'

interface CourseDetailsModalProps {
  course: any
  isOpen: boolean
  onClose: () => void
}

export default function CourseDetailsModal({ course, isOpen, onClose }: CourseDetailsModalProps) {
  const [feedbackState, setFeedbackState] = useState<'positive' | 'negative' | null>(null)

  if (!course) {
    return null
  }

  const courseId = course.course?.course_id || course.course?.courseId || course.courseId
  const matchScore = course.matchScore || 0

  const handleFeedback = async (feedbackType: 'positive' | 'negative') => {
    if (!courseId) {
      toast.error('Course ID not available')
      return
    }

    try {
      // Update local state immediately
      setFeedbackState(feedbackType)

      // Submit feedback
      await api.post('/recommendations/feedback', {
        courseId: courseId,
        feedbackType: feedbackType,
        matchScore: matchScore,
        searchCriteria: {}
      })

      toast.success('Feedback submitted! This helps improve your future recommendations.')
    } catch (error: any) {
      // Revert state on error
      setFeedbackState(null)
      const errorMessage = error?.response?.data?.message || 'Failed to submit feedback'
      toast.error(errorMessage)
    }
  }

  const universityName = course.course?.university?.name || course.university?.name || ''
  const universityUrl = course.course?.university?.websiteUrl || course.university?.websiteUrl
  const universityLink: React.ReactNode = universityUrl ? (
    <a 
      href={universityUrl} 
      target="_blank" 
      rel="noopener noreferrer"
      className="text-indigo-700 hover:text-indigo-900 hover:underline"
    >
      {universityName}
    </a>
  ) : (
    <span>{universityName}</span>
  )

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black bg-opacity-25" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4 text-center">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-3xl transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                <Dialog.Title
                  as="h3"
                  className="text-2xl font-bold leading-6 text-gray-900 mb-4"
                >
                  {(course.course?.courseUrl || course.courseUrl) ? (
                    <a 
                      href={course.course?.courseUrl || course.courseUrl} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-primary-600 hover:text-primary-800 hover:underline"
                    >
                      {course.course?.name || course.name}
                    </a>
                  ) : (
                    course.course?.name || course.name
                  )}
                </Dialog.Title>

                <div className="space-y-6 max-h-[70vh] overflow-y-auto pr-2">
                  {/* University Info */}
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">University</h4>
                    <p className="text-gray-700">
                      {(course.course?.university?.websiteUrl || course.university?.websiteUrl) ? (
                        <a 
                          href={course.course?.university?.websiteUrl || course.university?.websiteUrl} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-primary-600 hover:text-primary-800 hover:underline"
                        >
                          {course.course?.university?.name || course.university?.name}
                        </a>
                      ) : (
                        course.course?.university?.name || course.university?.name
                      )}
                    </p>
                    {course.course?.university?.region && (
                      <p className="text-sm text-gray-500 mt-1">Region: {course.course.university.region}</p>
                    )}
                    {course.course?.university?.ranking?.overall && (
                      <p className="text-sm text-gray-500">Ranking: #{course.course.university.ranking.overall}</p>
                    )}
                  </div>

                  {/* Course Details */}
                  <div>
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">Course Details</h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-500">Duration</p>
                        <p className="text-gray-900">{course.course?.duration || 'N/A'} years</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Annual Fee</p>
                        <p className="text-gray-900">£{course.course?.fees?.uk?.toLocaleString() || course.course?.annual_fee?.toLocaleString() || 'N/A'}</p>
                      </div>
                      {course.course?.ucas_code && (
                        <div>
                          <p className="text-sm text-gray-500">UCAS Code</p>
                          <p className="text-gray-900">{course.course.ucas_code}</p>
                        </div>
                      )}
                      {course.course?.employability?.employmentRate && (
                        <div>
                          <p className="text-sm text-gray-500">Employment Rate</p>
                          <p className="text-gray-900">{course.course.employability.employmentRate}%</p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Entry Requirements */}
                  {(course.course?.entryRequirements?.grades || course.entryRequirements?.grades) && (
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-2">Entry Requirements</h4>
                      <div className="flex flex-wrap gap-2">
                        {Object.entries(course.course?.entryRequirements?.grades || course.entryRequirements?.grades || {}).map(([subject, grade]) => (
                          <span key={subject} className="inline-block bg-primary-100 text-primary-800 rounded px-3 py-1 text-sm font-medium">
                            {subject}: {String(grade)}
                          </span>
                        ))}
                      </div>
                      {course.course?.typical_offer_text && (
                        <p className="text-sm text-gray-600 mt-2">{course.course.typical_offer_text}</p>
                      )}
                      {course.course?.typical_offer_tariff && (
                        <p className="text-sm text-gray-600 mt-1">Typical Offer Tariff: {course.course.typical_offer_tariff}</p>
                      )}
                    </div>
                  )}

                  {/* Match Reasons */}
                  {course.reasons && course.reasons.length > 0 && (
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-2">Why This Matches Your Profile</h4>
                      <ul className="list-disc list-inside space-y-1">
                        {course.reasons.map((reason: string, index: number) => (
                          <li key={index} className="text-gray-700">{reason}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Match Score */}
                  {course.matchScore !== undefined && (
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-2">Match Score</h4>
                      <div className="flex items-center space-x-4">
                        <div className="flex-1 bg-gray-200 rounded-full h-4">
                          <div
                            className="bg-primary-600 h-4 rounded-full"
                            style={{ width: `${Math.round(course.matchScore * 100)}%` }}
                          ></div>
                        </div>
                        <span className="text-lg font-semibold text-primary-600">
                          {Math.round(course.matchScore * 100)}%
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Employment Outcomes */}
                  {course.course?.employmentOutcomes && (
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <h4 className="text-lg font-semibold text-gray-900 mb-3">Graduate Employment Outcomes</h4>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {course.course.employmentOutcomes.employed !== null && (
                          <div>
                            <div className="text-sm text-gray-600">Employed</div>
                            <div className="text-lg font-semibold text-green-700">
                              {course.course.employmentOutcomes.employed?.toLocaleString() || 'N/A'}
                            </div>
                          </div>
                        )}
                        {course.course.employmentOutcomes.studying !== null && (
                          <div>
                            <div className="text-sm text-gray-600">Studying</div>
                            <div className="text-lg font-semibold text-blue-700">
                              {course.course.employmentOutcomes.studying?.toLocaleString() || 'N/A'}
                            </div>
                          </div>
                        )}
                        {course.course.employmentOutcomes.unemployed !== null && (
                          <div>
                            <div className="text-sm text-gray-600">Unemployed</div>
                            <div className="text-lg font-semibold text-red-700">
                              {course.course.employmentOutcomes.unemployed?.toLocaleString() || 'N/A'}
                            </div>
                          </div>
                        )}
                        {course.course.employmentOutcomes.totalGraduates !== null && (
                          <div>
                            <div className="text-sm text-gray-600">Total Graduates</div>
                            <div className="text-lg font-semibold text-gray-700">
                              {course.course.employmentOutcomes.totalGraduates?.toLocaleString() || 'N/A'}
                            </div>
                          </div>
                        )}
                      </div>
                      {course.course.employmentOutcomes.responseRate !== null && (
                        <div className="mt-3 text-sm text-gray-500">
                          Response Rate: {course.course.employmentOutcomes.responseRate}%
                        </div>
                      )}
                    </div>
                  )}

                  {/* Salary & Earnings */}
                  {(course.course?.salaryData || course.course?.earningsData) && (
                    <div className="p-4 bg-green-50 rounded-lg">
                      <h4 className="text-lg font-semibold text-gray-900 mb-3">Graduate Earnings</h4>
                      <div className="space-y-3">
                        {course.course.salaryData?.medianSalary && (
                          <div>
                            <div className="text-sm text-gray-600">Starting Salary (Median)</div>
                            <div className="text-xl font-semibold text-green-700">
                              £{course.course.salaryData.medianSalary.toLocaleString()}
                            </div>
                            {course.course.salaryData.lowerQuartile && course.course.salaryData.upperQuartile && (
                              <div className="text-sm text-gray-500 mt-1">
                                Range: £{course.course.salaryData.lowerQuartile.toLocaleString()} - £{course.course.salaryData.upperQuartile.toLocaleString()}
                              </div>
                            )}
                          </div>
                        )}
                        {course.course.earningsData?.median3Years && (
                          <div>
                            <div className="text-sm text-gray-600">Earnings After 3 Years (Median)</div>
                            <div className="text-xl font-semibold text-green-700">
                              £{course.course.earningsData.median3Years.toLocaleString()}
                            </div>
                            {course.course.earningsData.lowerQuartile3Years && course.course.earningsData.upperQuartile3Years && (
                              <div className="text-sm text-gray-500 mt-1">
                                Range: £{course.course.earningsData.lowerQuartile3Years.toLocaleString()} - £{course.course.earningsData.upperQuartile3Years.toLocaleString()}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Common Job Types */}
                  {course.course?.commonJobTypes && course.course.commonJobTypes.length > 0 && (
                    <div className="p-4 bg-purple-50 rounded-lg">
                      <h4 className="text-lg font-semibold text-gray-900 mb-3">Common Job Types for Graduates</h4>
                      <div className="space-y-2">
                        {course.course.commonJobTypes.map((job: any, idx: number) => (
                          <div key={idx} className="flex justify-between items-center">
                            <span className="text-gray-700">{job.job}</span>
                            <span className="font-semibold text-purple-700 text-lg">{job.percentage}%</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Entry Statistics */}
                  {course.course?.entryStatistics && (
                    <div className="p-4 bg-yellow-50 rounded-lg">
                      <h4 className="text-lg font-semibold text-gray-900 mb-3">Student Entry Profile</h4>
                      <div className="space-y-2 text-sm">
                        {course.course.entryStatistics.aLevelStudents !== null && (
                          <div>
                            <span className="font-medium text-gray-900">A-Level Students:</span>{' '}
                            <span className="text-gray-700">{course.course.entryStatistics.aLevelStudents.toLocaleString()}</span>
                            {course.course.entryStatistics.totalEntryPopulation && (
                              <span className="text-gray-500 ml-2">
                                ({Math.round((course.course.entryStatistics.aLevelStudents / course.course.entryStatistics.totalEntryPopulation) * 100)}%)
                              </span>
                            )}
                          </div>
                        )}
                        {course.course.entryStatistics.totalEntryPopulation !== null && (
                          <div className="text-gray-500">
                            Total Entry Population: {course.course.entryStatistics.totalEntryPopulation.toLocaleString()} students
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* University's Best Course */}
                  {course.universityBestCourse && (
                    <div className="p-4 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg border border-indigo-200">
                      <div className="flex items-center mb-3">
                        <svg className="w-6 h-6 text-indigo-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                        </svg>
                        <h4 className="text-lg font-semibold text-gray-900">
                          {universityLink}'s Best Course (Highest Employability)
                        </h4>
                      </div>
                      
                      <div className="bg-white rounded-lg p-4 shadow-sm">
                        <h5 className="font-bold text-gray-900 text-lg mb-2">
                          {course.universityBestCourse.courseUrl ? (
                            <a 
                              href={course.universityBestCourse.courseUrl} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-indigo-700 hover:text-indigo-900 hover:underline"
                            >
                              {course.universityBestCourse.name}
                            </a>
                          ) : (
                            course.universityBestCourse.name
                          )}
                        </h5>
                        
                        <div className="grid grid-cols-2 gap-4 mb-3">
                          {course.universityBestCourse.employability?.employmentRate && (
                            <div>
                              <div className="text-sm text-gray-600">Employability Score</div>
                              <div className="font-bold text-indigo-700 text-xl">
                                {course.universityBestCourse.employability.employmentRate}%
                              </div>
                            </div>
                          )}
                          {course.universityBestCourse.fees?.uk && (
                            <div>
                              <div className="text-sm text-gray-600">Annual Fee</div>
                              <div className="font-semibold text-gray-900 text-lg">
                                £{course.universityBestCourse.fees.uk.toLocaleString()}
                              </div>
                            </div>
                          )}
                        </div>
                        
                        {course.universityBestCourse.entryRequirements?.grades && 
                         Object.keys(course.universityBestCourse.entryRequirements.grades).length > 0 && (
                          <div className="mb-3 pt-3 border-t border-gray-200">
                            <div className="text-sm text-gray-600 mb-2">Entry Requirements:</div>
                            <div className="flex flex-wrap gap-2">
                              {Object.entries(course.universityBestCourse.entryRequirements.grades)
                                .slice(0, 5)
                                .map(([subject, grade]) => (
                                <span key={subject} className="inline-block bg-indigo-100 text-indigo-800 rounded px-3 py-1 text-sm font-medium">
                                  {subject}: {String(grade)}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {(course.universityBestCourse.employmentOutcomes || course.universityBestCourse.salaryData || course.universityBestCourse.earningsData) && (
                          <div className="pt-3 border-t border-gray-200">
                            <div className="grid grid-cols-3 gap-3 text-sm">
                              {course.universityBestCourse.employmentOutcomes?.employed !== null && (
                                <div>
                                  <div className="text-gray-600">Employed</div>
                                  <div className="font-semibold text-green-700">
                                    {course.universityBestCourse.employmentOutcomes.employed?.toLocaleString() || 'N/A'}
                                  </div>
                                </div>
                              )}
                              {course.universityBestCourse.salaryData?.medianSalary && (
                                <div>
                                  <div className="text-gray-600">Median Salary</div>
                                  <div className="font-semibold text-green-700">
                                    £{course.universityBestCourse.salaryData.medianSalary.toLocaleString()}
                                  </div>
                                </div>
                              )}
                              {course.universityBestCourse.earningsData?.median3Years && (
                                <div>
                                  <div className="text-gray-600">3yr Earnings</div>
                                  <div className="font-semibold text-green-700">
                                    £{course.universityBestCourse.earningsData.median3Years.toLocaleString()}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                      
                      <p className="text-sm text-gray-600 mt-3 italic">
                        This is the course with the highest employability score at {universityLink}, 
                        representing their strongest program.
                      </p>
                    </div>
                  )}
                </div>

                {/* Feedback Section */}
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-sm text-gray-600 font-medium">Was this recommendation helpful?</span>
                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => handleFeedback('positive')}
                        className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg transition-all ${
                          feedbackState === 'positive'
                            ? 'bg-green-100 text-green-700 border-2 border-green-500'
                            : 'bg-gray-100 text-gray-600 hover:bg-green-50 hover:text-green-600 border-2 border-transparent'
                        }`}
                        title="This recommendation is helpful"
                      >
                        <span className="text-xl">👍</span>
                        <span className="text-sm font-medium">Helpful</span>
                      </button>
                      <button
                        onClick={() => handleFeedback('negative')}
                        className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg transition-all ${
                          feedbackState === 'negative'
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

                <div className="mt-4 flex justify-end">
                  <button
                    type="button"
                    className="btn-secondary"
                    onClick={onClose}
                  >
                    Close
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  )
}
