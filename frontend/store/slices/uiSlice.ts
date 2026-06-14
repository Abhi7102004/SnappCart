// store/slices/uiSlice.ts

import { createSlice, PayloadAction } from "@reduxjs/toolkit"

interface UiState {
  isCartOpen: boolean
  isMobileMenuOpen: boolean
  isSearchOpen: boolean
  isPageLoading: boolean
}

const initialState: UiState = {
  isCartOpen: false,
  isMobileMenuOpen: false,
  isSearchOpen: false,
  isPageLoading: false,
}

const uiSlice = createSlice({
  name: "ui",
  initialState,
  reducers: {
    toggleCart: (state) => {
      state.isCartOpen = !state.isCartOpen
    },
    setCartOpen: (state, action: PayloadAction<boolean>) => {
      state.isCartOpen = action.payload
    },
    toggleMobileMenu: (state) => {
      state.isMobileMenuOpen = !state.isMobileMenuOpen
    },
    toggleSearch: (state) => {
      state.isSearchOpen = !state.isSearchOpen
    },
    setPageLoading: (state, action: PayloadAction<boolean>) => {
      state.isPageLoading = action.payload
    },
  },
})

export const {
  toggleCart,
  setCartOpen,
  toggleMobileMenu,
  toggleSearch,
  setPageLoading,
} = uiSlice.actions
export default uiSlice.reducer