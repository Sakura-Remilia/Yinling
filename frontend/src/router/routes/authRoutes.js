export default [
  {
    path: '/auth',
    component: () => import('@/layouts/BlankLayout.vue'),
    children: [
      {
        path: 'login',
        name: 'login',
        component: () => import('@/views/auth/LoginPage.vue'),
        meta: { title: '登录' }
      },
      {
        path: 'register',
        name: 'register',
        component: () => import('@/views/auth/RegisterPage.vue'),
        meta: { title: '注册' }
      }
    ]
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('@/views/auth/ProfilePage.vue'),
    meta: { requiresAuth: true, title: '个人设置' }
  }
]