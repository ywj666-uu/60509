import client from './client'

export const uploadAudio = (formData) =>
  client.post('/audio/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

export const getRecordings = (sessionId) =>
  client.get('/audio/recordings/', { params: { session_id: sessionId } })

export const getRecording = (id) =>
  client.get(`/audio/recordings/${id}/`)
