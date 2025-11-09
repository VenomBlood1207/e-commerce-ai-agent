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
        className="fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-lg hover:bg-gray-50"
      >
        {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
      </button>

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-40 w-64 bg-white border-r border-gray-200 
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="flex flex-col h-full pt-16 px-4">
          {/* Logo/Title */}
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-800">
              E-commerce AI
            </h2>
            <p className="text-sm text-gray-600">Intelligence Agent</p>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-2">
            <button
              onClick={() => onSessionChange('default')}
              className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <MessageSquare className="w-5 h-5 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">Chat</span>
            </button>

            <button
              onClick={loadStats}
              className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <BarChart3 className="w-5 h-5 text-gray-600" />
              <span className="text-sm font-medium text-gray-700">Statistics</span>
            </button>

            <button
              onClick={clearConversation}
              className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg hover:bg-red-50 transition-colors text-red-600"
            >
              <Trash2 className="w-5 h-5" />
              <span className="text-sm font-medium">Clear History</span>
            </button>
          </nav>

          {/* Stats Display */}
          {showStats && stats && (
            <div className="mb-4 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                <Database className="w-4 h-4 mr-2" />
                Database Stats
              </h3>
              <div className="space-y-2 text-xs">
                {Object.entries(stats.tables || {}).map(([table, count]) => (
                  <div key={table} className="flex justify-between">
                    <span className="text-gray-600">{table}</span>
                    <span className="font-medium text-gray-900">
                      {count.toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Footer */}
          <div className="py-4 border-t border-gray-200">
            <div className="flex items-center space-x-2 text-xs text-gray-500">
              <Info className="w-4 h-4" />
              <span>Powered by Groq AI</span>
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
