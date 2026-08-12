import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit"
import { api, publicApi } from "@/lib/axios"
import { getApiError } from "@/lib/api-error"
import { User } from "@/types/user"
import {
  LoginRequest, LoginResponse,RegisterRequest,
  RegisterResponse,MessageResponse,
  ResetPasswordRequest,
} from "@/types/auth"
import { TwoFactorLoginResponse } from "@/types/two-factor"

interface AuthState {
    user: User | null
    accessToken:string | null
    isLoggedIn:boolean
    isLoginLoading: boolean
    isRegisterLoading: boolean
    isFetchMeLoading: boolean
    isForgotPasswordLoading: boolean
    isResetPasswordLoading: boolean
    isResendVerificationLoading: boolean
    pendingTwoFactorSession: string | null
    isTwoFactorRequired: boolean
    error: string | null

}

const initialState: AuthState = {
    user: null,
    accessToken: null,
    isLoggedIn: false,
    isLoginLoading: false,
    isRegisterLoading: false,
    isFetchMeLoading: false,
    isForgotPasswordLoading:false,
    isResetPasswordLoading:false,
    isResendVerificationLoading:false,
    pendingTwoFactorSession:null,
    isTwoFactorRequired: false,
    error: null,
}

export const loginUser = createAsyncThunk<
  LoginResponse | TwoFactorLoginResponse,
  LoginRequest,
  { rejectValue: string }
>("auth/login", async (credentials, { rejectWithValue }) => {
  try {
    const { data } = await api.post("/auth/login", credentials)
    return data
  } catch (error) {
    return rejectWithValue(getApiError(error))
  }
})

export const registerUser = createAsyncThunk<
  RegisterResponse,
  RegisterRequest,
  { rejectValue: string }
>("auth/register", async (payload, { rejectWithValue }) => {
  try {
    const { data } = await publicApi.post<RegisterResponse>("/auth/register", payload)
    return data
  } catch (error) {
    return rejectWithValue(getApiError(error))
  }
})

export const fetchCurrentUser = createAsyncThunk<
  User,
  void,
  { rejectValue: string }
>("auth/fetchMe", async (_, { rejectWithValue }) => {
  try {
    const { data } = await api.get<User>("/auth/me")
    return data
  } catch (error) {
    return rejectWithValue(getApiError(error))
  }
})

export const verifyEmail = createAsyncThunk<
  MessageResponse,
  string,
  { rejectValue: string }
>("auth/verifyEmail", async (token, { rejectWithValue }) => {
  try {
    const { data } = await publicApi.post<MessageResponse>("/auth/verify-email", { token })
    return data
  } catch (error) {
    return rejectWithValue(getApiError(error))
  }
})

export const resendVerificationEmail = createAsyncThunk<
  MessageResponse,
  string,
  { rejectValue: string }
>("auth/resendVerification", async (email, { rejectWithValue }) => {
  try {
    const { data } = await publicApi.post<MessageResponse>("/auth/resend-verification", { email })
    return data
  } catch (error) {
    return rejectWithValue(getApiError(error))
  }
})

export const forgotPassword = createAsyncThunk<
  MessageResponse,
  string,
  { rejectValue: string }
>("auth/forgotPassword", async (email, { rejectWithValue }) => {
  try {
    const { data } = await publicApi.post<MessageResponse>("/auth/forgot-password", { email })
    return data
  } catch (error) {
    return rejectWithValue(getApiError(error))
  }
})

export const resetPassword = createAsyncThunk<
  MessageResponse,
  ResetPasswordRequest,
  { rejectValue: string }
>("auth/resetPassword", async (payload, { rejectWithValue }) => {
  try {
    const { data } = await publicApi.post<MessageResponse>("/auth/reset-password", payload)
    return data
  } catch (error) {
    return rejectWithValue(getApiError(error))
  }
})

export const logoutUser = createAsyncThunk<void, void>(
    "auth/logout",
    async () => {
      try {
        await api.post("/auth/logout")
      } catch {
        // logout should never fail
      }
    }
  )

const authSlice = createSlice({
    name:"auth",
    initialState,
    reducers:{
        updateAccessToken: (state, action: PayloadAction<string>) => {
            state.accessToken = action.payload
        },
        logout: (state)=>{
            state.user=null
            state.accessToken=null
            state.isLoggedIn=false
        },
        clearAuthError: (state) => {
            state.error = null
        },
        clearTwoFactorState: (state) => {
          state.isTwoFactorRequired = false
          state.pendingTwoFactorSession = null
        },
    },
    extraReducers: (builder) => {
        builder
        // ── Login ──
        .addCase(loginUser.pending, (state) => {
            state.isLoginLoading = true
            state.error = null
        })
        .addCase(loginUser.fulfilled, (state, action) => {
          state.isLoginLoading = false
        
          const payload = action.payload
        
          if ("two_factor_required" in payload) {
            state.isTwoFactorRequired = true
            state.pendingTwoFactorSession = payload.session_token
            return
          }
        
          state.user = payload.user
          state.accessToken = payload.access_token
          state.isTwoFactorRequired = false
          state.pendingTwoFactorSession = null
          state.isLoggedIn = true
        })
        .addCase(loginUser.rejected, (state, action) => {
            state.isLoginLoading = false
            state.error = action.payload || "Login failed"
        })
        
        // ── Register ──
        .addCase(registerUser.pending, (state) => {
            state.isRegisterLoading = true
            state.error = null
        })
        .addCase(registerUser.fulfilled, (state) => {
            state.isRegisterLoading = false
        })
        .addCase(registerUser.rejected, (state, action) => {
            state.isRegisterLoading = false
            state.error = action.payload || "Registration failed"
        })

        // ── Fetch current user ──
        .addCase(fetchCurrentUser.pending, (state) => {
            state.isFetchMeLoading = true
        })
        .addCase(fetchCurrentUser.fulfilled, (state, action) => {
            state.isFetchMeLoading = false
            state.user = action.payload
            state.isLoggedIn = true
        })
        .addCase(fetchCurrentUser.rejected, (state) => {
            state.isFetchMeLoading = false
        })

        // ── Logout ──
        .addCase(logoutUser.fulfilled, (state) => {
            state.user = null
            state.accessToken = null
            state.isLoggedIn = false
        })

        .addCase(resendVerificationEmail.pending, (state) => {
            state.isResendVerificationLoading = true
        })
        .addCase(resendVerificationEmail.fulfilled, (state) => {
            state.isResendVerificationLoading = false
        })
        .addCase(resendVerificationEmail.rejected, (state) => {
            state.isResendVerificationLoading = false
        })
        
        .addCase(forgotPassword.pending, (state) => {
            state.isForgotPasswordLoading = true
        })
        .addCase(forgotPassword.fulfilled, (state) => {
            state.isForgotPasswordLoading = false
        })
        .addCase(forgotPassword.rejected, (state) => {
            state.isForgotPasswordLoading = false
        })
        
        .addCase(resetPassword.pending, (state) => {
            state.isResetPasswordLoading = true
        })
        .addCase(resetPassword.fulfilled, (state) => {
            state.isResetPasswordLoading = false
        })
        .addCase(resetPassword.rejected, (state) => {
            state.isResetPasswordLoading = false
        })
    },
})

export const { updateAccessToken, logout, clearAuthError,clearTwoFactorState } = authSlice.actions
export default authSlice.reducer