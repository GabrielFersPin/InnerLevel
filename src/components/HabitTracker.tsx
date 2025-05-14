import React from 'react'

interface Habit {
  name: string
  category: string
  points: number
}

export function HabitTracker() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Habit Tracker</h2>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Personal Habits Section */}
        <div className="card">
          <h3 className="text-xl font-semibold mb-4">Personal Habits</h3>
          <div className="space-y-3">
            {/* Habit items will go here */}
          </div>
        </div>

        {/* Professional Habits Section */}
        <div className="card">
          <h3 className="text-xl font-semibold mb-4">Professional Habits</h3>
          <div className="space-y-3">
            {/* Habit items will go here */}
          </div>
        </div>

        {/* Add New Habit Section */}
        <div className="card">
          <h3 className="text-xl font-semibold mb-4">Add New Habit</h3>
          <p className="text-gray-600">Track your daily habits and earn points!</p>
        </div>
      </div>
    </div>
  )
}