import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const sidebarCollapsed = ref(false)
  const pageLoading = ref(false)
  const breadcrumbs = ref([])

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
  }

  function setPageLoading(loading) {
    pageLoading.value = loading
  }

  function setBreadcrumbs(items) {
    breadcrumbs.value = items
  }

  return {
    sidebarCollapsed,
    pageLoading,
    breadcrumbs,
    toggleSidebar,
    setPageLoading,
    setBreadcrumbs
  }
})