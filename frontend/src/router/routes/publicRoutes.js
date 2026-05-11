export default [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/public/HomePage.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('@/views/public/AboutPage.vue'),
    meta: { title: '关于我们' }
  },
  {
    path: '/contact',
    name: 'contact',
    component: () => import('@/views/public/ContactPage.vue'),
    meta: { title: '联系我们' }
  }
]