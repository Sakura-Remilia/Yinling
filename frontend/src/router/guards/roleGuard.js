import { useAuthStore } from '@/stores/auth'

export const roleGuard = (to, from, next) => {
  const authStore = useAuthStore()
  const requiredRoles = to.meta.roles

  if (requiredRoles && !requiredRoles.includes(authStore.userRole)) {
    next({ name: 'unauthorized' })
  } else {
    next()
  }
}