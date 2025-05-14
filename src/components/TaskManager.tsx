import React from 'react'

interface Task {
  ID: string
  Task: string
  'Due Date': string
  Priority: 'High' | 'Medium' | 'Low'
  Status: 'Pending' | 'Completed'
  Points: number
}

export function TaskManager() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Task Manager</h2>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Active Tasks */}
        <div className="card">
          <h3 className="text-xl font-semibold mb-4">Active Tasks</h3>
          <div className="space-y-3">
            <p className="text-gray-600">Your pending tasks will appear here</p>
          </div>
        </div>

        {/* Completed Tasks */}
        <div className="card">
          <h3 className="text-xl font-semibold mb-4">Completed Tasks</h3>
          <div className="space-y-3">
            <p className="text-gray-600">Track your completed tasks here</p>
          </div>
        </div>

        {/* Add New Task */}
        <div className="card">
          <h3 className="text-xl font-semibold mb-4">Add New Task</h3>
          <p className="text-gray-600">Create new tasks and assign points!</p>
        </div>
      </div>
    </div>
  )
}