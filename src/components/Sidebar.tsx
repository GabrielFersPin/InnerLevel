import React from 'react'
import { 
  FiHome,
  FiSmile,
  FiCheckSquare,
  FiList,
  FiGift
} from 'react-icons/fi'

interface SidebarProps {
  activeTab: string
  setActiveTab: (tab: string) => void
}

export function Sidebar({ activeTab, setActiveTab }: SidebarProps) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: FiHome },
    { id: 'emotions', label: 'Emotional Log', icon: FiSmile },
    { id: 'habits', label: 'Habits', icon: FiCheckSquare },
    { id: 'tasks', label: 'Tasks', icon: FiList },
    { id: 'rewards', label: 'Rewards', icon: FiGift }
  ]

  return (
    <aside className="w-64 bg-secondary text-white p-6">
      <h1 className="text-2xl font-bold mb-8">InnerLevel</h1>
      
      <nav className="space-y-2">
        {menuItems.map(item => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`
              flex items-center gap-3 w-full px-4 py-2 rounded-lg transition-colors
              ${activeTab === item.id 
                ? 'bg-primary text-white' 
                : 'hover:bg-gray-700'
              }
            `}
          >
            <item.icon className="w-5 h-5" />
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </aside>
  )
}