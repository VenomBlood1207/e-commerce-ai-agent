import { useState, useEffect } from 'react'
import { X, Database, Table, Columns, Hash } from 'lucide-react'
import axios from 'axios'

const TablesPanel = ({ isOpen, onClose }) => {
  const [tables, setTables] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (isOpen) {
      loadTables()
    }
  }, [isOpen])

  const loadTables = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await axios.get(`${API_BASE_URL}/stats`)
      setTables(response.data.tables)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  // Table schema information (column names)
  const tableSchemas = {
    orders: ['order_id', 'customer_id', 'order_status', 'order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date'],
    customers: ['customer_id', 'customer_unique_id', 'customer_zip_code_prefix', 'customer_city', 'customer_state'],
    order_items: ['order_id', 'order_item_id', 'product_id', 'seller_id', 'shipping_limit_date', 'price', 'freight_value'],
    order_payments: ['order_id', 'payment_sequential', 'payment_type', 'payment_installments', 'payment_value'],
    order_reviews: ['review_id', 'order_id', 'review_score', 'review_comment_title', 'review_comment_message', 'review_creation_date', 'review_answer_timestamp'],
    products: ['product_id', 'product_category_name', 'product_name_length', 'product_description_length', 'product_photos_qty', 'product_weight_g', 'product_length_cm', 'product_height_cm', 'product_width_cm'],
    sellers: ['seller_id', 'seller_zip_code_prefix', 'seller_city', 'seller_state'],
    product_category_name_translation: ['product_category_name', 'product_category_name_english'],
    geolocation: ['geolocation_zip_code_prefix', 'geolocation_lat', 'geolocation_lng', 'geolocation_city', 'geolocation_state']
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-3xl shadow-2xl w-full max-w-6xl max-h-[90vh] overflow-hidden animate-slide-up">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-600 to-accent-600 px-8 py-6 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-white/20 rounded-2xl flex items-center justify-center backdrop-blur-sm">
              <Database className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Database Tables</h2>
              <p className="text-sm text-white/80">Schema and row counts</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-10 h-10 bg-white/20 hover:bg-white/30 rounded-xl flex items-center justify-center transition-colors backdrop-blur-sm"
          >
            <X className="w-5 h-5 text-white" />
          </button>
        </div>

        {/* Content */}
        <div className="p-8 overflow-y-auto max-h-[calc(90vh-100px)]">
          {loading && (
            <div className="flex items-center justify-center py-20">
              <div className="flex space-x-2">
                <div className="w-3 h-3 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-3 h-3 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-3 h-3 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-2xl p-6 text-center">
              <p className="text-red-700 font-medium">Error loading tables: {error}</p>
              <button
                onClick={loadTables}
                className="mt-4 px-6 py-2 bg-red-600 text-white rounded-xl hover:bg-red-700 transition-colors"
              >
                Retry
              </button>
            </div>
          )}

          {!loading && !error && tables && (
            <div className="space-y-4">
              {Object.entries(tables).map(([tableName, rowCount]) => {
                const columns = tableSchemas[tableName] || []
                
                return (
                  <div
                    key={tableName}
                    className="bg-gradient-to-br from-white to-neutral-50 border border-neutral-200 rounded-2xl p-6 hover:shadow-soft transition-all duration-200"
                  >
                    {/* Table Header */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-primary-100 to-accent-100 rounded-xl flex items-center justify-center">
                          <Table className="w-5 h-5 text-primary-600" />
                        </div>
                        <div>
                          <h3 className="text-lg font-bold text-neutral-800">{tableName}</h3>
                          <div className="flex items-center space-x-2 text-xs text-neutral-600">
                            <Hash className="w-3 h-3" />
                            <span className="font-semibold">{rowCount.toLocaleString()} rows</span>
                            <span className="text-neutral-400">•</span>
                            <Columns className="w-3 h-3" />
                            <span>{columns.length} columns</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Columns */}
                    {columns.length > 0 && (
                      <div className="mt-4">
                        <div className="flex items-center space-x-2 mb-3">
                          <Columns className="w-4 h-4 text-neutral-500" />
                          <span className="text-xs font-semibold text-neutral-600 uppercase tracking-wider">Columns</span>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                          {columns.map((column, idx) => (
                            <div
                              key={idx}
                              className="px-3 py-2 bg-white border border-neutral-200 rounded-lg text-xs font-mono text-neutral-700 hover:border-primary-300 hover:bg-primary-50 transition-colors"
                            >
                              {column}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default TablesPanel
