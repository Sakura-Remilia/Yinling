<template>
  <div class="login-page">
    <div class="login-card">
      <div class="card shadow">
        <div class="card-body p-5">
          <h3 class="text-center mb-4">
            <i class="bi bi-heart-pulse text-danger"></i> 银龄社区
          </h3>
          <p class="text-center text-muted mb-4">养老管理系统</p>

          <form @submit.prevent="handleLogin">
            <div class="mb-3">
              <label class="form-label">用户名</label>
              <input
                type="text"
                class="form-control"
                v-model="formData.username"
                placeholder="请输入用户名"
                required
              />
            </div>

            <div class="mb-3">
              <label class="form-label">密码</label>
              <input
                type="password"
                class="form-control"
                v-model="formData.password"
                placeholder="请输入密码"
                required
              />
            </div>

            <div class="mb-3 form-check">
              <input type="checkbox" class="form-check-input" id="remember" v-model="formData.remember" />
              <label class="form-check-label" for="remember">记住我</label>
            </div>

            <div v-if="errorMessage" class="alert alert-danger py-2">
              {{ errorMessage }}
            </div>

            <button type="submit" class="btn btn-primary w-100" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              登录
            </button>
          </form>

          <div class="text-center mt-3">
            <span class="text-muted">还没有账号？</span>
            <router-link to="/auth/register" class="text-decoration-none">立即注册</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formData = ref({
  username: '',
  password: '',
  remember: false
})

const loading = ref(false)
const errorMessage = ref('')

async function handleLogin() {
  loading.value = true
  errorMessage.value = ''

  const result = await authStore.login(formData.value)

  loading.value = false

  if (result.success) {
    const redirect = route.query.redirect || getDashboardRoute(authStore.userRole)
    router.push(redirect)
  } else {
    errorMessage.value = result.message || '登录失败'
  }
}

function getDashboardRoute(role) {
  const routes = {
    elderly: '/elderly/dashboard',
    volunteer: '/volunteer/dashboard',
    worker: '/worker/dashboard',
    community_admin: '/community-admin/dashboard',
    super_admin: '/super-admin/dashboard'
  }
  return routes[role] || '/'
}
</script>

<style scoped>
.login-page {
  width: 100%;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
}

.card {
  border: none;
  border-radius: 10px;
}
</style>