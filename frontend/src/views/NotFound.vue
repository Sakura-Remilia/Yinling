<template>
  <div class="not-found-page">
    <div class="text-center">
      <h1 class="display-1">404</h1>
      <h2>页面不存在</h2>
      <p class="text-muted mb-4">抱歉，您访问的页面不存在或已被删除</p>
      <router-link to="/" class="btn btn-primary">返回首页</router-link>
    </div>
  </div>
</template>

<style scoped>
.not-found-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>