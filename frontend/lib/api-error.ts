/**
 * Lazy store accessor — avoids circular imports and SSR crashes.
 * Axios interceptors run only in the browser (Client Components),
 * so this is safe. Never import this in Server Components.
 */

export function getApiError(error: unknown): string {
    if (!error || typeof error !== "object") return "Something went wrong"
  
    const err = error as { response?: { data?: { detail?: unknown } } }
    const detail = err.response?.data?.detail
  
    if (!detail) return "Something went wrong"
    if (typeof detail === "string") return detail
    if (Array.isArray(detail) && detail.length > 0) {
      return detail.map((d: { msg?: string }) => d.msg || "Validation error").join(", ")
    }
    return "Something went wrong"
  }