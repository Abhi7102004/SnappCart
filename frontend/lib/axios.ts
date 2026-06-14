import axios from "axios"
import { store } from "@/store"
import { updateAccessToken, logout } from "@/store/slices/authSlice"

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export const publicApi = axios.create({
    baseURL: `${BASE_URL}/api/v1`,
    timeout: 10000,
    headers: {
        "Content-Type": "application/json",
    },
})

export const api = axios.create({
    baseURL: `${BASE_URL}/api/v1`,
    timeout: 10000,
    headers: {
        "Content-Type": "application/json",
    },
    withCredentials:true
})

api.interceptors.request.use(
    (config)=>{
        const state = store.getState()
        const token = state.auth.accessToken
        if(token){
            config.headers.Authorization =`Bearer ${token}`
        }
        return config
    },
    (error) => Promise.reject(error)
)

let isRefreshing = false
let failedQueue: Array<{
  resolve: (token: string) => void
  reject: (error: unknown) => void
}> = []

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error)
    } else {
      promise.resolve(token!)
    }
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Queue requests while refreshing
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return api(originalRequest)
          })
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        // Refresh token sent automatically via httpOnly cookie
        const response = await publicApi.post("/auth/refresh")
        const { access_token } = response.data

        store.dispatch(updateAccessToken(access_token))
        processQueue(null, access_token)

        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        store.dispatch(logout())
        window.location.href = "/login"
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

export default api
