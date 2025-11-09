import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts'

const COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#84cc16'
]

const ChartDisplay = ({ type, data }) => {
  if (!data || !data.data || data.data.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No data available for visualization
      </div>
    )
  }

  const chartData = data.data

  switch (type) {
    case 'bar':
      return (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={data.x_axis} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey={data.y_axis} fill={COLORS[0]} />
          </BarChart>
        </ResponsiveContainer>
      )

    case 'line':
      return (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={data.x_axis} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey={data.y_axis} 
              stroke={COLORS[0]} 
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      )

    case 'pie':
      return (
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              dataKey={data.value}
              nameKey={data.label}
              cx="50%"
              cy="50%"
              outerRadius={100}
              label
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      )

    case 'scatter':
      return (
        <ResponsiveContainer width="100%" height={300}>
          <ScatterChart>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={data.x_axis} />
            <YAxis dataKey={data.y_axis} />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
            <Legend />
            <Scatter 
              name="Data Points" 
              data={chartData} 
              fill={COLORS[0]} 
            />
          </ScatterChart>
        </ResponsiveContainer>
      )

    default:
      return (
        <div className="text-center py-8 text-gray-500">
          Chart type not supported: {type}
        </div>
      )
  }
}

export default ChartDisplay
