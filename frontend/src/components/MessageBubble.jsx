import { useState } from 'react'
import { User, Bot, Database, TrendingUp, ChevronDown, ChevronRight } from 'lucide-react'
import ChartDisplay from './ChartDisplay'
import DataTable from './DataTable'

const MessageBubble = ({ message }) => {
  const isUser = message.role === 'user'
  const metadata = message.metadata || {}
  const [showSqlQuery, setShowSqlQuery] = useState(false)

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-slide-up`}>
      <div className={`flex space-x-3 max-w-4xl ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-10 h-10 rounded-2xl flex items-center justify-center shadow-soft ${
          isUser 
            ? 'bg-gradient-to-br from-primary-500 to-primary-600' 
            : 'bg-gradient-to-br from-neutral-700 to-neutral-800'
        }`}>
          {isUser ? (
            <User className="w-5 h-5 text-white" />
          ) : (
            <Bot className="w-5 h-5 text-white" />
          )}
        </div>

        {/* Content */}
        <div className={`flex-1 ${isUser ? 'items-end' : 'items-start'}`}>
          <div className={`px-5 py-4 rounded-2xl shadow-soft ${
            isUser 
              ? 'bg-gradient-to-br from-primary-500 to-primary-600 text-white' 
              : 'bg-white/90 backdrop-blur-sm border border-neutral-200 text-neutral-800'
          }`}>
            <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
          </div>

          {/* Metadata for assistant messages */}
          {!isUser && metadata.query_type === 'data_query' && (
            <div className="mt-3 space-y-3">
              {/* SQL Query - Collapsible */}
              {metadata.sql_query && (
                <div className="bg-gradient-to-br from-neutral-900 to-neutral-800 text-neutral-100 rounded-2xl shadow-soft border border-neutral-700 overflow-hidden">
                  {/* Dropdown Header */}
                  <button
                    onClick={() => setShowSqlQuery(!showSqlQuery)}
                    className="w-full px-5 py-4 flex items-center justify-between hover:bg-neutral-800/50 transition-colors"
                  >
                    <div className="flex items-center space-x-2">
                      <div className="w-6 h-6 bg-primary-500/20 rounded-lg flex items-center justify-center">
                        <Database className="w-4 h-4 text-primary-400" />
                      </div>
                      <span className="text-xs uppercase text-neutral-400 font-semibold tracking-wider">SQL Query</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-neutral-500">
                        {showSqlQuery ? 'Hide' : 'Show'}
                      </span>
                      {showSqlQuery ? (
                        <ChevronDown className="w-4 h-4 text-neutral-400" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-neutral-400" />
                      )}
                    </div>
                  </button>
                  
                  {/* Collapsible Content */}
                  {showSqlQuery && (
                    <div className="px-5 pb-4 border-t border-neutral-700/50 pt-3 animate-slide-up">
                      <pre className="text-xs leading-relaxed text-neutral-300 overflow-x-auto">{metadata.sql_query}</pre>
                    </div>
                  )}
                </div>
              )}

              {/* Data Table */}
              {metadata.result_data && metadata.result_data.data && (
                <DataTable data={metadata.result_data} />
              )}

              {/* Chart */}
              {metadata.chart_type && metadata.chart_data && (
                <div className="bg-white/90 backdrop-blur-sm border border-neutral-200 rounded-2xl p-6 shadow-soft">
                  <div className="flex items-center space-x-2 mb-5">
                    <div className="w-8 h-8 bg-gradient-to-br from-primary-100 to-accent-100 rounded-xl flex items-center justify-center">
                      <TrendingUp className="w-4 h-4 text-primary-600" />
                    </div>
                    <span className="text-sm font-semibold text-neutral-800">Visualization</span>
                  </div>
                  <ChartDisplay 
                    type={metadata.chart_type}
                    data={metadata.chart_data}
                  />
                </div>
              )}
            </div>
          )}

          {/* Error display */}
          {metadata.error && (
            <div className="mt-3 px-5 py-3 bg-red-50 border border-red-200 rounded-2xl text-sm text-red-700 shadow-soft">
              <div className="flex items-center space-x-2">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span className="font-medium">Error: {metadata.error}</span>
              </div>
            </div>
          )}

          {/* Timestamp */}
          <div className={`mt-2 text-xs text-neutral-500 font-medium ${isUser ? 'text-right' : 'text-left'}`}>
            {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </div>
    </div>
  )
}

export default MessageBubble
