export default function PairChat({ messages, onSendText, currentUserId }) {
  return (
    <div className="border rounded-lg bg-white overflow-hidden">
      <div className="h-64 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <p className="text-center text-gray-400">暂无消息</p>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.sender_id === currentUserId ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-xs px-4 py-2 rounded-lg ${
              msg.type === 'system'
                ? 'bg-gray-100 text-gray-500 text-sm text-center w-full'
                : msg.sender_id === currentUserId
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-800'
            }`}>
              {msg.type === 'braille_challenge' && (
                <div>
                  <span className="text-xs opacity-75">盲文挑战:</span>
                  <p className="font-mono text-lg">{msg.braille_text}</p>
                  <p className="text-xs opacity-75">({msg.sentence})</p>
                </div>
              )}
              {msg.type === 'text' && <p>{msg.message}</p>}
              {msg.type === 'audio_result' && (
                <div>
                  <span className={msg.is_correct ? 'text-green-300' : 'text-red-300'}>
                    {msg.is_correct ? '正确' : '错误'}
                  </span>
                  <span className="text-xs ml-2">
                    识别: {msg.predicted_character} (置信度: {(msg.confidence * 100).toFixed(1)}%)
                  </span>
                  {msg.session_accuracy != null && (
                    <p className="text-xs mt-1 opacity-75">
                      本句准确率: {(msg.session_accuracy * 100).toFixed(0)}%
                    </p>
                  )}
                </div>
              )}
              {msg.type === 'system' && <p>{msg.message}</p>}
            </div>
          </div>
        ))}
      </div>
      <div className="border-t p-3">
        <form onSubmit={(e) => {
          e.preventDefault()
          const input = e.target.elements.message
          if (input.value.trim()) {
            onSendText(input.value.trim())
            input.value = ''
          }
        }} className="flex space-x-2">
          <input
            name="message"
            type="text"
            placeholder="输入消息..."
            className="flex-1 border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            发送
          </button>
        </form>
      </div>
    </div>
  )
}
