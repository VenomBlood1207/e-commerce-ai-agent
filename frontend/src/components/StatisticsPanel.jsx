import { useState, useEffect } from 'react'
import { X, Database, TrendingUp, Users, Package, Star, MapPin, DollarSign, Clock } from 'lucide-react'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import axios from 'axios'

const StatisticsPanel = ({ isOpen, onClose }) => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (isOpen) {
      loadStatistics()
    }
  }, [isOpen])

  const loadStatistics = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Load basic stats
      const statsResponse = await axios.get('/api/stats')
      setStats(statsResponse.data)
    } catch (err) {
      setError(err.message)
      console.error('Error loading statistics:', err)
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  // Colors for charts
  const COLORS = ['#0ea5e9', '#d946ef', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899']

  // Prepare data for visualizations
  const tableData = stats?.tables ? Object.entries(stats.tables).map(([name, count]) => ({
    name: name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    count: count,
    shortName: name.split('_').map(w => w[0].toUpperCase()).join('')
  })) : []

  // Mock data for user perspective stats (you can replace with real API calls)
  const orderStatusData = [
    { name: 'Delivered', value: 85, color: '#22c55e' },
    { name: 'Shipped', value: 10, color: '#0ea5e9' },
    { name: 'Processing', value: 3, color: '#f59e0b' },
    { name: 'Cancelled', value: 2, color: '#ef4444' },
  ]

  const monthlyTrends = [
    { month: 'Jan', orders: 4000, revenue: 24000 },
    { month: 'Feb', orders: 3000, revenue: 18000 },
    { month: 'Mar', orders: 5000, revenue: 32000 },
    { month: 'Apr', orders: 4500, revenue: 28000 },
    { month: 'May', orders: 6000, revenue: 38000 },
    { month: 'Jun', orders: 5500, revenue: 35000 },
  ]

  const topCategories = [
    { category: 'Electronics', sales: 12500 },
    { category: 'Fashion', sales: 9800 },
    { category: 'Home & Garden', sales: 8200 },
    { category: 'Sports', sales: 6500 },
    { category: 'Books', sales: 5200 },
  ]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-fade-in">
      <div className="bg-white rounded-3xl shadow-2xl w-full max-w-7xl max-h-[90vh] overflow-hidden animate-slide-up">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-500 to-accent-500 px-8 py-6 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-white/20 backdrop-blur-md rounded-2xl flex items-center justify-center">
              <TrendingUp className="w-7 h-7 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Analytics Dashboard</h2>
              <p className="text-primary-100 text-sm">E-commerce Performance Overview</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/20 rounded-xl transition-colors"
          >
            <X className="w-6 h-6 text-white" />
          </button>
        </div>

        {/* Content */}
        <div className="p-8 overflow-y-auto max-h-[calc(90vh-100px)]">
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="flex flex-col items-center space-y-4">
                <div className="flex space-x-2">
                  <div className="w-3 h-3 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-3 h-3 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-3 h-3 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
                <p className="text-neutral-600 font-medium">Loading statistics...</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center py-20">
              <div className="text-center">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <X className="w-8 h-8 text-red-600" />
                </div>
                <p className="text-red-600 font-medium">Error loading statistics</p>
                <p className="text-neutral-500 text-sm mt-2">{error}</p>
                <button
                  onClick={loadStatistics}
                  className="mt-4 px-6 py-2 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-colors"
                >
                  Retry
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-8">
              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <MetricCard
                  icon={<Package className="w-6 h-6" />}
                  title="Total Orders"
                  value={stats?.tables?.orders?.toLocaleString() || '0'}
                  color="from-primary-500 to-primary-600"
                  trend="+12.5%"
                />
                <MetricCard
                  icon={<Users className="w-6 h-6" />}
                  title="Customers"
                  value={stats?.tables?.customers?.toLocaleString() || '0'}
                  color="from-accent-500 to-accent-600"
                  trend="+8.2%"
                />
                <MetricCard
                  icon={<Star className="w-6 h-6" />}
                  title="Reviews"
                  value={stats?.tables?.order_reviews?.toLocaleString() || '0'}
                  color="from-success-500 to-success-600"
                  trend="+15.3%"
                />
                <MetricCard
                  icon={<Database className="w-6 h-6" />}
                  title="Products"
                  value={stats?.tables?.products?.toLocaleString() || '0'}
                  color="from-orange-500 to-orange-600"
                  trend="+5.7%"
                />
              </div>

              {/* Charts Row 1 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Database Tables Overview */}
                <ChartCard title="Database Overview" icon={<Database className="w-5 h-5" />}>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={tableData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                      <XAxis dataKey="shortName" stroke="#737373" fontSize={12} />
                      <YAxis stroke="#737373" fontSize={12} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'white',
                          border: '1px solid #e5e5e5',
                          borderRadius: '12px',
                          padding: '12px'
                        }}
                      />
                      <Bar dataKey="count" fill="#0ea5e9" radius={[8, 8, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>

                {/* Order Status Distribution */}
                <ChartCard title="Order Status Distribution" icon={<TrendingUp className="w-5 h-5" />}>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={orderStatusData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={100}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {orderStatusData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </ChartCard>
              </div>

              {/* Charts Row 2 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Monthly Trends */}
                <ChartCard title="Monthly Performance" icon={<Clock className="w-5 h-5" />}>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={monthlyTrends}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                      <XAxis dataKey="month" stroke="#737373" fontSize={12} />
                      <YAxis stroke="#737373" fontSize={12} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'white',
                          border: '1px solid #e5e5e5',
                          borderRadius: '12px',
                          padding: '12px'
                        }}
                      />
                      <Legend />
                      <Line type="monotone" dataKey="orders" stroke="#0ea5e9" strokeWidth={3} dot={{ r: 5 }} />
                      <Line type="monotone" dataKey="revenue" stroke="#d946ef" strokeWidth={3} dot={{ r: 5 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </ChartCard>

                {/* Top Categories */}
                <ChartCard title="Top Product Categories" icon={<Package className="w-5 h-5" />}>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={topCategories} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e5e5" />
                      <XAxis type="number" stroke="#737373" fontSize={12} />
                      <YAxis dataKey="category" type="category" stroke="#737373" fontSize={12} width={120} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'white',
                          border: '1px solid #e5e5e5',
                          borderRadius: '12px',
                          padding: '12px'
                        }}
                      />
                      <Bar dataKey="sales" fill="#22c55e" radius={[0, 8, 8, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>
              </div>

              {/* Additional Stats Table */}
              <div className="bg-gradient-to-br from-neutral-50 to-neutral-100 rounded-2xl p-6 border border-neutral-200">
                <h3 className="text-lg font-bold text-neutral-800 mb-4 flex items-center">
                  <div className="w-8 h-8 bg-primary-100 rounded-xl flex items-center justify-center mr-3">
                    <Database className="w-5 h-5 text-primary-600" />
                  </div>
                  Database Tables
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {tableData.map((table, idx) => (
                    <div
                      key={idx}
                      className="bg-white rounded-xl p-4 hover:shadow-soft transition-shadow"
                    >
                      <p className="text-xs text-neutral-600 font-medium mb-1">{table.name}</p>
                      <p className="text-2xl font-bold text-primary-600">{table.count.toLocaleString()}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// Metric Card Component
const MetricCard = ({ icon, title, value, color, trend }) => (
  <div className="bg-white rounded-2xl p-6 border border-neutral-200 shadow-soft hover:shadow-glow transition-all duration-200 group">
    <div className="flex items-start justify-between mb-4">
      <div className={`w-12 h-12 bg-gradient-to-br ${color} rounded-xl flex items-center justify-center text-white shadow-soft group-hover:scale-110 transition-transform`}>
        {icon}
      </div>
      {trend && (
        <span className="text-xs font-semibold text-success-600 bg-success-50 px-2 py-1 rounded-lg">
          {trend}
        </span>
      )}
    </div>
    <p className="text-sm text-neutral-600 font-medium mb-1">{title}</p>
    <p className="text-3xl font-bold text-neutral-900">{value}</p>
  </div>
)

// Chart Card Component
const ChartCard = ({ title, icon, children }) => (
  <div className="bg-white rounded-2xl p-6 border border-neutral-200 shadow-soft">
    <div className="flex items-center space-x-2 mb-6">
      <div className="w-8 h-8 bg-gradient-to-br from-primary-100 to-accent-100 rounded-xl flex items-center justify-center text-primary-600">
        {icon}
      </div>
      <h3 className="text-lg font-bold text-neutral-800">{title}</h3>
    </div>
    {children}
  </div>
)

export default StatisticsPanel
