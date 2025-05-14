import React from 'react'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

export function Analytics() {
  const chartData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Points Earned',
        data: [10, 25, 15, 30, 20, 35, 25],
        borderColor: '#3498db',
        backgroundColor: 'rgba(52, 152, 219, 0.1)',
        tension: 0.4
      }
    ]
  }

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const
      },
      title: {
        display: true,
        text: 'Weekly Progress'
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Analytics Dashboard</h2>
      
      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-600">Total Points</h3>
          <p className="text-3xl font-bold text-primary mt-2">160</p>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-600">Tasks Completed</h3>
          <p className="text-3xl font-bold text-success mt-2">12</p>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-600">Active Habits</h3>
          <p className="text-3xl font-bold text-warning mt-2">7</p>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-600">Rewards Claimed</h3>
          <p className="text-3xl font-bold text-danger mt-2">3</p>
        </div>
      </div>

      {/* Progress Chart */}
      <div className="card">
        <h3 className="text-xl font-semibold mb-4">Progress Overview</h3>
        <div className="h-[300px]">
          <Line data={chartData} options={chartOptions} />
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h3 className="text-xl font-semibold mb-4">Recent Activity</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between py-2 border-b">
            <span className="text-gray-600">Completed Daily Coding</span>
            <span className="text-primary font-semibold">+10 pts</span>
          </div>
          <div className="flex items-center justify-between py-2 border-b">
            <span className="text-gray-600">Posted on LinkedIn</span>
            <span className="text-primary font-semibold">+15 pts</span>
          </div>
          <div className="flex items-center justify-between py-2">
            <span className="text-gray-600">Submitted Job Application</span>
            <span className="text-primary font-semibold">+15 pts</span>
          </div>
        </div>
      </div>
    </div>
  )
}