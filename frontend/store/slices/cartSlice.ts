import { createSlice,PayloadAction } from "@reduxjs/toolkit";


export interface CartItem {
    productId: string
    variantId: string | null
    name: string
    price: number
    quantity: number
    imageUrl: string
    stock: number
    sellerId: string
  }

interface CartState {
    items: CartItem[]
    couponCode: string | null
    discount: number
    loyaltyPointsUsed: number
    walletAmountUsed: number
  }

const initialState: CartState = {
    items:[],
    couponCode:null,
    discount: 0,
    loyaltyPointsUsed: 0,
    walletAmountUsed: 0
}

const cartSlice = createSlice({
    name:"cart",
    initialState,
    reducers:{
        addToCart(state,action:PayloadAction<CartItem>){
            const existing = state.items.find(
                (i)=> i.productId===action.payload.productId && i.variantId===action.payload.variantId
            )
            if(existing){
                existing.quantity+=action.payload.quantity
            }else{
                state.items.push(action.payload)
            }
        },
        removeFromCart: (
            state,
            action: PayloadAction<{ productId: string; variantId: string | null }>
          ) => {
            state.items = state.items.filter(
              (i) =>
                !(i.productId === action.payload.productId &&
                  i.variantId === action.payload.variantId)
            )
        },
        updateQuantity: (
            state,
            action: PayloadAction<{
              productId: string
              variantId: string | null
              quantity: number
            }>
          ) => {
            const item = state.items.find(
              (i) =>
                i.productId === action.payload.productId &&
                i.variantId === action.payload.variantId
            )
            if (item) {
              item.quantity = action.payload.quantity
            }
        },
        clearCart: (state) => {
            state.items = []
            state.couponCode = null
            state.discount = 0
            state.loyaltyPointsUsed = 0
            state.walletAmountUsed = 0
        },
        applyCoupon: (
            state,
            action: PayloadAction<{ code: string; discount: number }>
          ) => {
            state.couponCode = action.payload.code
            state.discount = action.payload.discount
        },
        removeCoupon: (state) => {
            state.couponCode = null
            state.discount = 0
        },
        setLoyaltyPoints: (state, action: PayloadAction<number>) => {
            state.loyaltyPointsUsed = action.payload
          },
        setWalletAmount: (state, action: PayloadAction<number>) => {
            state.walletAmountUsed = action.payload
        },
    }
})

export const {
    addToCart,
    removeFromCart,
    updateQuantity,
    clearCart,
    applyCoupon,
    removeCoupon,
    setLoyaltyPoints,
    setWalletAmount,
} = cartSlice.actions
export default cartSlice.reducer