<template>
  <div class="dashboard-layout">
    <Navbar :user="authStore.user" @logout="handleLogout" />
    <div class="container-fluid">
      <div class="row">
        <Sidebar :role="authStore.userRole" />
        <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 main-content">
          <h1 class="my-4">老人仪表盘</h1>
          <p class="text-muted">欢迎使用银龄社区养老管理系统</p>
          <div class="row mt-4">
            <div class="col-md-4 mb-3">
              <div class="card">
                <div class="card-body">
                  <h5 class="card-title">待处理订单</h5>
                  <p class="card-text display-4">0</p>
                </div>
              </div>
            </div>
            <div class="col-md-4 mb-3">
              <div class="card">
                <div class="card-body">
                  <h5 class="card-title">进行中服务</h5>
                  <p class="card-text display-4">0</p>
                </div>
              </div>
            </div>
            <div class="col-md-4 mb-3">
              <div class="card">
                <div class="card-body">
                  <h5 class="card-title">已报名活动</h5>
                  <p class="card-text display-4">0</p>
                </div>
              </div>
            </div>
          </div>
          <div class="mt-4">
            <h3>快捷操作</h3>
            <div class="row mt-3">
              <div class="col-md-3 mb-2">
                <router-link to="/elderly/sos" class="btn btn-danger w-100">
                  <i class="bi bi-exclamation-triangle me-2"></i>SOS紧急求助
                </router-link>
              </div>
              <div class="col-md-3 mb-2">
                <router-link to="/elderly/services" class="btn btn-primary w-100">
                  <i class="bi bi-basket me-2"></i>预约服务
                </router-link>
              </div>
              <div class="col-md-3 mb-2">
                <router-link to="/elderly/health" class="btn btn-success w-100">
                  <i class="bi bi-heart-pulse me-2"></i>健康记录
                </router-link>
              </div>
              <div class="col-md-3 mb-2">
                <router-link to="/elderly/activities" class="btn btn-info w-100">
                  <i class="bi bi-calendar-event me-2"></i>活动报名
                </router-link>
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

<style scoped>
.main-content {
  padding-top: 20px;
}
</style>