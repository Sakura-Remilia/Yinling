<template>
  <div class="dashboard-layout">
    <Navbar :user="authStore.user" @logout="handleLogout" />
    <div class="container-fluid">
      <div class="row">
        <Sidebar role="super_admin" />
        <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 main-content">
          <h1 class="my-4">系统概览</h1>
          <p class="text-muted">欢迎 {{ authStore.user?.real_name || authStore.user?.username }}</p>

          <!-- 统计卡片 -->
          <div class="row mt-4">
            <div class="col-md-2 mb-3">
              <div class="card border-primary">
                <div class="card-body text-center">
                  <h5 class="card-title text-primary">总用户数</h5>
                  <p class="card-text display-5">{{ stats.total_users || 0 }}</p>
                </div>
              </div>
            </div>
            <div class="col-md-2 mb-3">
              <div class="card border-info">
                <div class="card-body text-center">
                  <h5 class="card-title text-info">社区数量</h5>
                  <p class="card-text display-5">{{ stats.total_communities || 0 }}</p>
                </div>
              </div>
            </div>
            <div class="col-md-2 mb-3">
              <div class="card border-success">
                <div class="card-body text-center">
                  <h5 class="card-title text-success">老人数量</h5>
                  <p class="card-text display-5">{{ stats.elderly_count || 0 }}</p>
                </div>
              </div>
            </div>
            <div class="col-md-2 mb-3">
              <div class="card border-warning">
                <div class="card-body text-center">
                  <h5 class="card-title text-warning">志愿者数量</h5>
                  <p class="card-text display-5">{{ stats.volunteer_count || 0 }}</p>
                </div>
              </div>
            </div>
            <div class="col-md-2 mb-3">
              <div class="card border-secondary">
                <div class="card-body text-center">
                  <h5 class="card-title">工作人员</h5>
                  <p class="card-text display-5">{{ stats.worker_count || 0 }}</p>
                </div>
              </div>
            </div>
            <div class="col-md-2 mb-3">
              <div class="card border-danger">
                <div class="card-body text-center">
                  <h5 class="card-title text-danger">活跃用户</h5>
                  <p class="card-text display-5">{{ stats.active_users || 0 }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- 图表区域 -->
          <div class="row mt-4">
            <!-- 饼状图：用户角色分布 -->
            <div class="col-lg-6 mb-4">
              <div class="card">
                <div class="card-header bg-white">
                  <h5 class="mb-0"><i class="bi bi-pie-chart me-2"></i>用户角色分布</h5>
                </div>
                <div class="card-body">
                  <div ref="pieChartRef" class="chart-container"></div>
                </div>
              </div>
            </div>

            <!-- 柱状图：各社区用户数量 -->
            <div class="col-lg-6 mb-4">
              <div class="card">
                <div class="card-header bg-white">
                  <h5 class="mb-0"><i class="bi bi-bar-chart me-2"></i>各社区用户数量</h5>
                </div>
                <div class="card-body">
                  <div ref="barChartRef" class="chart-container"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- 折线图：用户增长趋势 -->
          <div class="row mt-4">
            <div class="col-lg-12 mb-4">
              <div class="card">
                <div class="card-header bg-white">
                  <h5 class="mb-0"><i class="bi bi-graph-up me-2"></i>用户增长趋势</h5>
                </div>
                <div class="card-body">
                  <div ref="lineChartRef" class="chart-container-line"></div>
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
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import Navbar from '@/components/common/Navbar.vue'
import Sidebar from '@/components/common/Sidebar.vue'
import { superAdminApi } from '@/api'

const authStore = useAuthStore()
const router = useRouter()

const stats = ref({
  total_users: 0,
  total_communities: 0,
  elderly_count: 0,
  volunteer_count: 0,
  worker_count: 0,
  active_users: 0
})

// 图表实例
let pieChart = null
let barChart = null
let lineChart = null

const pieChartRef = ref(null)
const barChartRef = ref(null)
const lineChartRef = ref(null)

onMounted(async () => {
  // 初始化图表
  pieChart = echarts.init(pieChartRef.value)
  barChart = echarts.init(barChartRef.value)
  lineChart = echarts.init(lineChartRef.value)

  // 获取统计数据
  try {
    const res = await superAdminApi.getDashboard()
    if (res.success && res.data) {
      stats.value = res.data
      updateCharts()
    }
  } catch (e) {
    console.error('获取统计数据失败', e)
    // 使用模拟数据
    updateCharts()
  }

  // 响应式
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  pieChart?.dispose()
  barChart?.dispose()
  lineChart?.dispose()
})

function handleResize() {
  pieChart?.resize()
  barChart?.resize()
  lineChart?.resize()
}

function updateCharts() {
  // 饼状图：用户角色分布
  const pieOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    color: ['#198754', '#ffc107', '#0dcaf0', '#6c757d', '#0d6efd'],
    series: [{
      name: '用户角色',
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: true,
        formatter: '{b}: {c}'
      },
      data: [
        { value: stats.value.elderly_count || 0, name: '老人' },
        { value: stats.value.volunteer_count || 0, name: '志愿者' },
        { value: stats.value.worker_count || 0, name: '工作人员' },
        { value: 1, name: '社区管理员' },
        { value: 1, name: '超级管理员' }
      ]
    }]
  }
  pieChart.setOption(pieOption)

  // 柱状图：各社区用户数量（模拟数据）
  const barOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['社区A', '社区B', '社区C', '社区D', '社区E'],
      axisLabel: { rotate: 0 }
    },
    yAxis: {
      type: 'value',
      name: '用户数'
    },
    series: [{
      name: '用户数量',
      type: 'bar',
      data: [
        Math.floor(Math.random() * 100) + 50,
        Math.floor(Math.random() * 80) + 40,
        Math.floor(Math.random() * 120) + 60,
        Math.floor(Math.random() * 90) + 30,
        Math.floor(Math.random() * 70) + 20
      ],
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#0d6efd' },
          { offset: 1, color: '#0dcaf0' }
        ]),
        borderRadius: [4, 4, 0, 0]
      },
      barWidth: '50%'
    }]
  }
  barChart.setOption(barOption)

  // 折线图：用户增长趋势
  const months = ['1月', '2月', '3月', '4月', '5月', '6月']
  const lineOption = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['总用户', '活跃用户'],
      top: 'top'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: months
    },
    yAxis: {
      type: 'value',
      name: '用户数'
    },
    series: [{
      name: '总用户',
      type: 'line',
      smooth: true,
      data: [120, 180, 250, 320, 420, 550],
      itemStyle: { color: '#0d6efd' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(13, 110, 253, 0.3)' },
          { offset: 1, color: 'rgba(13, 110, 253, 0.05)' }
        ])
      }
    }, {
      name: '活跃用户',
      type: 'line',
      smooth: true,
      data: [80, 130, 190, 260, 350, 480],
      itemStyle: { color: '#198754' },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(25, 135, 84, 0.3)' },
          { offset: 1, color: 'rgba(25, 135, 84, 0.05)' }
        ])
      }
    }]
  }
  lineChart.setOption(lineOption)
}

async function handleLogout() {
  await authStore.logout()
  router.push('/auth/login')
}
</script>

<style scoped>
.chart-container {
  height: 300px;
  width: 100%;
}

.chart-container-line {
  height: 350px;
  width: 100%;
}

.card {
  border: none;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.card-header {
  border-bottom: 1px solid #eee;
  font-weight: 600;
}
</style>