import client from './client'

export const getCharacters = (grade) =>
  client.get('/braille/characters/', { params: { grade } })

export const getSentences = (difficulty) =>
  client.get('/braille/sentences/', { params: { difficulty } })

export const createSession = (data) =>
  client.post('/braille/sessions/', data)

export const endSession = (sessionId) =>
  client.post(`/braille/sessions/${sessionId}/end/`)

export const getSessions = () =>
  client.get('/braille/sessions/')
