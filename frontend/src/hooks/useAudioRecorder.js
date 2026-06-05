import { useState, useRef, useCallback } from 'react'

export function useAudioRecorder() {
  const [isRecording, setIsRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState(null)
  const [duration, setDuration] = useState(0)
  const mediaRecorder = useRef(null)
  const chunks = useRef([])
  const timerRef = useRef(null)

  const startRecording = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder.current = new MediaRecorder(stream, { mimeType: 'audio/webm' })
    chunks.current = []
    setDuration(0)

    mediaRecorder.current.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.current.push(e.data)
    }

    mediaRecorder.current.onstop = () => {
      const blob = new Blob(chunks.current, { type: 'audio/webm' })
      setAudioBlob(blob)
      stream.getTracks().forEach(track => track.stop())
      clearInterval(timerRef.current)
    }

    mediaRecorder.current.start()
    setIsRecording(true)

    timerRef.current = setInterval(() => {
      setDuration(d => d + 1)
    }, 1000)
  }, [])

  const stopRecording = useCallback(() => {
    if (mediaRecorder.current?.state === 'recording') {
      mediaRecorder.current.stop()
      setIsRecording(false)
    }
  }, [])

  const resetRecording = useCallback(() => {
    setAudioBlob(null)
    setDuration(0)
  }, [])

  return { isRecording, audioBlob, duration, startRecording, stopRecording, resetRecording }
}
