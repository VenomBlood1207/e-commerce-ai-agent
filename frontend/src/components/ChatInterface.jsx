import { useState, useEffect, useRef } from 'react'
import { Send, Loader2 } from 'lucide-react'
import MessageBubble from './MessageBubble'
import axios from 'axios'

const ChatInterface = ({ sessionId }) => {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  useEffect(() => {
    // Load conversation history when session changes
    loadHistory()
  }, [sessionId])

  const loadHistory = async () => {
    try {
      const response = await axios.get(`/api/conversation/${sessionId}`)
      const history = response.data.messages || []
      
      const formattedMessages = history.map(msg => ({
        role: msg.role,
        content: msg.content,
        metadata: msg.metadata,
        timestamp: msg.timestamp
      }))
      
      setMessages(formattedMessages)
    } catch (error) {
      console.error('Error loading history:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!input.trim() || isLoading) return

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await axios.post('/api/query', {
        query: input,
        session_id: sessionId
      })

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        metadata: {
          query_type: response.data.query_type,
          sql_query: response.data.sql_query,
          result_data: response.data.result_data,
          chart_type: response.data.chart_type,
          chart_data: response.data.chart_data,
          error: response.data.error
        },
        timestamp: response.data.timestamp
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${error.response?.data?.detail || error.message}`,
        metadata: { error: true },
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const exampleQueries = [
    "What are the top 5 product categories by sales?",
    "Show me average delivery time by state",
    "Which sellers have the highest ratings?",
    "Translate 'cama_mesa_banho' to English"
  ]

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-800">E-commerce Intelligence Agent</h1>
        <p className="text-sm text-gray-600">Ask me anything about the e-commerce data</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center py-12">
            <h2 className="text-xl font-semibold text-gray-700 mb-4">Welcome! 👋</h2>
            <p className="text-gray-600 mb-6">Try asking:</p>
            <div className="grid gap-2 max-w-2xl mx-auto">
              {exampleQueries.map((query, idx) => (
                <button
                  key={idx}
                  onClick={() => setInput(query)}
                  className="text-left px-4 py-3 bg-white border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
                >
                  <span className="text-sm text-gray-700">{query}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message, idx) => (
          <MessageBubble key={idx} message={message} />
        ))}

        {isLoading && (
          <div className="flex items-center space-x-2 text-gray-500">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Thinking...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <form onSubmit={handleSubmit} className="flex space-x-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            disabled={isLoading}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-100"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            <Send className="w-5 h-5" />
            <span>Send</span>
          </button>
        </form>
      </div>
    </div>
  )
}

export default ChatInterface
