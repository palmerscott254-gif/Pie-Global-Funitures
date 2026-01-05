import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { CartItem } from '@/types';

interface CartState {
  items: CartItem[];
  totalItems: number;
  totalPrice: number;
  addItem: (item: Omit<CartItem, 'quantity'>) => void;
  removeItem: (id: number) => void;
  updateQuantity: (id: number, quantity: number) => void;
  clearCart: () => void;
}

const computeTotals = (items: CartItem[]) => {
  const totalItems = items.reduce((total, item) => total + item.quantity, 0);
  const totalPrice = items.reduce((total, item) => total + item.price * item.quantity, 0);
  return { totalItems, totalPrice };
};

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],
      totalItems: 0,
      totalPrice: 0,

      addItem: (item) => {
        const existingItem = get().items.find((i) => i.id === item.id);
        
        let newItems: CartItem[];
        if (existingItem) {
          newItems = get().items.map((i) =>
            i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i
          );
        } else {
          newItems = [...get().items, { ...item, quantity: 1 }];
        }
        
        const { totalItems, totalPrice } = computeTotals(newItems);
        set({ items: newItems, totalItems, totalPrice });
      },

      removeItem: (id) => {
        const newItems = get().items.filter((item) => item.id !== id);
        const { totalItems, totalPrice } = computeTotals(newItems);
        set({ items: newItems, totalItems, totalPrice });
      },

      updateQuantity: (id, quantity) => {
        if (quantity <= 0) {
          get().removeItem(id);
          return;
        }

        const newItems = get().items.map((item) =>
          item.id === id ? { ...item, quantity } : item
        );
        const { totalItems, totalPrice } = computeTotals(newItems);
        set({ items: newItems, totalItems, totalPrice });
      },

      clearCart: () => {
        set({ items: [], totalItems: 0, totalPrice: 0 });
      },
    }),
    {
      name: 'cart-storage',
    }
  )
);
