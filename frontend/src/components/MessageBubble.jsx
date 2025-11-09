import { User, Bot, Database, TrendingUp } from 'lucide-react'
import ChartDisplay from './ChartDisplay'
import DataTable from './DataTable'

const MessageBubble = ({ message }) => {
  const isUser = message.role === 'user'
  const metadata = message.metadata || {}

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex space-x-3 max-w-3xl ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-primary-600' : 'bg-gray-700'
        }`}>
          {isUser ? (
            <User className="w-5 h-5 text-white" />
          ) : (
            <Bot className="w-5 h-5 text-white" />
          )}
        </div>

        {/* Content */}
        <div className={`flex-1 ${isUser ? 'items-end' : 'items-start'}`}>
          <div className={`px-4 py-3 rounded-lg ${
            isUser 
              ? 'bg-primary-600 text-white' 
              : 'bg-white border border-gray-200 text-gray-800'
          }`}>
            <p className="whitespace-pre-wrap">{message.content}</p>
          </div>

          {/* Metadata for assistant messages */}
          {!isUser && metadata.query_type === 'data_query' && (
            <div className="mt-3 space-y-3">
              {/* SQL Query */}
              {metadata.sql_query && (
                <div className="bg-gray-900 text-gray-100 px-4 py-3 rounded-lg text-sm font-mono overflow-x-auto">
                  <div className="flex items-center space-x-2 mb-2">
                    <Database className="w-4 h-4" />
                    <span className="text-xs uppercase text-gray-400">SQL Query</span>
                  </div>
                  <pre className="text-xs">{metadata.sql_query}</pre>
                </div>
              )}

              {/* Data Table */}
              {metadata.result_data && metadata.result_data.data && (
                <DataTable data={metadata.result_data} />
              )}

              {/* Chart */}
              {metadata.chart_type && metadata.chart_data && (
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-4">
                    <TrendingUp className="w-4 h-4 text-primary-600" />
                    <span className="text-sm font-medium text-gray-700">Visualization</span>
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
            <div className="mt-2 px-4 py-2 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              Error: {metadata.error}
            </div>
          )}

          {/* Timestamp */}
          <div className={`mt-1 text-xs text-gray-500 ${isUser ? 'text-right' : 'text-left'}`}>
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    </div>
  )
}

export default MessageBubble
