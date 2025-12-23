'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { useForm } from 'react-hook-form'
import api from '@/lib/api'
import toast from 'react-hot-toast'

interface ProfileSetupProps {
  onComplete: (criteria: any) => void
  isComplete: boolean
}

interface FormData {
  aLevelSubjects: string[]
  predictedGrades: Record<string, string>
  preferences: {
    preferredRegion: string
    maxBudget: number
    preferredUniSize: string
    preferredCourseLength: string
    careerInterests: string[]
  }
}

const A_LEVEL_SUBJECTS = [
  'Mathematics', 'Further Mathematics', 'Physics', 'Chemistry', 'Biology',
  'English Literature', 'English Language', 'History', 'Geography', 'Economics',
  'Business Studies', 'Psychology', 'Sociology', 'Politics', 'Philosophy',
  'Art', 'Design Technology', 'Computer Science', 'French', 'Spanish',
  'German', 'Italian', 'Latin', 'Classical Civilisation', 'Religious Studies',
  'Music', 'Drama', 'Physical Education', 'Media Studies', 'Film Studies'
]

const REGIONS = [
  'London', 'South East', 'South West', 'Midlands', 'North West',
  'North East', 'Scotland', 'Wales', 'Any'
]

const UNIVERSITY_SIZES = [
  'Small (< 5,000 students)', 'Medium (5,000-15,000 students)', 
  'Large (15,000+ students)', 'Any'
]

const COURSE_LENGTHS = ['3 years', '4 years', '5 years', 'Any']

const CAREER_INTERESTS = [
  'Medicine & Healthcare', 'Engineering & Technology', 'Business & Finance',
  'Law', 'Education', 'Arts & Humanities', 'Sciences', 'Social Sciences',
  'Creative Arts', 'Sports & Fitness', 'Other'
]

export default function ProfileSetup({ onComplete, isComplete }: ProfileSetupProps) {
  const { user, updateUser } = useAuth()
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState(1)

  const { register, handleSubmit, watch, setValue, formState: { errors }, reset } = useForm<FormData>({
    defaultValues: {
      aLevelSubjects: user?.aLevelSubjects || [],
      predictedGrades: user?.predictedGrades || {},
      preferences: user?.preferences || {
        preferredRegion: '',
        maxBudget: 9250,
        preferredUniSize: '',
        preferredCourseLength: '3 years',
        careerInterests: []
      }
    }
  })

  // Update form when user data changes
  useEffect(() => {
    if (user) {
      reset({
        aLevelSubjects: user.aLevelSubjects || [],
        predictedGrades: user.predictedGrades || {},
        preferences: user.preferences || {
          preferredRegion: '',
          maxBudget: 9250,
          preferredUniSize: '',
          preferredCourseLength: '3 years',
          careerInterests: []
        }
      })
    }
  }, [user, reset])

  const watchedSubjects = watch('aLevelSubjects')
  const watchedGrades = watch('predictedGrades')

  const onSubmit = async (data: FormData) => {
    setLoading(true)
    try {
      // Update user profile
      await api.put('/student/profile', {
        aLevelSubjects: data.aLevelSubjects,
        predictedGrades: data.predictedGrades,
        preferences: data.preferences
      })

      updateUser({
        aLevelSubjects: data.aLevelSubjects,
        predictedGrades: data.predictedGrades,
        preferences: data.preferences
      })

      toast.success('Profile updated successfully!')
      
      // Only auto-generate recommendations if this is the first time setup
      // Otherwise, let user click "Get Recommendations" button
      if (!isComplete) {
        onComplete(data.preferences)
      }
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Failed to update profile')
    } finally {
      setLoading(false)
    }
  }

  const handleSubjectToggle = (subject: string) => {
    const currentSubjects = watchedSubjects || []
    const newSubjects = currentSubjects.includes(subject)
      ? currentSubjects.filter(s => s !== subject)
      : [...currentSubjects, subject]
    
    setValue('aLevelSubjects', newSubjects)
  }

  const handleGradeChange = (subject: string, grade: string) => {
    const currentGrades = watchedGrades || {}
    setValue('predictedGrades', {
      ...currentGrades,
      [subject]: grade
    })
  }

  // Autosave function - saves current form data when navigating between steps
  const autosaveProfile = async () => {
    try {
      const formData = watch()
      // Only save if there's actual data
      if (formData.aLevelSubjects && formData.aLevelSubjects.length > 0) {
        await api.put('/student/profile', {
          aLevelSubjects: formData.aLevelSubjects,
          predictedGrades: formData.predictedGrades || {},
          preferences: formData.preferences || {
            preferredRegion: '',
            maxBudget: 9250,
            preferredUniSize: '',
            preferredCourseLength: '3 years',
            careerInterests: []
          }
        })

        updateUser({
          aLevelSubjects: formData.aLevelSubjects,
          predictedGrades: formData.predictedGrades || {},
          preferences: formData.preferences || {
            preferredRegion: '',
            maxBudget: 9250,
            preferredUniSize: '',
            preferredCourseLength: '3 years',
            careerInterests: []
          }
        })
      }
    } catch (error) {
      // Silently fail autosave - don't interrupt user flow
      console.error('Autosave failed:', error)
    }
  }

  // Handle step navigation with autosave
  const handleNextStep = async () => {
    await autosaveProfile()
    setStep(step + 1)
  }

  const handlePreviousStep = async () => {
    await autosaveProfile()
    setStep(step - 1)
  }

  // Always show the editable form, but add a note if profile is complete
  const showCompleteMessage = isComplete && step === 3

  return (
    <div className="card">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {isComplete ? 'Edit Your Profile' : 'Set Up Your Profile'} ({step}/3)
            </h2>
            <p className="mt-1 text-sm text-gray-600">
              {isComplete 
                ? 'Update your A-level subjects, predicted grades, and preferences.'
                : 'Help us understand your academic profile and preferences to provide better recommendations.'
              }
            </p>
          </div>
          {isComplete && (
            <div className="flex items-center text-success-600">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span className="text-sm font-medium">Profile Complete</span>
            </div>
          )}
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="card-body">
        {/* Step 1: A-level Subjects */}
        {step === 1 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                What A-level subjects are you taking?
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {A_LEVEL_SUBJECTS.map((subject) => (
                  <label
                    key={subject}
                    className={`relative flex items-center p-3 border rounded-lg cursor-pointer transition-colors ${
                      watchedSubjects?.includes(subject)
                        ? 'border-primary-500 bg-primary-50 text-primary-700'
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                  >
                    <input
                      type="checkbox"
                      className="sr-only"
                      checked={watchedSubjects?.includes(subject) || false}
                      onChange={() => handleSubjectToggle(subject)}
                    />
                    <span className="text-sm font-medium">{subject}</span>
                  </label>
                ))}
              </div>
              {errors.aLevelSubjects && (
                <p className="mt-2 text-sm text-red-600">Please select at least one subject</p>
              )}
            </div>
          </div>
        )}

        {/* Step 2: Predicted Grades */}
        {step === 2 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                What are your predicted grades?
              </h3>
              <div className="space-y-4">
                {watchedSubjects?.map((subject) => (
                  <div key={subject} className="flex items-center justify-between p-4 border rounded-lg">
                    <span className="font-medium">{subject}</span>
                    <select
                      value={watchedGrades?.[subject] || ''}
                      onChange={(e) => handleGradeChange(subject, e.target.value)}
                      className="input w-24"
                    >
                      <option value="">Select</option>
                      <option value="A*">A*</option>
                      <option value="A">A</option>
                      <option value="B">B</option>
                      <option value="C">C</option>
                      <option value="D">D</option>
                      <option value="E">E</option>
                      <option value="U">U</option>
                    </select>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Preferences */}
        {step === 3 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Tell us about your preferences
              </h3>
              
              <div className="space-y-6">
                {/* Preferred Region */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Preferred Region
                  </label>
                  <select {...register('preferences.preferredRegion')} className="input">
                    <option value="">Any region</option>
                    {REGIONS.map((region) => (
                      <option key={region} value={region}>{region}</option>
                    ))}
                  </select>
                </div>

                {/* Budget */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Maximum Budget (per year)
                  </label>
                  <input
                    type="number"
                    {...register('preferences.maxBudget', { valueAsNumber: true })}
                    className="input"
                    placeholder="9250"
                  />
                </div>

                {/* University Size */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Preferred University Size
                  </label>
                  <select {...register('preferences.preferredUniSize')} className="input">
                    <option value="">Any size</option>
                    {UNIVERSITY_SIZES.map((size) => (
                      <option key={size} value={size}>{size}</option>
                    ))}
                  </select>
                </div>

                {/* Course Length */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Preferred Course Length
                  </label>
                  <select {...register('preferences.preferredCourseLength')} className="input">
                    {COURSE_LENGTHS.map((length) => (
                      <option key={length} value={length}>{length}</option>
                    ))}
                  </select>
                </div>

                {/* Career Interests */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Career Interests (select all that apply)
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {CAREER_INTERESTS.map((interest) => (
                      <label key={interest} className="flex items-center">
                        <input
                          type="checkbox"
                          value={interest}
                          {...register('preferences.careerInterests')}
                          className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                        />
                        <span className="ml-2 text-sm text-gray-700">{interest}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="flex justify-between pt-6 border-t border-gray-200">
          {step > 1 ? (
            <button
              type="button"
              onClick={handlePreviousStep}
              className="btn-secondary"
            >
              Previous
            </button>
          ) : (
            <div></div>
          )}

          {step < 3 ? (
            <button
              type="button"
              onClick={handleNextStep}
              className="btn-primary"
            >
              Next
            </button>
          ) : (
            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={loading}
                className="btn-primary"
              >
                {loading ? 'Saving...' : isComplete ? 'Update Profile' : 'Complete Setup'}
              </button>
              {isComplete && (
                <button
                  type="button"
                  onClick={() => onComplete(user?.preferences || {})}
                  className="btn-secondary"
                >
                  Get Recommendations
                </button>
              )}
            </div>
          )}
        </div>
      </form>
    </div>
  )
}
