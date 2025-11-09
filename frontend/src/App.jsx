import { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import Sidebar from './components/Sidebar'

function App() {
  const [sessionId, setSessionId] = useState('default')
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar 
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        sessionId={sessionId}
        onSessionChange={setSessionId}
      />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <ChatInterface sessionId={sessionId} />
      </div>
    </div>
  )
}

export default App
