import { defineStore } from 'pinia'
import api from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    role: localStorage.getItem('role') || '',
    name: localStorage.getItem('name') || '',
    userId: localStorage.getItem('userId') || '',
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.role === 'admin',
    isStaff: (state) => ['recruiter', 'collector', 'admin'].includes(state.role),
  },
  actions: {
    setAuth(data) {
      this.token = data.access_token
      this.role = data.role
      this.name = data.name
      this.userId = data.user_id
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('role', data.role)
      localStorage.setItem('name', data.name)
      localStorage.setItem('userId', data.user_id)
    },
    async login(payload) {
      const data = await api.post('/auth/login', payload)
      this.setAuth(data)
      return data
    },
    async register(payload) {
      const data = await api.post('/auth/register', payload)
      this.setAuth(data)
      return data
    },
    logout() {
      this.token = ''
      this.role = ''
      this.name = ''
      this.userId = ''
      localStorage.clear()
    },
  },
})
