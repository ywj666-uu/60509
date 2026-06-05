import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { getProficiencyStats } from '../api/auth'
import { getCharacters, getSessions } from '../api/braille'
import BrailleDisplay from '../components/BrailleDisplay'

export default function Dashboard() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [characters, setCharacters] = useState([])
  const [recentSessions, setRecentSessions] = useState([])

  useEffect(() => {
    getProficiencyStats().then(res => setStats(res.data)).catch(() => {})
    getCharacters().then(res => setCharacters(res.data)).catch(() => {})
    getSessions().then(res => setRecentSessions(res.data.results || res.data)).catch(() => {})
  }, [])

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">欢迎回来，{user?.username}</h1>
        <span className="text-lg text-blue-600 font-medium">
          熟练度等级: Lv.{user?.proficiency_level}
        </span>
      </div>

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <StatCard title="总练习次数" value={stats.total_sessions} />
          <StatCard title="总录音数" value={stats.total_recordings} />
          <StatCard title="正确次数" value={stats.correct_count} />
          <StatCard title="准确率" value={`${stats.accuracy_rate}%`} />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">盲文字母表</h2>
          <div className="grid grid-cols-6 gap-2">
            {characters.slice(0, 26).map(char => (
              <div key={char.id} className="text-center p-2 border rounded hover:bg-blue-50">
                <span className="text-2xl">{char.unicode_repr}</span>
                <p className="text-xs text-gray-500 mt-1">{char.character.toUpperCase()}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">最近练习</h2>
            <Link to="/practice" className="text-blue-600 hover:underline text-sm">
              开始练习 &rarr;
            </Link>
          </div>
          {recentSessions.length === 0 ? (
            <p className="text-gray-400 text-center py-8">还没有练习记录</p>
          ) : (
            <div className="space-y-3">
              {recentSessions.slice(0, 5).map(session => (
                <div key={session.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                  <div>
                    <span className="text-sm font-medium">
                      {session.session_type === 'solo' ? '独立练习' : '结对练习'}
                    </span>
                    <p className="text-xs text-gray-500">
                      {new Date(session.started_at).toLocaleString('zh-CN')}
                    </p>
                  </div>
                  <span className={`text-sm font-medium ${
                    session.accuracy !== null
                      ? session.accuracy >= 0.7 ? 'text-green-600' : 'text-orange-600'
                      : 'text-gray-400'
                  }`}>
                    {session.accuracy !== null ? `${(session.accuracy * 100).toFixed(0)}%` : '进行中'}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">示例盲文</h2>
        <BrailleDisplay text="hello" />
      </div>
    </div>
  )
}

function StatCard({ title, value }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <p className="text-sm text-gray-500">{title}</p>
      <p className="text-2xl font-bold text-blue-600 mt-1">{value}</p>
    </div>
  )
}
