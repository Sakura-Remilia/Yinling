import request from '@/utils/request'

// 认证相关API
export const authApi = {
  login(data) {
    return request.post('/auth/login', data)
  },
  register(data) {
    return request.post('/auth/register', data)
  },
  logout() {
    return request.post('/auth/logout')
  },
  getUser() {
    return request.get('/auth/user')
  },
  updateProfile(data) {
    return request.put('/auth/profile', data)
  },
  changePassword(data) {
    return request.put('/auth/password', data)
  },
  refreshToken(refreshToken) {
    return request.post('/auth/refresh', { refresh_token: refreshToken })
  }
}

// 用户相关API
export const userApi = {
  getUsers(params) {
    return request.get('/users', { params })
  },
  getUser(id) {
    return request.get(`/users/${id}`)
  },
  createUser(data) {
    return request.post('/users', data)
  },
  updateUser(id, data) {
    return request.put(`/users/${id}`, data)
  },
  toggleUserActive(id, isActive) {
    return request.put(`/users/${id}/toggle-active`, { is_active: isActive })
  },
  resetPassword(id, newPassword) {
    return request.put(`/users/${id}/reset-password`, { new_password: newPassword })
  },
  deleteUser(id) {
    return request.delete(`/users/${id}`)
  }
}

// 老人模块API
export const elderlyApi = {
  getProfile() {
    return request.get('/elderly/profile')
  },
  updateProfile(data) {
    return request.put('/elderly/profile', data)
  },
  getHealthRecords(params) {
    return request.get('/elderly/health-records', { params })
  },
  createHealthRecord(data) {
    return request.post('/elderly/health-records', data)
  },
  getMedicationReminders() {
    return request.get('/elderly/medication-reminders')
  },
  createMedicationReminder(data) {
    return request.post('/elderly/medication-reminders', data)
  },
  updateMedicationReminder(id, data) {
    return request.put(`/elderly/medication-reminders/${id}`, data)
  },
  deleteMedicationReminder(id) {
    return request.delete(`/elderly/medication-reminders/${id}`)
  },
  getAppointments() {
    return request.get('/elderly/appointments')
  },
  createAppointment(data) {
    return request.post('/elderly/appointments', data)
  },
  updateAppointment(id, data) {
    return request.put(`/elderly/appointments/${id}`, data)
  },
  deleteAppointment(id) {
    return request.delete(`/elderly/appointments/${id}`)
  },
  completeAppointment(id) {
    return request.post(`/elderly/appointments/${id}/complete`)
  }
}

// 志愿者模块API
export const volunteerApi = {
  getProfile() {
    return request.get('/volunteer/profile')
  },
  updateProfile(data) {
    return request.put('/volunteer/profile', data)
  },
  getTasks(params) {
    return request.get('/volunteer/tasks', { params })
  },
  acceptTask(taskId) {
    return request.post(`/volunteer/tasks/${taskId}/accept`)
  },
  getOrders(params) {
    return request.get('/volunteer/orders', { params })
  },
  checkin(orderId) {
    return request.post(`/volunteer/orders/${orderId}/checkin`)
  },
  complete(orderId) {
    return request.post(`/volunteer/orders/${orderId}/complete`)
  },
  getRecords(params) {
    return request.get('/volunteer/records', { params })
  },
  getPoints() {
    return request.get('/volunteer/points')
  },
  getPointTransactions(params) {
    return request.get('/volunteer/points/transactions', { params })
  },
  getProducts(params) {
    return request.get('/volunteer/points/products', { params })
  },
  exchangeProduct(productId) {
    return request.post(`/volunteer/points/exchange/${productId}`)
  }
}

// 工作人员模块API
export const workerApi = {
  getProfile() {
    return request.get('/worker/profile')
  },
  updateProfile(data) {
    return request.put('/worker/profile', data)
  },
  getOrders(params) {
    return request.get('/worker/orders', { params })
  },
  acceptOrder(orderId) {
    return request.post(`/worker/orders/${orderId}/accept`)
  },
  getMyOrders(params) {
    return request.get('/worker/my-orders', { params })
  },
  arrive(orderId) {
    return request.post(`/worker/orders/${orderId}/arrive`)
  },
  completeOrder(orderId, data) {
    return request.post(`/worker/orders/${orderId}/complete`, data)
  },
  getElderlyList(params) {
    return request.get('/worker/elderly', { params })
  },
  getElderlyDetail(id) {
    return request.get(`/worker/elderly/${id}`)
  },
  getVisits(params) {
    return request.get('/worker/visits', { params })
  },
  createVisit(data) {
    return request.post('/worker/visits', data)
  },
  completeVisit(id, data) {
    return request.post(`/worker/visits/${id}/complete`, data)
  },
  getFollowUps(params) {
    return request.get('/worker/follow-ups', { params })
  },
  createFollowUp(data) {
    return request.post('/worker/follow-ups', data)
  }
}

// 社区管理员API
export const communityAdminApi = {
  getDashboard() {
    return request.get('/community-admin/dashboard')
  },
  getElderlyList(params) {
    return request.get('/community-admin/elderly', { params })
  },
  getVolunteers(params) {
    return request.get('/community-admin/volunteers', { params })
  },
  verifyVolunteer(id) {
    return request.post(`/community-admin/volunteers/${id}/verify`)
  },
  getWorkers(params) {
    return request.get('/community-admin/workers', { params })
  },
  verifyWorker(id) {
    return request.post(`/community-admin/workers/${id}/verify`)
  },
  markWorkerTrained(id) {
    return request.post(`/community-admin/workers/${id}/train`)
  },
  getOrders(params) {
    return request.get('/community-admin/orders', { params })
  },
  getSOSList(params) {
    return request.get('/community-admin/sos', { params })
  },
  getActivities(params) {
    return request.get('/community-admin/activities', { params })
  },
  createActivity(data) {
    return request.post('/community-admin/activities', data)
  },
  updateActivity(id, data) {
    return request.put(`/community-admin/activities/${id}`, data)
  },
  getAccounts(params) {
    return request.get('/community-admin/accounts', { params })
  },
  getAlerts(params) {
    return request.get('/community-admin/alerts', { params })
  }
}

// 超级管理员API
export const superAdminApi = {
  getDashboard() {
    return request.get('/super-admin/dashboard')
  },
  // 社区管理
  getCommunities(params) {
    return request.get('/super-admin/communities', { params })
  },
  createCommunity(data) {
    return request.post('/super-admin/communities', data)
  },
  updateCommunity(id, data) {
    return request.put(`/super-admin/communities/${id}`, data)
  },
  deleteCommunity(id) {
    return request.delete(`/super-admin/communities/${id}`)
  },
  // 用户管理
  getUsers(params) {
    return request.get('/users', { params })
  },
  createUser(data) {
    return request.post('/users', data)
  },
  updateUser(id, data) {
    return request.put(`/users/${id}`, data)
  },
  deleteUser(id) {
    return request.delete(`/users/${id}`)
  },
  // 服务分类管理
  getServiceCategories(params) {
    return request.get('/super-admin/service-categories', { params })
  },
  createServiceCategory(data) {
    return request.post('/super-admin/service-categories', data)
  },
  updateServiceCategory(id, data) {
    return request.put(`/super-admin/service-categories/${id}`, data)
  },
  deleteServiceCategory(id) {
    return request.delete(`/super-admin/service-categories/${id}`)
  },
  // 新闻管理
  getNews(params) {
    return request.get('/super-admin/news', { params })
  },
  createNews(data) {
    return request.post('/super-admin/news', data)
  },
  updateNews(id, data) {
    return request.put(`/super-admin/news/${id}`, data)
  },
  deleteNews(id) {
    return request.delete(`/super-admin/news/${id}`)
  },
  // 积分商品管理
  getPointProducts(params) {
    return request.get('/super-admin/point-products', { params })
  },
  createPointProduct(data) {
    return request.post('/super-admin/point-products', data)
  },
  updatePointProduct(id, data) {
    return request.put(`/super-admin/point-products/${id}`, data)
  },
  deletePointProduct(id) {
    return request.delete(`/super-admin/point-products/${id}`)
  },
  // 预警规则管理
  getAlertRules(params) {
    return request.get('/super-admin/alert-rules', { params })
  },
  createAlertRule(data) {
    return request.post('/super-admin/alert-rules', data)
  },
  updateAlertRule(id, data) {
    return request.put(`/super-admin/alert-rules/${id}`, data)
  },
  deleteAlertRule(id) {
    return request.delete(`/super-admin/alert-rules/${id}`)
  },
  // 日志
  getLogs(params) {
    return request.get('/super-admin/logs', { params })
  }
}

// 订单API
export const orderApi = {
  getOrders(params) {
    return request.get('/orders', { params })
  },
  getOrderDetail(id) {
    return request.get(`/orders/${id}`)
  },
  createOrder(data) {
    return request.post('/orders', data)
  },
  updateOrderStatus(id, data) {
    return request.put(`/orders/${id}/status`, data)
  },
  reviewOrder(id, data) {
    return request.post(`/orders/${id}/review`, data)
  },
  getCategories() {
    return request.get('/orders/categories')
  }
}

// 活动API
export const activityApi = {
  getActivities(params) {
    return request.get('/activities', { params })
  },
  getActivityDetail(id) {
    return request.get(`/activities/${id}`)
  },
  register(id) {
    return request.post(`/activities/${id}/register`)
  },
  cancelRegistration(id) {
    return request.post(`/activities/${id}/cancel`)
  },
  getMyRegistrations() {
    return request.get('/activities/my-registrations')
  }
}

// SOS API
export const sosApi = {
  trigger(data) {
    return request.post('/sos/trigger', data)
  },
  getMyAlerts(params) {
    return request.get('/sos/my-alerts', { params })
  },
  getAlertDetail(id) {
    return request.get(`/sos/${id}`)
  },
  respond(id) {
    return request.post(`/sos/${id}/respond`)
  },
  resolve(id, data) {
    return request.post(`/sos/${id}/resolve`, data)
  },
  cancel(id) {
    return request.post(`/sos/${id}/cancel`)
  }
}

// 公开API
export const publicApi = {
  getNews(params) {
    return request.get('/public/news', { params })
  },
  getNewsDetail(id) {
    return request.get(`/public/news/${id}`)
  },
  getActivities(params) {
    return request.get('/public/activities', { params })
  },
  getServiceCategories() {
    return request.get('/public/service-categories')
  },
  getCommunities(params) {
    return request.get('/public/communities', { params })
  }
}