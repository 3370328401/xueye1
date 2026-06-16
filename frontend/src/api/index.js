import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail || error.message || '请求失败'
    if (status === 401) {
      localStorage.clear()
      ElMessage.error('登录已失效，请重新登录')
      router.push('/login')
    } else {
      ElMessage.error(typeof detail === 'string' ? detail : '请求失败')
    }
    return Promise.reject(error)
  },
)

export default api
