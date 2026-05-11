const TokenKey = 'yinling_token'
const RefreshTokenKey = 'yinling_refresh_token'
const UserKey = 'yinling_user'

export const storage = {
  getToken() {
    return localStorage.getItem(TokenKey)
  },
  setToken(token) {
    localStorage.setItem(TokenKey, token)
  },
  getRefreshToken() {
    return localStorage.getItem(RefreshTokenKey)
  },
  setRefreshToken(token) {
    localStorage.setItem(RefreshTokenKey, token)
  },
  getUser() {
    const userStr = localStorage.getItem(UserKey)
    return userStr ? JSON.parse(userStr) : null
  },
  setUser(user) {
    localStorage.setItem(UserKey, JSON.stringify(user))
  },
  removeTokens() {
    localStorage.removeItem(TokenKey)
    localStorage.removeItem(RefreshTokenKey)
    localStorage.removeItem(UserKey)
  }
}