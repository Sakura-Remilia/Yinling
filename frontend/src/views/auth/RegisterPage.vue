<template>
  <div class="register-page">
    <div class="register-card">
      <div class="card shadow">
        <div class="card-body p-5">
          <h3 class="text-center mb-4">
            <i class="bi bi-heart-pulse text-danger"></i> 银龄社区
          </h3>
          <p class="text-center text-muted mb-4">用户注册</p>

          <form @submit.prevent="handleRegister">
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
              <label class="form-label">真实姓名</label>
              <input
                type="text"
                class="form-control"
                v-model="formData.real_name"
                placeholder="请输入真实姓名"
                required
              />
            </div>

            <div class="mb-3">
              <label class="form-label">手机号</label>
              <input
                type="tel"
                class="form-control"
                v-model="formData.phone"
                placeholder="请输入手机号"
                required
              />
            </div>

            <div class="mb-3">
              <label class="form-label">密码</label>
              <input
                type="password"
                class="form-control"
                v-model="formData.password"
                placeholder="请输入密码（至少6位）"
                required
                minlength="6"
              />
            </div>

            <div class="mb-3">
              <label class="form-label">确认密码</label>
              <input
                type="password"
                class="form-control"
                v-model="formData.confirm_password"
                placeholder="请再次输入密码"
                required
              />
            </div>

            <div class="mb-3">
              <label class="form-label">用户类型</label>
              <select class="form-select" v-model="formData.role">
                <option value="elderly">老人</option>
                <option value="volunteer">志愿者</option>
              </select>
            </div>

            <div v-if="errorMessage" class="alert alert-danger py-2">
              {{ errorMessage }}
            </div>

            <button type="submit" class="btn btn-primary w-100" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              注册
            </button>
          </form>

          <div class="text-center mt-3">
            <span class="text-muted">已有账号？</span>
            <router-link to="/auth/login" class="text-decoration-none">立即登录</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  username: '',
  real_name: '',
  phone: '',
  password: '',
  confirm_password: '',
  role: 'elderly'
})

const loading = ref(false)
const errorMessage = ref('')

async function handleRegister() {
  if (formData.value.password !== formData.value.confirm_password) {
    errorMessage.value = '两次密码输入不一致'
    return
  }

  loading.value = true
  errorMessage.value = ''

  const result = await authStore.register(formData.value)

  loading.value = false

  if (result.success) {
    router.push('/auth/login')
  } else {
    errorMessage.value = result.message || '注册失败'
  }
}
</script>

<style scoped>
.register-page {
  width: 100%;
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 400px;
}

.card {
  border: none;
  border-radius: 10px;
}
</style>