
export interface ApiResponse<T>{
    data : T
    message?:string
    status:string
}

export interface ApiError{
    detail:string
    status_code:string
}

export interface PaginatedResponse<T>{
    items:T[]
    total:number
    page:number
    per_page:number
    total_pages:number
}

export interface HealthCheck{
    status:string
    version:string
    environment:string
    services:{
        api:boolean
        postgresql:boolean
        redis:boolean
    }
}