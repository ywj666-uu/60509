import client from './client'

export const getAvailablePartners = () =>
  client.get('/pairing/available/')

export const getPairSessions = () =>
  client.get('/pairing/sessions/')

export const createPairSession = (partnerId, sentenceId) =>
  client.post('/pairing/sessions/', {
    partner_id: partnerId,
    sentence_id: sentenceId,
  })

export const getPairSession = (id) =>
  client.get(`/pairing/sessions/${id}/`)

export const endPairSession = (id) =>
  client.patch(`/pairing/sessions/${id}/`, { status: 'completed' })
