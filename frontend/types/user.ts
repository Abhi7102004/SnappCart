
export interface User {
    id:string
    email:string | null
    phone:string | null
    username:string | null
    full_name:string | null
    role: "customer" | "seller" | "admin"
    avatar_url:string | null
    oauth_avatar_url: string | null
    is_email_verified:boolean
    is_phone_verified:boolean
    oauth_provider: "local" | "google" | "github"
    created_at: string
}