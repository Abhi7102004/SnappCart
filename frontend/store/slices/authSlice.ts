import { createSlice, PayloadAction } from "@reduxjs/toolkit"
import { User } from "@/types/user"

interface AuthState {
    user: User | null
    accessToken:string | null
    isLoggedIn:boolean
    isLoading:boolean
}

const initialState: AuthState = {
    user: null,
    accessToken: null,
    isLoggedIn: false,
    isLoading: false,
}

const authSlice = createSlice({
    name:"auth",
    initialState,
    reducers:{
        setCredentials: (
            state,
            action:PayloadAction<{ user: User; accessToken: string }>
        )=>{
            state.user=action.payload.user
            state.accessToken=action.payload.accessToken
            state.isLoggedIn=true
        },
        updateAccessToken: (state, action: PayloadAction<string>) => {
            state.accessToken = action.payload
        },
        logout: (state)=>{
            state.user=null
            state.accessToken=null
            state.isLoggedIn=false
        },
        setLoading:(state,action: PayloadAction<boolean>)=>{
            state.isLoading=action.payload
        }
    }
})

export const {setCredentials,updateAccessToken,logout,setLoading}=authSlice.actions

export default authSlice.reducer