<template>
  <div class="profile-page">
    <div class="container py-4">
      <h2 class="mb-4">个人设置</h2>
      <div class="card">
        <div class="card-body">
          <div class="text-center mb-4">
            <img src="@/assets/images/default_avatar.svg" alt="头像" class="rounded-circle" width="100" height="100" />
          </div>

          <form @submit.prevent="handleSubmit">
            <div class="mb-3">
              <label class="form-label">用户名</label>
              <input type="text" class="form-control" :value="user?.username" disabled />
            </div>

            <div class="mb-3">
              <label class="form-label">真实姓名</label>
              <input type="text" class="form-control" v-model="formData.real_name" />
            </div>

            <div class="mb-3">
              <label class="form-label">手机号</label>
              <input type="tel" class="form-control" v-model="formData.phone" />
            </div>

            <div class="mb-3">
              <label class="form-label">邮箱</label>
              <input type="email" class="form-control" v-model="formData.email" />
            </div>

            <button type="submit" class="btn btn-primary" :disabled="loading">保存修改</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const user = authStore.user
const loading = ref(false)

const formData = ref({
  real_name: user?.real_name || '',
  phone: user?.phone || '',
  email: user?.email || ''
})

async function handleSubmit() {
  loading.value = true
  try {
    await authStore.updateProfile(formData.value)
    ElMessage.success('资料更新成功')
  } catch (e) {
    ElMessage.error('更新失败')
  }
  loading.value = false
}
</script>