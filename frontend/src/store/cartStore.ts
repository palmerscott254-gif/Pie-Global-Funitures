import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { cartApi } from '@/services/api';
import type { CartItem, CartResponse } from '@/types';

interface CartState {
  items: CartItem[];
  totalItems: number;
  totalPrice: number;
  addItem: (item: Omit<CartItem, 'quantity'>) => void;
  removeItem: (id: number) => void;
  updateQuantity: (id: number, quantity: number) => void;
  clearCart: () => void;
  hydrateFromServer: (cart: CartResponse) => void;
  syncFromServer: () => Promise<void>;
  syncGuestCart: () => Promise<void>;
}

const computeTotals = (items: CartItem[]) => {
  const totalItems = items.reduce((total, item) => total + item.quantity, 0);
  const totalPrice = items.reduce((total, item) => total + item.price * item.quantity, 0);
  return { totalItems, totalPrice };
};

const isAuthenticated = () => Boolean(localStorage.getItem('pgf-auth-access'));

const normalizeServerCart = (cart: CartResponse): CartItem[] => {
  return (cart.items || [])
    .map((entry) => {
      const product = entry.product;
      if (!product) return null;
      return {
        id: product.id,
        cartItemId: entry.id,
        name: product.name,
        price: typeof product.price === 'string' ? parseFloat(product.price) : product.price,
        quantity: entry.quantity,
        image: product.image || product.main_image || '',
        slug: product.slug,
      } as CartItem;
    })
    .filter(Boolean) as CartItem[];
};

const setCartState = (set: any, items: CartItem[]) => {
  const { totalItems, totalPrice } = computeTotals(items);
  set({ items, totalItems, totalPrice });
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
        
        setCartState(set, newItems);

        if (isAuthenticated()) {
          void cartApi.addToCart(item.id, 1)
            .then(() => get().syncFromServer())
            .catch(() => undefined);
        }
      },

      removeItem: (id) => {
        const existingItem = get().items.find((item) => item.id === id);
        const newItems = get().items.filter((item) => item.id !== id);
        setCartState(set, newItems);

        if (isAuthenticated() && existingItem) {
          const itemId = existingItem.cartItemId ?? id;
          void cartApi.removeItem(itemId)
            .then(() => get().syncFromServer())
            .catch(() => undefined);
        }
      },

      updateQuantity: (id, quantity) => {
        if (quantity <= 0) {
          get().removeItem(id);
          return;
        }

        const existingItem = get().items.find((item) => item.id === id);
        const newItems = get().items.map((item) =>
          item.id === id ? { ...item, quantity } : item
        );
        setCartState(set, newItems);

        if (isAuthenticated() && existingItem) {
          const itemId = existingItem.cartItemId ?? id;
          void cartApi.updateItem(itemId, quantity)
            .then(() => get().syncFromServer())
            .catch(() => undefined);
        }
      },

      clearCart: () => {
        set({ items: [], totalItems: 0, totalPrice: 0 });
      },

      hydrateFromServer: (cart) => {
        const items = normalizeServerCart(cart);
        setCartState(set, items);
      },

      syncFromServer: async () => {
        try {
          if (!isAuthenticated()) return;
          const cart = await cartApi.getCart();
          get().hydrateFromServer(cart);
        } catch {
          // silent fallback; keep local cart
        }
      },

      syncGuestCart: async () => {
        try {
          if (!isAuthenticated()) return;
          const localItems = get().items;
          if (!localItems.length) {
            await get().syncFromServer();
            return;
          }

          await cartApi.mergeGuestCart(
            localItems.map((item) => ({ product_id: item.id, quantity: item.quantity }))
          );
          await get().syncFromServer();
        } catch {
          // Keep local cart if server merge fails
        }
      },
    }),
    {
      name: 'cart-storage',
    }
  )
);
