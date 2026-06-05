import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useWebSocket } from '../hooks/useWebSocket'
import { getAvailablePartners, createPairSession, getPairSession, endPairSession } from '../api/pairing'
import { getSentences } from '../api/braille'
import { uploadAudio } from '../api/audio'
import AudioRecorder from '../components/AudioRecorder'
import PairChat from '../components/PairChat'
import BrailleDisplay from '../components/BrailleDisplay'

export default function PairPractice() {
  const { sessionId } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [partners, setPartners] = useState([])
  const [sentences, setSentences] = useState([])
  const [activeSession, setActiveSession] = useState(null)
  const [selectedPartner, setSelectedPartner] = useState(null)
  const [selectedSentence, setSelectedSentence] = useState(null)
  const [challengeSentence, setChallengeSentence] = useState('')

  const { messages, isConnected, sendMessage } = useWebSocket(
    activeSession?.id || sessionId
  )

  useEffect(() => {
    if (sessionId) {
      getPairSession(sessionId).then(res => setActiveSession(res.data)).catch(() => {})
    } else {
      getAvailablePartners().then(res => setPartners(res.data)).catch(() => {})
      getSentences().then(res => setSentences(res.data.results || res.data)).catch(() => {})
    }
  }, [sessionId])

  const handleCreateSession = async () => {
    if (!selectedPartner) return
    const res = await createPairSession(selectedPartner.id, selectedSentence?.id)
    setActiveSession(res.data)
    navigate(`/pair/${res.data.id}`)
  }

  const handleEndSession = async () => {
    if (!activeSession) return
    await endPairSession(activeSession.id)
    setActiveSession(null)
    navigate('/pair')
  }

  const handleSendChallenge = () => {
    if (!challengeSentence.trim()) return
    sendMessage({
      type: 'braille_challenge',
      sentence: challengeSentence,
      braille_text: challengeSentence,
    })
    setChallengeSentence('')
  }

  const handleSendText = (text) => {
    sendMessage({ type: 'text', message: text })
  }

  const handleAudioRecorded = async (audioBlob) => {
    if (!activeSession?.practice_session) return
    const formData = new FormData()
    formData.append('audio_file', audioBlob, 'recording.webm')
    formData.append('session_id', activeSession.practice_session)
    await uploadAudio(formData)
  }

  if (!activeSession && !sessionId) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">结对练习</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">可用练习伙伴</h2>
            {partners.length === 0 ? (
              <p className="text-gray-400 text-center py-8">暂无可用伙伴</p>
            ) : (
              <div className="space-y-3">
                {partners.map(p => (
                  <button
                    key={p.id}
                    onClick={() => setSelectedPartner(p)}
                    className={`w-full text-left p-4 border rounded-lg hover:bg-blue-50 transition ${
                      selectedPartner?.id === p.id ? 'border-blue-500 bg-blue-50' : ''
                    }`}
                  >
                    <span className="font-medium">{p.username}</span>
                    <span className="ml-2 text-sm text-gray-500">Lv.{p.proficiency_level}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">选择句子（可选）</h2>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {sentences.map(s => (
                <button
                  key={s.id}
                  onClick={() => setSelectedSentence(s)}
                  className={`w-full text-left p-3 border rounded hover:bg-blue-50 ${
                    selectedSentence?.id === s.id ? 'border-blue-500 bg-blue-50' : ''
                  }`}
                >
                  <span>{s.text}</span>
                  <span className="text-xs text-gray-500 ml-2">难度 {s.difficulty_level}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        <button
          onClick={handleCreateSession}
          disabled={!selectedPartner}
          className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
        >
          开始结对练习
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">结对练习</h1>
        <div className="flex items-center space-x-4">
          <span className={`flex items-center space-x-1 ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-sm">{isConnected ? '已连接' : '未连接'}</span>
          </span>
          <button
            onClick={handleEndSession}
            className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
          >
            结束练习
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="font-semibold mb-3">发送盲文挑战</h3>
            <div className="flex space-x-2">
              <input
                type="text"
                value={challengeSentence}
                onChange={(e) => setChallengeSentence(e.target.value)}
                placeholder="输入英文单词/句子..."
                className="flex-1 border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                onClick={handleSendChallenge}
                disabled={!challengeSentence.trim()}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
              >
                发送
              </button>
            </div>
            {challengeSentence && (
              <div className="mt-3">
                <BrailleDisplay text={challengeSentence} />
              </div>
            )}
          </div>

          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="font-semibold mb-3">录音回答</h3>
            <AudioRecorder onRecorded={handleAudioRecorded} />
          </div>
        </div>

        <div>
          <PairChat
            messages={messages}
            onSendText={handleSendText}
            currentUserId={user?.id}
          />
        </div>
      </div>
    </div>
  )
}
