import { useState } from 'react'
import { 
  Menu, X, MessageSquare, Trash2, Settings, 
  BarChart3, Database, Info 
} from 'lucide-react'
import axios from 'axios'

const Sidebar = ({ isOpen, onToggle, sessionId, onSessionChange }) => {
  const [stats, setStats] = useState(null)
  const [showStats, setShowStats] = useState(false)

  const loadStats = async () => {
    try {
      const response = await axios.get('/api/stats')
      setStats(response.data)
      setShowStats(true)
    } catch (error) {
      console.error('Error loading stats:', error)
    }
  }

  const clearConversation = async () => {
    if (window.confirm('Clear conversation history?')) {
      try {
        await axios.delete(`/api/conversation/${sessionId}`)
        window.location.reload()
      } catch (error) {
        console.error('Error clearing conversation:', error)
      }
    }
  }

  return (
    <>
      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className="fixed top-6 left-6 z-50 p-3 bg-white/90 backdrop-blur-md rounded-2xl shadow-soft hover:shadow-glow hover:scale-105 transition-all duration-200 border border-neutral-200"
      >
        {isOpen ? <X className="w-6 h-6 text-neutral-700" /> : <Menu className="w-6 h-6 text-neutral-700" />}
      </button>

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-40 w-72 bg-white/95 backdrop-blur-xl border-r border-neutral-200/50 shadow-2xl
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex flex-col h-full pt-20 px-6">
          {/* Logo/Title */}
          <div className="mb-10">
            <div className="flex items-center space-x-3 mb-2">
              <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-accent-500 rounded-2xl flex items-center justify-center shadow-glow">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-bold bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent">
                  E-commerce AI
                </h2>
                <p className="text-xs text-neutral-600 font-medium">Intelligence Agent</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-3">
            <button
              onClick={() => onSessionChange('default')}
              className="w-full flex items-center space-x-3 px-5 py-4 rounded-2xl bg-gradient-to-r from-primary-50 to-accent-50 hover:from-primary-100 hover:to-accent-100 transition-all duration-200 shadow-soft hover:shadow-glow group"
            >
              <div className="w-9 h-9 bg-white rounded-xl flex items-center justify-center shadow-soft group-hover:scale-110 transition-transform">
                <MessageSquare className="w-5 h-5 text-primary-600" />
              </div>
              <span className="text-sm font-semibold text-neutral-800">Chat</span>
            </button>

            <button
              onClick={loadStats}
              className="w-full flex items-center space-x-3 px-5 py-4 rounded-2xl hover:bg-neutral-100 transition-all duration-200 group"
            >
              <div className="w-9 h-9 bg-neutral-100 rounded-xl flex items-center justify-center group-hover:bg-white group-hover:shadow-soft transition-all">
                <BarChart3 className="w-5 h-5 text-neutral-600" />
              </div>
              <span className="text-sm font-semibold text-neutral-700">Statistics</span>
            </button>

            <button
              onClick={clearConversation}
              className="w-full flex items-center space-x-3 px-5 py-4 rounded-2xl hover:bg-red-50 transition-all duration-200 group"
            >
              <div className="w-9 h-9 bg-red-50 rounded-xl flex items-center justify-center group-hover:bg-red-100 transition-all">
                <Trash2 className="w-5 h-5 text-red-600" />
              </div>
              <span className="text-sm font-semibold text-red-600">Clear History</span>
            </button>
          </nav>

          {/* Stats Display */}
          {showStats && stats && (
            <div className="mb-6 p-5 bg-gradient-to-br from-neutral-50 to-neutral-100 rounded-2xl border border-neutral-200 shadow-soft animate-slide-in">
              <h3 className="text-sm font-bold text-neutral-800 mb-4 flex items-center">
                <div className="w-7 h-7 bg-primary-100 rounded-lg flex items-center justify-center mr-2">
                  <Database className="w-4 h-4 text-primary-600" />
                </div>
                Database Stats
              </h3>
              <div className="space-y-3 text-xs">
                {Object.entries(stats.tables || {}).map(([table, count]) => (
                  <div key={table} className="flex justify-between items-center py-2 px-3 bg-white rounded-xl hover:shadow-soft transition-shadow">
                    <span className="text-neutral-600 font-medium capitalize">{table.replace('_', ' ')}</span>
                    <span className="font-bold text-primary-600 bg-primary-50 px-3 py-1 rounded-lg">
                      {count.toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Footer */}
          <div className="py-6 border-t border-neutral-200">
            <div className="flex items-center justify-center space-x-2 text-xs text-neutral-500 font-medium">
              <div className="w-6 h-6 bg-neutral-100 rounded-lg flex items-center justify-center">
                <Info className="w-3 h-3 text-neutral-600" />
              </div>
              <span>Powered by <span className="text-primary-600 font-semibold">Groq AI</span></span>
            </div>
          </div>
        </div>
      </div>

      {/* Overlay */}
      {isOpen && (
        <div
          onClick={onToggle}
          className="fixed inset-0 bg-black bg-opacity-50 z-30"
        />
      )}
    </>
  )
}

export default Sidebar
