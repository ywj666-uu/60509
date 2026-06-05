import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  if (!user) return null

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link to="/" className="text-xl font-bold text-blue-600">
              ⠃⠗ 盲文学习平台
            </Link>
            <div className="hidden md:flex space-x-4">
              <Link to="/" className="text-gray-700 hover:text-blue-600 px-3 py-2">
                首页
              </Link>
              <Link to="/practice" className="text-gray-700 hover:text-blue-600 px-3 py-2">
                练习
              </Link>
              <Link to="/pair" className="text-gray-700 hover:text-blue-600 px-3 py-2">
                结对练习
              </Link>
              <Link to="/proficiency" className="text-gray-700 hover:text-blue-600 px-3 py-2">
                学习进度
              </Link>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">
              {user.username} (Lv.{user.proficiency_level})
            </span>
            <button
              onClick={handleLogout}
              className="text-sm text-red-600 hover:text-red-800"
            >
              退出
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
