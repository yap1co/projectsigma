'use client'

import { useState } from 'react'
import { useQuery } from 'react-query'
import api from '@/lib/api'

interface Project {
  _id: string
  title: string
  description: string
  status: string
  priority: string
  startDate: string
  endDate?: string
  tags: string[]
  createdBy: {
    _id: string
    username: string
    firstName: string
    lastName: string
  }
  teamMembers: Array<{
    user: {
      _id: string
      username: string
      firstName: string
      lastName: string
    }
    role: string
  }>
  tasks: Array<{
    _id: string
    title: string
    status: string
    priority: string
    assignedTo?: {
      _id: string
      username: string
    }
  }>
  createdAt: string
  updatedAt: string
}

interface ProjectCardProps {
  project: Project
}

export default function ProjectCard({ project }: ProjectCardProps) {
  const [showDetails, setShowDetails] = useState(false)

  const { data: projectDetails } = useQuery(
    ['project', project._id],
    async () => {
      const response = await api.get(`/projects/${project._id}`)
      return response.data.project
    },
    {
      enabled: showDetails
    }
  )

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'planning':
        return 'bg-blue-100 text-blue-800'
      case 'in-progress':
        return 'bg-yellow-100 text-yellow-800'
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'on-hold':
        return 'bg-gray-100 text-gray-800'
      case 'cancelled':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-100 text-red-800'
      case 'high':
        return 'bg-orange-100 text-orange-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'low':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const completedTasks = project.tasks.filter(task => task.status === 'completed').length
  const totalTasks = project.tasks.length
  const progressPercentage = totalTasks > 0 ? (completedTasks / totalTasks) * 100 : 0

  return (
    <div className="card hover:shadow-lg transition-shadow duration-200">
      <div className="card-body">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{project.title}</h3>
            <p className="text-gray-600 text-sm line-clamp-2">{project.description}</p>
          </div>
          <div className="flex space-x-2 ml-4">
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
              {project.status.replace('-', ' ')}
            </span>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(project.priority)}`}>
              {project.priority}
            </span>
          </div>
        </div>

        {/* Progress Bar */}
        {totalTasks > 0 && (
          <div className="mb-4">
            <div className="flex justify-between text-sm text-gray-600 mb-1">
              <span>Progress</span>
              <span>{completedTasks}/{totalTasks} tasks</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progressPercentage}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Tags */}
        {project.tags.length > 0 && (
          <div className="mb-4">
            <div className="flex flex-wrap gap-1">
              {project.tags.slice(0, 3).map((tag, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800"
                >
                  {tag}
                </span>
              ))}
              {project.tags.length > 3 && (
                <span className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800">
                  +{project.tags.length - 3} more
                </span>
              )}
            </div>
          </div>
        )}

        {/* Team Members */}
        <div className="mb-4">
          <div className="flex items-center">
            <div className="flex -space-x-2">
              {project.teamMembers.slice(0, 3).map((member, index) => (
                <div
                  key={index}
                  className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center border-2 border-white"
                >
                  <span className="text-xs font-medium text-primary-600">
                    {member.user.firstName.charAt(0)}{member.user.lastName.charAt(0)}
                  </span>
                </div>
              ))}
              {project.teamMembers.length > 3 && (
                <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center border-2 border-white">
                  <span className="text-xs font-medium text-gray-600">
                    +{project.teamMembers.length - 3}
                  </span>
                </div>
              )}
            </div>
            <span className="ml-2 text-sm text-gray-600">
              {project.teamMembers.length} member{project.teamMembers.length !== 1 ? 's' : ''}
            </span>
          </div>
        </div>

        {/* Dates */}
        <div className="flex justify-between items-center text-sm text-gray-500 mb-4">
          <div>
            <span className="font-medium">Start:</span> {new Date(project.startDate).toLocaleDateString()}
          </div>
          {project.endDate && (
            <div>
              <span className="font-medium">End:</span> {new Date(project.endDate).toLocaleDateString()}
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex justify-between items-center">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            {showDetails ? 'Hide Details' : 'View Details'}
          </button>
          <div className="flex space-x-2">
            <button className="text-gray-400 hover:text-gray-600">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button className="text-gray-400 hover:text-gray-600">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>

        {/* Expanded Details */}
        {showDetails && projectDetails && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="font-medium text-gray-900 mb-2">Tasks</h4>
            <div className="space-y-2">
              {projectDetails.tasks.slice(0, 5).map((task: any) => (
                <div key={task._id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={task.status === 'completed'}
                      readOnly
                      className="rounded"
                    />
                    <span className={`text-sm ${task.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                      {task.title}
                    </span>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded ${getPriorityColor(task.priority)}`}>
                    {task.priority}
                  </span>
                </div>
              ))}
              {projectDetails.tasks.length > 5 && (
                <div className="text-sm text-gray-500 text-center">
                  +{projectDetails.tasks.length - 5} more tasks
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
