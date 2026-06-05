import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function ProgressChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg">
        <p className="text-gray-400">暂无练习数据</p>
      </div>
    )
  }

  const chartData = data.map((item, idx) => ({
    name: `#${idx + 1}`,
    accuracy: Math.round((item.accuracy || 0) * 100),
    date: new Date(item.started_at).toLocaleDateString('zh-CN'),
  }))

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis domain={[0, 100]} unit="%" />
          <Tooltip
            formatter={(value) => [`${value}%`, '准确率']}
            labelFormatter={(label) => {
              const item = chartData.find(d => d.name === label)
              return item ? item.date : label
            }}
          />
          <Line
            type="monotone"
            dataKey="accuracy"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={{ fill: '#3b82f6' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
