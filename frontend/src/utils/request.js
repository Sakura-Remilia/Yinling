import axios from 'axios'
import { ElMessage } from 'element-plus'
import { storage } from './storage'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = storage.getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data
    if (res.success === false) {
      ElMessage.error(res.message || '操作失败')
      return Promise.reject(new Error(res.message || '操作失败'))
    }
    return res
  },
  async error => {
    if (error.response?.status === 401) {
      const refreshToken = storage.getRefreshToken()
      if (refreshToken) {
        try {
          const res = await axios.post(import.meta.env.VITE_API_BASE_URL + '/auth/refresh', { refresh_token: refreshToken })
          storage.setToken(res.data.access_token)
          storage.setRefreshToken(res.data.refresh_token)
          error.config.headers.Authorization = `Bearer ${res.data.access_token}`
          return service(error.config)
        } catch (refreshError) {
          storage.removeTokens()
          window.location.href = '/auth/login'
        }
      } else {
        window.location.href = '/auth/login'
      }
    } else if (error.response?.status === 403) {
      ElMessage.error('无权访问')
    } else if (error.response?.status === 404) {
      ElMessage.error('资源不存在')
    } else if (error.response?.status >= 500) {
      ElMessage.error('服务器错误')
    }
    return Promise.reject(error)
  }
)

export default service