import { useState, useEffect } from 'react'
import { getProficiencyStats, getProficiencyHistory } from '../api/auth'
import ProgressChart from '../components/ProgressChart'

export default function Proficiency() {
  const [stats, setStats] = useState(null)
  const [history, setHistory] = useState([])

  useEffect(() => {
    getProficiencyStats().then(res => setStats(res.data)).catch(() => {})
    getProficiencyHistory().then(res => setHistory(res.data)).catch(() => {})
  }, [])

  const getLevelColor = (level) => {
    if (level >= 8) return 'text-green-600'
    if (level >= 5) return 'text-blue-600'
    if (level >= 3) return 'text-yellow-600'
    return 'text-gray-600'
  }

  const getAccuracyColor = (accuracy) => {
    if (accuracy >= 80) return 'bg-green-500'
    if (accuracy >= 60) return 'bg-blue-500'
    if (accuracy >= 40) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">学习进度</h1>

      {stats && (
        <>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-lg text-gray-500">当前熟练度等级</h2>
                <p className={`text-5xl font-bold ${getLevelColor(stats.proficiency_level)}`}>
                  Lv.{stats.proficiency_level}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">加权准确率</p>
                <p className="text-3xl font-bold text-blue-600">{stats.accuracy_rate}%</p>
              </div>
            </div>

            <div className="w-full bg-gray-200 rounded-full h-4">
              <div
                className="bg-blue-600 h-4 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(stats.accuracy_rate, 100)}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-2">
              基于每个字符最近10次练习的加权得分计算
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg shadow p-6 text-center">
              <p className="text-3xl font-bold text-blue-600">{stats.total_sessions}</p>
              <p className="text-sm text-gray-500 mt-1">练习次数</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6 text-center">
              <p className="text-3xl font-bold text-green-600">{stats.correct_count}</p>
              <p className="text-sm text-gray-500 mt-1">正确识别</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6 text-center">
              <p className="text-3xl font-bold text-purple-600">{stats.total_recordings}</p>
              <p className="text-sm text-gray-500 mt-1">总录音数</p>
            </div>
          </div>

          {/* Per-character proficiency heatmap */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-2">字符熟练度</h2>
            <p className="text-sm text-gray-500 mb-4">
              基于最近10次尝试，错误会降低权重使得熟练度更贴合真实掌握程度
            </p>
            {stats.character_proficiency && stats.character_proficiency.length > 0 ? (
              <div className="grid grid-cols-7 md:grid-cols-13 gap-2">
                {stats.character_proficiency.map(cp => (
                  <div key={cp.character} className="relative group">
                    <div className={`flex flex-col items-center p-2 rounded-lg border-2 transition ${
                      cp.accuracy >= 80 ? 'border-green-300 bg-green-50' :
                      cp.accuracy >= 60 ? 'border-blue-300 bg-blue-50' :
                      cp.accuracy >= 40 ? 'border-yellow-300 bg-yellow-50' :
                      'border-red-300 bg-red-50'
                    }`}>
                      <span className="text-lg">{cp.unicode_repr}</span>
                      <span className="text-xs font-medium">{cp.character.toUpperCase()}</span>
                      <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                        <div
                          className={`h-1.5 rounded-full ${getAccuracyColor(cp.accuracy)}`}
                          style={{ width: `${cp.accuracy}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500">{cp.accuracy}%</span>
                    </div>
                    {/* Tooltip on hover */}
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-10">
                      <div className="bg-gray-800 text-white text-xs rounded py-2 px-3 whitespace-nowrap">
                        <p>字符: {cp.character.toUpperCase()}</p>
                        <p>加权得分: {cp.weighted_score}%</p>
                        <p>总尝试: {cp.total_attempts}次</p>
                        <p>最近记录: {JSON.parse(cp.recent_attempts).map(r => r ? '○' : '×').join('')}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-400 text-center py-8">开始练习后将显示各字符熟练度</p>
            )}
          </div>
        </>
      )}

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">准确率趋势</h2>
        <ProgressChart data={history} />
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">练习记录</h2>
        {history.length === 0 ? (
          <p className="text-gray-400 text-center py-4">暂无练习记录</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-3">日期</th>
                  <th className="text-left py-2 px-3">类型</th>
                  <th className="text-left py-2 px-3">准确率</th>
                </tr>
              </thead>
              <tbody>
                {history.slice().reverse().slice(0, 20).map(session => (
                  <tr key={session.id} className="border-b hover:bg-gray-50">
                    <td className="py-2 px-3">
                      {new Date(session.started_at).toLocaleString('zh-CN')}
                    </td>
                    <td className="py-2 px-3">
                      {session.session_type === 'solo' ? '独立练习' : '结对练习'}
                    </td>
                    <td className="py-2 px-3">
                      <span className={`font-medium ${
                        session.accuracy >= 0.7 ? 'text-green-600' : 'text-orange-600'
                      }`}>
                        {(session.accuracy * 100).toFixed(0)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
