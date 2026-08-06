"use client"

import { store, persistor } from "@/store"
import { Provider } from "react-redux"
import { PersistGate } from "redux-persist/integration/react"
import { ThemeProvider } from "@/components/theme/theme-provider"
import { AuthBootstrap } from "@/components/auth/AuthBootstrap"

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <Provider store={store}>
        <PersistGate loading={null} persistor={persistor}>
        <AuthBootstrap>
          {children}
        </AuthBootstrap>
        </PersistGate>
      </Provider>
    </ThemeProvider>
  )
}