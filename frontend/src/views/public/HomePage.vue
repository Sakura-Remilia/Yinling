<template>
  <div class="home-page">
    <!-- 导航栏 -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container">
        <router-link to="/" class="navbar-brand">
          <i class="bi bi-heart-pulse"></i> 银龄社区
        </router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <router-link to="/" class="nav-link active">首页</router-link>
            </li>
            <li class="nav-item">
              <router-link to="/about" class="nav-link">关于我们</router-link>
            </li>
            <li class="nav-item">
              <router-link to="/contact" class="nav-link">联系我们</router-link>
            </li>
            <li class="nav-item ms-2">
              <router-link to="/auth/login" class="btn btn-light">登录</router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <div class="hero-section bg-light py-5">
      <div class="container text-center py-5">
        <h1 class="display-4 mb-4">智慧养老 温暖相伴</h1>
        <p class="lead text-muted mb-4">为老年人提供全方位的养老服务，让爱与关怀无处不在</p>
        <router-link to="/auth/register" class="btn btn-primary btn-lg me-2">立即体验</router-link>
        <router-link to="/about" class="btn btn-outline-secondary btn-lg">了解更多</router-link>
      </div>
    </div>

    <!-- 服务介绍 -->
    <div class="container my-5">
      <h2 class="text-center mb-4">我们的服务</h2>
      <div class="row g-4">
        <div class="col-md-4">
          <div class="card h-100 text-center border-0 shadow-sm">
            <div class="card-body p-4">
              <i class="bi bi-people display-4 text-primary mb-3"></i>
              <h5 class="card-title">社区养老</h5>
              <p class="card-text text-muted">足不出户的社区养老服务，专业护理人员上门照护</p>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card h-100 text-center border-0 shadow-sm">
            <div class="card-body p-4">
              <i class="bi bi-heart-pulse display-4 text-danger mb-3"></i>
              <h5 class="card-title">健康监测</h5>
              <p class="card-text text-muted">实时监测血压、血糖等健康数据，守护老人健康</p>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card h-100 text-center border-0 shadow-sm">
            <div class="card-body p-4">
              <i class="bi bi-bell display-4 text-warning mb-3"></i>
              <h5 class="card-title">紧急求助</h5>
              <p class="card-text text-muted">一键SOS紧急求助，快速响应保障安全</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 页脚 -->
    <footer class="bg-dark text-white py-4 mt-5">
      <div class="container text-center">
        <p class="mb-0">© 2024 银龄社区养老管理系统. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
</script>

<style scoped>
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.hero-section h1 {
  font-weight: 700;
}

.hero-section .lead {
  color: rgba(255, 255, 255, 0.9) !important;
}

.navbar-brand i {
  margin-right: 8px;
}
</style>