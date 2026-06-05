import { useEffect, useRef, useState, useCallback } from 'react'
import { WS_BASE_URL } from '../utils/constants'

export function useWebSocket(sessionId) {
  const [messages, setMessages] = useState([])
  const [isConnected, setIsConnected] = useState(false)
  const ws = useRef(null)

  useEffect(() => {
    if (!sessionId) return

    const token = localStorage.getItem('access_token')
    if (!token) return

    const url = `${WS_BASE_URL}/pair/${sessionId}/?token=${token}`
    ws.current = new WebSocket(url)

    ws.current.onopen = () => setIsConnected(true)
    ws.current.onclose = () => setIsConnected(false)
    ws.current.onerror = () => setIsConnected(false)

    ws.current.onmessage = (e) => {
      const data = JSON.parse(e.data)
      setMessages(prev => [...prev, { ...data, timestamp: new Date().toISOString() }])
    }

    return () => {
      if (ws.current) {
        ws.current.close()
      }
    }
  }, [sessionId])

  const sendMessage = useCallback((data) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(data))
    }
  }, [])

  const clearMessages = useCallback(() => {
    setMessages([])
  }, [])

  return { messages, isConnected, sendMessage, clearMessages }
}
