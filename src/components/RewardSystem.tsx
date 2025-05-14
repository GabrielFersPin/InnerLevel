import React from 'react'

interface Reward {
  id: string
  name: string
  description: string
  points_required: number
  category: string
  redeemed: boolean
}

export function RewardSystem() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Reward System</h2>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Available Rewards */}
        <div className="card">
          <h3 className="text-xl font-semibold mb-4">Available Rewards</h3>
          <div className="space-y-3">
            <p className="text-gray-600">Complete tasks and habits to earn points and unlock rewards!</p>
          </div>
        </div>

        {/* Redeemed History */}
        <div className="card">
          <h3 className="text-xl font-semibold mb-4">Redeemed History</h3>
          <div className="space-y-3">
            <p className="text-gray-600">Track your redeemed rewards here</p>
          </div>
        </div>

        {/* Points Summary */}
        <div className="card">
          <h3 className="text-xl font-semibold mb-4">Points Summary</h3>
          <div className="space-y-2">
            <p className="text-gray-600">Current Points: 0</p>
            <p className="text-gray-600">Total Redeemed: 0</p>
          </div>
        </div>
      </div>
    </div>
  )
}