import client from './client'

export const login = (username, password) =>
  client.post('/auth/login/', { username, password })

export const register = (username, email, password, password_confirm) =>
  client.post('/auth/register/', { username, email, password, password_confirm })

export const getProfile = () => client.get('/auth/profile/')

export const updateProfile = (data) => client.put('/auth/profile/', data)

export const getProficiencyStats = () => client.get('/auth/proficiency/stats/')

export const getProficiencyHistory = () => client.get('/auth/proficiency/history/')
