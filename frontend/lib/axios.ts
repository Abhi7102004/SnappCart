"use client";

import axios, {
  AxiosInstance,
  InternalAxiosRequestConfig,
  AxiosError,
} from "axios";
import { getStore } from "@/lib/store-accessor";
import { updateAccessToken, logout } from "@/store/slices/authSlice";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const publicApi: AxiosInstance = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});

export const api: AxiosInstance = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
  withCredentials: true, // sends httpOnly refresh_token cookie automatically
});

// ── Dedicated refresh instance ───────────────────────────────────
// Separate from both api and publicApi:
//   api      → has JWT interceptor (would cause infinite loop on refresh 401)
//   publicApi → no withCredentials (httpOnly cookie never sent)
// This instance has NEITHER interceptor AND has withCredentials ✅
const refreshApi: AxiosInstance = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
  withCredentials: true,
});

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const store = getStore();
    const token = store?.getState().auth.accessToken;
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((p) => (error ? p.reject(error) : p.resolve(token!)));
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      })
        .then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        })
        .catch((err) => Promise.reject(err));
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const { data } = await refreshApi.post("/auth/refresh");
      const newToken: string = data.access_token;

      const store = getStore();
      store?.dispatch(updateAccessToken(newToken));

      processQueue(null, newToken);

      originalRequest.headers.Authorization = `Bearer ${newToken}`;
      return api(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError, null);

      const store = getStore();
      store?.dispatch(logout());

      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }

      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

export default api;
