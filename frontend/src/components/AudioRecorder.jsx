import { useAudioRecorder } from '../hooks/useAudioRecorder'

export default function AudioRecorder({ onRecorded, disabled = false }) {
  const { isRecording, audioBlob, duration, startRecording, stopRecording, resetRecording } =
    useAudioRecorder()

  const handleSubmit = () => {
    if (audioBlob && onRecorded) {
      onRecorded(audioBlob)
      resetRecording()
    }
  }

  return (
    <div className="flex flex-col items-center space-y-4 p-4 border rounded-lg bg-white">
      <div className="text-center">
        {isRecording && (
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
            <span className="text-red-600 font-medium">录音中 {duration}s</span>
          </div>
        )}
        {!isRecording && audioBlob && (
          <span className="text-green-600">录音完成 ({duration}s)</span>
        )}
        {!isRecording && !audioBlob && (
          <span className="text-gray-500">点击开始录音</span>
        )}
      </div>

      <div className="flex space-x-3">
        {!isRecording && !audioBlob && (
          <button
            onClick={startRecording}
            disabled={disabled}
            className="px-6 py-3 bg-red-500 text-white rounded-full hover:bg-red-600 disabled:opacity-50 transition"
          >
            开始录音
          </button>
        )}
        {isRecording && (
          <button
            onClick={stopRecording}
            className="px-6 py-3 bg-gray-700 text-white rounded-full hover:bg-gray-800 transition"
          >
            停止录音
          </button>
        )}
        {audioBlob && !isRecording && (
          <>
            <button
              onClick={handleSubmit}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              提交识别
            </button>
            <button
              onClick={resetRecording}
              className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
            >
              重新录音
            </button>
          </>
        )}
      </div>
    </div>
  )
}
