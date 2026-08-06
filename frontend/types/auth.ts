import { User } from "./user"

export interface LoginRequest {
  email_or_phone: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface RegisterRequest {
  email?: string
  phone?: string
  password: string
  full_name?: string
}

export interface RegisterResponse {
  message: string
  user: User
  email_verification_sent: boolean
}

export interface RefreshResponse {
  access_token: string
  token_type: string
}

export interface MessageResponse {
  message: string
}