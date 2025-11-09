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
      <div className="bg-white/80 backdrop-blur-md border-b border-neutral-200/50 px-8 py-6 shadow-soft">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center shadow-glow">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-accent-600 bg-clip-text text-transparent">E-commerce Intelligence Agent</h1>
              <p className="text-sm text-neutral-600">Powered by AI • Ask me anything about your data</p>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-8 py-6 space-y-6">
        <div className="max-w-5xl mx-auto">
        {messages.length === 0 && (
          <div className="text-center py-16 animate-fade-in">
            <div className="mb-8">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-primary-100 to-accent-100 rounded-3xl mb-4 shadow-soft">
                <span className="text-5xl">👋</span>
              </div>
              <h2 className="text-3xl font-bold text-neutral-800 mb-2">Welcome!</h2>
              <p className="text-neutral-600 text-lg">I'm your AI-powered e-commerce analytics assistant</p>
            </div>
            <p className="text-neutral-700 font-medium mb-6">Try asking:</p>
            <div className="grid gap-3 max-w-2xl mx-auto">
              {exampleQueries.map((query, idx) => (
                <button
                  key={idx}
                  onClick={() => setInput(query)}
                  className="group text-left px-6 py-4 bg-white/80 backdrop-blur-sm border border-neutral-200 rounded-2xl hover:border-primary-400 hover:shadow-soft hover:scale-[1.02] transition-all duration-200 animate-slide-up"
                  style={{ animationDelay: `${idx * 100}ms` }}
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center group-hover:bg-primary-200 transition-colors">
                      <svg className="w-4 h-4 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                    </div>
                    <span className="text-sm text-neutral-700 group-hover:text-primary-700 transition-colors">{query}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message, idx) => (
          <MessageBubble key={idx} message={message} />
        ))}

        {isLoading && (
          <div className="flex items-center space-x-3 text-neutral-600 animate-slide-up">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
            <span className="text-sm font-medium">AI is thinking...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="bg-white/80 backdrop-blur-md border-t border-neutral-200/50 px-8 py-6 shadow-soft">
        <div className="max-w-5xl mx-auto">
          <form onSubmit={handleSubmit} className="flex space-x-4">
            <div className="flex-1 relative">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask me anything about your e-commerce data..."
                disabled={isLoading}
                className="w-full px-6 py-4 pr-12 bg-white border-2 border-neutral-200 rounded-2xl focus:outline-none focus:border-primary-400 focus:ring-4 focus:ring-primary-100 disabled:bg-neutral-100 disabled:text-neutral-400 transition-all duration-200 text-neutral-800 placeholder-neutral-400 shadow-inner-soft"
              />
              <div className="absolute right-4 top-1/2 -translate-y-1/2 text-neutral-400">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
            </div>
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="px-8 py-4 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white rounded-2xl disabled:from-neutral-300 disabled:to-neutral-300 disabled:cursor-not-allowed transition-all duration-200 flex items-center space-x-2 shadow-soft hover:shadow-glow font-medium"
            >
              <Send className="w-5 h-5" />
              <span>Send</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface
