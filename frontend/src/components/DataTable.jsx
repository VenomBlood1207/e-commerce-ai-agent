import { Table } from 'lucide-react'

const DataTable = ({ data }) => {
  if (!data || !data.data || data.data.length === 0) {
    return null
  }

  const { columns, data: rows, row_count, truncated } = data

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <div className="px-4 py-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Table className="w-4 h-4 text-gray-600" />
          <span className="text-sm font-medium text-gray-700">Results</span>
          <span className="text-xs text-gray-500">
            ({row_count} {row_count === 1 ? 'row' : 'rows'})
          </span>
        </div>
        {truncated && (
          <span className="text-xs text-amber-600">
            Showing first {rows.length} rows
          </span>
        )}
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              {columns.map((col, idx) => (
                <th
                  key={idx}
                  className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider"
                >
                  {col.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {rows.map((row, rowIdx) => (
              <tr key={rowIdx} className="hover:bg-gray-50">
                {columns.map((col, colIdx) => (
                  <td key={colIdx} className="px-4 py-3 text-gray-900">
                    {formatCellValue(row[col.name])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

const formatCellValue = (value) => {
  if (value === null || value === undefined) {
    return <span className="text-gray-400">null</span>
  }
  
  if (typeof value === 'number') {
    return value.toLocaleString()
  }
  
  if (typeof value === 'boolean') {
    return value ? 'true' : 'false'
  }
  
  return String(value)
}

export default DataTable
