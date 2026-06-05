import { useState, useEffect } from 'react'
import { getCharacters, getSentences, createSession, endSession } from '../api/braille'
import { uploadAudio, getRecordings } from '../api/audio'
import BrailleDisplay from '../components/BrailleDisplay'
import AudioRecorder from '../components/AudioRecorder'

export default function Practice() {
  const [characters, setCharacters] = useState([])
  const [sentences, setSentences] = useState([])
  const [selectedChar, setSelectedChar] = useState(null)
  const [currentSession, setCurrentSession] = useState(null)
  const [recordings, setRecordings] = useState([])
  const [mode, setMode] = useState('character') // 'character' or 'sentence'
  const [selectedSentence, setSelectedSentence] = useState(null)

  useEffect(() => {
    getCharacters().then(res => setCharacters(res.data)).catch(() => {})
    getSentences().then(res => setSentences(res.data.results || res.data)).catch(() => {})
  }, [])

  const startSession = async () => {
    const data = { session_type: 'solo' }
    if (mode === 'sentence' && selectedSentence) {
      data.sentence = selectedSentence.id
    }
    const res = await createSession(data)
    setCurrentSession(res.data)
    setRecordings([])
  }

  const handleEndSession = async () => {
    if (!currentSession) return
    await endSession(currentSession.id)
    setCurrentSession(null)
    setSelectedChar(null)
  }

  const handleAudioRecorded = async (audioBlob) => {
    if (!currentSession) return

    const formData = new FormData()
    formData.append('audio_file', audioBlob, 'recording.webm')
    formData.append('session_id', currentSession.id)
    if (selectedChar) {
      formData.append('target_character_id', selectedChar.id)
    }

    const res = await uploadAudio(formData)
    setRecordings(prev => [res.data, ...prev])

    // Poll for result
    setTimeout(async () => {
      const updated = await getRecordings(currentSession.id)
      setRecordings(updated.data)
    }, 3000)
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">盲文练习</h1>

      <div className="flex space-x-4">
        <button
          onClick={() => setMode('character')}
          className={`px-4 py-2 rounded-lg ${mode === 'character' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
        >
          单字符练习
        </button>
        <button
          onClick={() => setMode('sentence')}
          className={`px-4 py-2 rounded-lg ${mode === 'sentence' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
        >
          句子练习
        </button>
      </div>

      {!currentSession ? (
        <div className="bg-white rounded-lg shadow p-6">
          {mode === 'character' && (
            <>
              <h2 className="text-lg font-semibold mb-4">选择要练习的字符</h2>
              <div className="grid grid-cols-7 md:grid-cols-13 gap-2 mb-6">
                {characters.map(char => (
                  <button
                    key={char.id}
                    onClick={() => setSelectedChar(char)}
                    className={`p-3 border rounded-lg text-center hover:bg-blue-50 transition ${
                      selectedChar?.id === char.id ? 'border-blue-500 bg-blue-50' : ''
                    }`}
                  >
                    <span className="text-xl">{char.unicode_repr}</span>
                    <p className="text-xs mt-1">{char.character.toUpperCase()}</p>
                  </button>
                ))}
              </div>
            </>
          )}

          {mode === 'sentence' && (
            <>
              <h2 className="text-lg font-semibold mb-4">选择练习句子</h2>
              <div className="space-y-3 mb-6">
                {sentences.map(s => (
                  <button
                    key={s.id}
                    onClick={() => setSelectedSentence(s)}
                    className={`w-full text-left p-4 border rounded-lg hover:bg-blue-50 transition ${
                      selectedSentence?.id === s.id ? 'border-blue-500 bg-blue-50' : ''
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <span className="font-medium">{s.text}</span>
                      <span className="text-xs text-gray-500">难度 {s.difficulty_level}</span>
                    </div>
                    <p className="text-lg font-mono mt-1">{s.braille_text}</p>
                  </button>
                ))}
              </div>
            </>
          )}

          <button
            onClick={startSession}
            disabled={mode === 'character' && !selectedChar}
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            开始练习
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">当前练习</h2>
              <button
                onClick={handleEndSession}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
              >
                结束练习
              </button>
            </div>

            {selectedChar && (
              <div className="mb-6">
                <p className="text-sm text-gray-500 mb-2">目标字符:</p>
                <BrailleDisplay text={selectedChar.character} />
              </div>
            )}

            {selectedSentence && (
              <div className="mb-6">
                <p className="text-sm text-gray-500 mb-2">目标句子:</p>
                <BrailleDisplay text={selectedSentence.text} />
              </div>
            )}

            <AudioRecorder onRecorded={handleAudioRecorded} />
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold mb-4">识别结果</h3>
            {recordings.length === 0 ? (
              <p className="text-gray-400 text-center">录音后将显示识别结果</p>
            ) : (
              <div className="space-y-3">
                {recordings.map(rec => (
                  <div key={rec.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <div className="flex items-center space-x-3">
                      <span className={`w-3 h-3 rounded-full ${
                        rec.processing_status === 'completed'
                          ? rec.is_correct ? 'bg-green-500' : 'bg-red-500'
                          : rec.processing_status === 'processing' ? 'bg-yellow-500 animate-pulse' : 'bg-gray-300'
                      }`} />
                      <div>
                        <span className="text-sm font-medium">
                          {rec.processing_status === 'completed'
                            ? `识别: ${rec.predicted_character?.toUpperCase()}`
                            : rec.processing_status === 'processing' ? '处理中...' : '等待中...'
                          }
                        </span>
                        {rec.confidence && (
                          <span className="text-xs text-gray-500 ml-2">
                            置信度: {(rec.confidence * 100).toFixed(1)}%
                          </span>
                        )}
                      </div>
                    </div>
                    {rec.processing_status === 'completed' && (
                      <span className={`text-sm font-bold ${rec.is_correct ? 'text-green-600' : 'text-red-600'}`}>
                        {rec.is_correct ? '正确' : '错误'}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
