<template>
  <div class="dashboard-layout">
    <Navbar :user="authStore.user" @logout="handleLogout" />
    <div class="container-fluid">
      <div class="row">
        <Sidebar role="volunteer" />
        <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 main-content">
          <h1 class="my-4">志愿者仪表盘</h1>
          <p class="text-muted">欢迎 {{ authStore.user?.real_name || authStore.user?.username }}</p>
          <div class="row mt-4">
            <div class="col-md-4 mb-3">
              <div class="card border-primary">
                <div class="card-body">
                  <h5 class="card-title text-primary">待接任务</h5>
                  <p class="card-text display-4">0</p>
                </div>
              </div>
            </div>
            <div class="col-md-4 mb-3">
              <div class="card border-success">
                <div class="card-body">
                  <h5 class="card-title text-success">服务时长</h5>
                  <p class="card-text display-4">0<span class="h5">小时</span></p>
                </div>
              </div>
            </div>
            <div class="col-md-4 mb-3">
              <div class="card border-warning">
                <div class="card-body">
                  <h5 class="card-title text-warning">我的积分</h5>
                  <p class="card-text display-4">0</p>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import Navbar from '@/components/common/Navbar.vue'
import Sidebar from '@/components/common/Sidebar.vue'

const authStore = useAuthStore()
const router = useRouter()

async function handleLogout() {
  await authStore.logout()
  router.push('/auth/login')
}
</script>