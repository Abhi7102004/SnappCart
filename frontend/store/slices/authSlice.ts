import { createSlice, createAsyncThunk, PayloadAction } from "@reduxjs/toolkit"
import { api, publicApi } from "@/lib/axios"
import { getApiError } from "@/lib/api-error"
import { User } from "@/types/user"
import {
  LoginRequest, LoginResponse,
  RegisterRequest, RegisterResponse,
} from "@/types/auth"

interface AuthState {
    user: User | null
    accessToken:string | null
    isLoggedIn:boolean
    isLoginLoading: boolean
    isRegisterLoading: boolean
    isFetchMeLoading: boolean
    error: string | null

}

const initialState: AuthState = {
    user: null,
    accessToken: null,
    isLoggedIn: false,
    isLoginLoading: false,
    isRegisterLoading: false,
    isFetchMeLoading: false,
    error: null,
}

export const loginUser = createAsyncThunk<
  LoginResponse,
  LoginRequest,
  { rejectValue: string }
>("auth/login", async (credentials, { rejectWithValue }) => {
  try {
    const { data } = await api.post<LoginResponse>("/auth/login", credentials)
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
            state.user = action.payload.user
            state.accessToken = action.payload.access_token
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
    },
})

export const { updateAccessToken, logout, clearAuthError } = authSlice.actions
export default authSlice.reducer