// lib/store-accessor.ts
/**
 * Lazy store accessor — avoids circular imports and SSR crashes.
 * Axios interceptors run only in the browser (Client Components),
 * so this is safe. Never import this in Server Components.
 */

import type { AppDispatch, RootState } from "@/store"

let _store: { getState: () => RootState; dispatch: AppDispatch } | null = null

export function getStore() {
  if (!_store) {
    _store = require("@/store").store
  }
  return _store
}