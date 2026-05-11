import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'
import { storage } from '@/utils/storage'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(storage.getUser())
  const token = ref(storage.getToken())
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userRole = computed(() => user.value?.role)
  const isElderly = computed(() => userRole.value === 'elderly')
  const isVolunteer = computed(() => userRole.value === 'volunteer')
  const isWorker = computed(() => userRole.value === 'worker')
  const isCommunityAdmin = computed(() => userRole.value === 'community_admin')
  const isSuperAdmin = computed(() => userRole.value === 'super_admin')

  async function login(credentials) {
    loading.value = true
    try {
      const res = await authApi.login(credentials)
      token.value = res.data.access_token
      storage.setToken(res.data.access_token)
      storage.setRefreshToken(res.data.refresh_token)
      user.value = res.data.user
      storage.setUser(res.data.user)
      return { success: true }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  async function register(data) {
    loading.value = true
    try {
      const res = await authApi.register(data)
      token.value = res.data.access_token
      storage.setToken(res.data.access_token)
      storage.setRefreshToken(res.data.refresh_token)
      user.value = res.data.user
      storage.setUser(res.data.user)
      return { success: true }
    } catch (error) {
      return { success: false, message: error.message }
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch (e) {
      // 忽略错误
    } finally {
      token.value = null
      user.value = null
      storage.removeTokens()
    }
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const res = await authApi.getUser()
      user.value = res.data
      storage.setUser(res.data)
    } catch (error) {
      logout()
    }
  }

  async function updateProfile(data) {
    const res = await authApi.updateProfile(data)
    user.value = { ...user.value, ...res.data }
    storage.setUser(user.value)
    return res
  }

  async function changePassword(data) {
    return await authApi.changePassword(data)
  }

  return {
    user,
    token,
    loading,
    isAuthenticated,
    userRole,
    isElderly,
    isVolunteer,
    isWorker,
    isCommunityAdmin,
    isSuperAdmin,
    login,
    register,
    logout,
    fetchUser,
    updateProfile,
    changePassword
  }
})