<template>
  <aside class="col-md-3 col-lg-2 p-0 bg-light sidebar">
    <div class="list-group list-group-flush">
      <template v-if="role === 'elderly'">
        <router-link to="/elderly/dashboard" class="list-group-item list-group-item-action">
          <i class="bi bi-house me-2"></i>首页
        </router-link>
        <router-link to="/elderly/sos" class="list-group-item list-group-item-action text-danger">
          <i class="bi bi-exclamation-triangle me-2"></i>SOS求助
        </router-link>
        <router-link to="/elderly/health" class="list-group-item list-group-item-action">
          <i class="bi bi-heart-pulse me-2"></i>健康监测
        </router-link>
        <router-link to="/elderly/medication" class="list-group-item list-group-item-action">
          <i class="bi bi-bell me-2"></i>用药提醒
        </router-link>
        <router-link to="/elderly/appointments" class="list-group-item list-group-item-action">
          <i class="bi bi-calendar-check me-2"></i>复诊提醒
        </router-link>
        <router-link to="/elderly/services" class="list-group-item list-group-item-action">
          <i class="bi bi-basket me-2"></i>预约服务
        </router-link>
        <router-link to="/elderly/orders" class="list-group-item list-group-item-action">
          <i class="bi bi-list-check me-2"></i>我的订单
        </router-link>
        <router-link to="/elderly/activities" class="list-group-item list-group-item-action">
          <i class="bi bi-calendar-event me-2"></i>活动报名
        </router-link>
      </template>

      <template v-else-if="role === 'volunteer'">
        <router-link to="/volunteer/dashboard" class="list-group-item list-group-item-action">
          <i class="bi bi-house me-2"></i>首页
        </router-link>
        <router-link to="/volunteer/tasks" class="list-group-item list-group-item-action">
          <i class="bi bi-hand-index-thumb me-2"></i>任务大厅
        </router-link>
        <router-link to="/volunteer/my-orders" class="list-group-item list-group-item-action">
          <i class="bi bi-list-check me-2"></i>我的任务
        </router-link>
        <router-link to="/volunteer/records" class="list-group-item list-group-item-action">
          <i class="bi bi-clock-history me-2"></i>服务记录
        </router-link>
        <router-link to="/volunteer/points" class="list-group-item list-group-item-action">
          <i class="bi bi-gift me-2"></i>积分商城
        </router-link>
      </template>

      <template v-else-if="role === 'worker'">
        <router-link to="/worker/dashboard" class="list-group-item list-group-item-action">
          <i class="bi bi-house me-2"></i>首页
        </router-link>
        <router-link to="/worker/orders" class="list-group-item list-group-item-action">
          <i class="bi bi-basket me-2"></i>工单中心
        </router-link>
        <router-link to="/worker/my-orders" class="list-group-item list-group-item-action">
          <i class="bi bi-list-check me-2"></i>我的工单
        </router-link>
        <router-link to="/worker/elderly" class="list-group-item list-group-item-action">
          <i class="bi bi-people me-2"></i>老人档案
        </router-link>
        <router-link to="/worker/visits" class="list-group-item list-group-item-action">
          <i class="bi bi-compass me-2"></i>走访记录
        </router-link>
      </template>

      <template v-else-if="role === 'community_admin'">
        <router-link to="/community-admin/dashboard" class="list-group-item list-group-item-action">
          <i class="bi bi-house me-2"></i>首页
        </router-link>
        <router-link to="/community-admin/elderly" class="list-group-item list-group-item-action">
          <i class="bi bi-people me-2"></i>老人管理
        </router-link>
        <router-link to="/community-admin/volunteers" class="list-group-item list-group-item-action">
          <i class="bi bi-person-hearts me-2"></i>志愿者管理
        </router-link>
        <router-link to="/community-admin/workers" class="list-group-item list-group-item-action">
          <i class="bi bi-briefcase me-2"></i>工作人员管理
        </router-link>
        <router-link to="/community-admin/orders" class="list-group-item list-group-item-action">
          <i class="bi bi-cart me-2"></i>订单管理
        </router-link>
        <router-link to="/community-admin/sos" class="list-group-item list-group-item-action text-danger">
          <i class="bi bi-exclamation-triangle me-2"></i>SOS警报
        </router-link>
        <router-link to="/community-admin/activities" class="list-group-item list-group-item-action">
          <i class="bi bi-calendar-event me-2"></i>活动管理
        </router-link>
      </template>

      <template v-else-if="role === 'super_admin'">
        <router-link to="/super-admin/dashboard" class="list-group-item list-group-item-action">
          <i class="bi bi-house me-2"></i>首页
        </router-link>
        <router-link to="/super-admin/communities" class="list-group-item list-group-item-action">
          <i class="bi bi-building me-2"></i>社区管理
        </router-link>
        <router-link to="/super-admin/users" class="list-group-item list-group-item-action">
          <i class="bi bi-people me-2"></i>用户管理
        </router-link>
        <router-link to="/super-admin/service-categories" class="list-group-item list-group-item-action">
          <i class="bi bi-grid me-2"></i>服务分类
        </router-link>
        <router-link to="/super-admin/news" class="list-group-item list-group-item-action">
          <i class="bi bi-newspaper me-2"></i>新闻管理
        </router-link>
        <router-link to="/super-admin/point-products" class="list-group-item list-group-item-action">
          <i class="bi bi-gift me-2"></i>积分商品
        </router-link>
        <router-link to="/super-admin/alert-rules" class="list-group-item list-group-item-action">
          <i class="bi bi-bell me-2"></i>预警规则
        </router-link>
        <router-link to="/super-admin/logs" class="list-group-item list-group-item-action">
          <i class="bi bi-file-text me-2"></i>系统日志
        </router-link>
      </template>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  role: String
})
</script>

<style scoped>
.sidebar {
  min-height: calc(100vh - 56px);
  padding-top: 1rem;
}
</style>