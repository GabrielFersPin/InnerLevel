import React, { useState } from 'react'
import { EmotionalLog } from './components/EmotionalLog'
import { HabitTracker } from './components/HabitTracker'
import { RewardSystem } from './components/RewardSystem'
import { TaskManager } from './components/TaskManager'
import { Sidebar } from './components/Sidebar'
import { Analytics } from './components/Analytics'

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard')

  return (
    <div className="flex min-h-screen">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="flex-1 p-8">
        {activeTab === 'dashboard' && <Analytics />}
        {activeTab === 'emotions' && <EmotionalLog />}
        {activeTab === 'habits' && <HabitTracker />}
        {activeTab === 'tasks' && <TaskManager />}
        {activeTab === 'rewards' && <RewardSystem />}
      </main>
    </div>
  )
}