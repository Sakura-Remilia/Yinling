<template>
  <div class="dashboard-layout">
    <Navbar :user="authStore.user" @logout="handleLogout" />
    <div class="container-fluid">
      <div class="row">
        <Sidebar role="community_admin" />
        <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 main-content">
          <h1 class="my-4">社区管理员仪表盘</h1>
          <p class="text-muted">欢迎 {{ authStore.user?.real_name || authStore.user?.username }}</p>
          <div class="row mt-4">
            <div class="col-md-3 mb-3">
              <div class="card border-primary">
                <div class="card-body">
                  <h5 class="card-title text-primary">老人数量</h5>
                  <p class="card-text display-4">0</p>
                </div>
              </div>
            </div>
            <div class="col-md-3 mb-3">
              <div class="card border-danger">
                <div class="card-body">
                  <h5 class="card-title text-danger">SOS待处理</h5>
                  <p class="card-text display-4">0</p>
                </div>
              </div>
            </div>
            <div class="col-md-3 mb-3">
              <div class="card border-success">
                <div class="card-body">
                  <h5 class="card-title text-success">今日订单</h5>
                  <p class="card-text display-4">0</p>
                </div>
              </div>
            </div>
            <div class="col-md-3 mb-3">
              <div class="card border-warning">
                <div class="card-body">
                  <h5 class="card-title text-warning">独居老人</h5>
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