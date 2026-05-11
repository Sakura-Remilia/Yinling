import { createRouter, createWebHistory } from 'vue-router'

// 公开路由
import publicRoutes from './routes/publicRoutes'
import authRoutes from './routes/authRoutes'

const routes = [
  ...publicRoutes,
  ...authRoutes,
  // 404
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '页面不存在' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 银龄社区` : '银龄社区养老管理系统'
  next()
})

export default router