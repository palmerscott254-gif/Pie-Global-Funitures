import axios, { AxiosError } from 'axios';
import type {
  Product,
  Order,
  SliderImage,
  HomeVideo,
  ContactMessage,
  AboutPage,
  PaginatedResponse,
  AuthResponse,
  DashboardSummary,
  DashboardAlert,
  AdminOrder,
  AdminMessage,
  CartResponse,
} from '@/types';

// Stable API URL rules:
// - Local development always uses local backend by default.
// - Production always uses one backend URL (env override allowed).

const LOCAL_API_URL = 'http://localhost:8000/api/';
const PRODUCTION_API_URL = 'https://pie-global-funitures.onrender.com/api/';

const getApiUrl = (): string => {
  const envUrl = import.meta.env.VITE_API_URL;

  if (import.meta.env.DEV) {
    // In local dev, avoid accidentally sending account actions to production.
    const forceRemoteApi = String(import.meta.env.VITE_FORCE_REMOTE_API || '').toLowerCase() === 'true';
    if (!forceRemoteApi) {
      return LOCAL_API_URL;
    }
  }

  if (envUrl && typeof envUrl === 'string' && envUrl.trim()) {
    return envUrl;
  }

  return import.meta.env.PROD ? PRODUCTION_API_URL : LOCAL_API_URL;
};

const API_BASE_URL = getApiUrl();

// Log API URL in development for debugging (helps troubleshoot env var issues)
if (import.meta.env.DEV) {
  console.debug(
    '[API Configuration] Using API URL:',
    API_BASE_URL,
    'from env:',
    import.meta.env.VITE_API_URL || '(not set, using fallback)'
  );
}

// Validate API URL to prevent SSRF attacks
const isValidApiUrl = (url: string): boolean => {
  try {
    // Allow relative paths (used with Vercel rewrites)
    if (url.startsWith('/')) return true;
    const parsedUrl = new URL(url);
    // Only allow http and https protocols
    return ['http:', 'https:'].includes(parsedUrl.protocol);
  } catch {
    return false;
  }
};

if (!isValidApiUrl(API_BASE_URL)) {
  throw new Error(
    `[API Configuration Error] Invalid API URL: "${API_BASE_URL}". ` +
    `Check VITE_API_URL environment variable.`
  );
}

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000, // Increased timeout for better UX
  // CRITICAL for CORS: Allow credentials when calling cross-origin backend
  // Must match CORS_ALLOW_CREDENTIALS = True on Django backend
  withCredentials: true,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add CSRF token if available (for session-based auth)
    // Prefer cookie 'csrftoken' (Django default); fallback to meta tag
    const getCookie = (name: string): string | null => {
      if (typeof document === 'undefined') return null;
      const cookies = document.cookie.split(';').map((c) => c.trim());
      for (const c of cookies) {
        if (c.startsWith(name + '=')) {
          return decodeURIComponent(c.substring(name.length + 1));
        }
      }
      return null;
    };

    const csrfCookie = getCookie('csrftoken');
    const csrfMeta = document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]')?.content;
    const csrfToken = csrfCookie || csrfMeta;
    if (csrfToken) {
      (config.headers as any)['X-CSRFToken'] = csrfToken;
    }

    if (typeof window !== 'undefined') {
      const accessToken = localStorage.getItem('pgf-auth-access');
      if (accessToken) {
        (config.headers as any).Authorization = `Bearer ${accessToken}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor with improved error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Don't log sensitive error details in production
    if (import.meta.env.DEV) {
      if (error.response) {
        console.error('API Error:', error.response.status, error.response.data);
      } else if (error.request) {
        console.error('Network Error:', error.message);
      }
    }
    
    // Sanitize error messages before throwing
    if (error.response?.status === 429) {
      return Promise.reject(new Error('Too many requests. Please try again later.'));
    }
    
    return Promise.reject(error);
  }
);

// Products API
export const productsApi = {
  getAll: async (params?: Record<string, any>) => {
    // AGGRESSIVE cache-busting: Add timestamp + random value to force fresh data
    const cacheBuster = `${Date.now()}-${Math.random()}`;
    const allParams = { ...params, _cache: cacheBuster };
    console.debug('[ProductsAPI] Fetching with cache buster:', cacheBuster);
    const response = await api.get<PaginatedResponse<Product> | Product[]>('/products/', { params: allParams });
    console.debug('[ProductsAPI] Received products:', Array.isArray(response.data) ? response.data.length : response.data.results?.length);
    return response.data;
  },

  getBySlug: async (slug: string) => {
    const response = await api.get<Product>(`/products/${slug}/`);
    return response.data;
  },

  getFeatured: async () => {
    const response = await api.get<Product[]>('/products/featured/');
    return response.data;
  },

  getOnSale: async () => {
    const response = await api.get<Product[]>('/products/on_sale/');
    return response.data;
  },

  getByCategory: async () => {
    const response = await api.get<Record<string, Product[]>>('/products/by_category/');
    return response.data;
  },
};

// Orders API
export const ordersApi = {
  create: async (order: Order) => {
    const response = await api.post<{ message: string; order: Order }>('/orders/', order);
    return response.data;
  },
};

// Home API
export const homeApi = {
  getSliders: async () => {
    const response = await api.get<SliderImage[]>('/sliders/');
    return response.data;
  },

  getVideos: async () => {
    const response = await api.get<HomeVideo[]>('/videos/');
    return response.data;
  },
};

// Messages API
export const messagesApi = {
  create: async (message: ContactMessage) => {
    const response = await api.post<{ message: string; data: ContactMessage }>('/messages/', message);
    return response.data;
  },
};

// About API
export const aboutApi = {
  get: async () => {
    try {
      const response = await api.get<AboutPage>('/about/current/');
      return response.data;
    } catch (error) {
      // Fallback to list endpoint (sorted by backend ordering)
      const response = await api.get<AboutPage[]>('/about/');
      return response.data[0];
    }
  },
};

export const csrfApi = {
  bootstrap: async () => {
    await api.get('/csrf/');
  },
};

// Auth API (session-based)
export const authApi = {
  register: async (payload: { name: string; email: string; password: string; password_confirm: string }) => {
    const response = await api.post<AuthResponse>('/users/register/', payload);
    return response.data;
  },
  login: async (payload: { email: string; password: string }) => {
    const response = await api.post<AuthResponse>('/users/login/', payload);
    return response.data;
  },
  logout: async () => {
    const response = await api.post<AuthResponse>('/users/logout/');
    return response.data;
  },
  me: async () => {
    const response = await api.get<AuthResponse>('/users/me/');
    return response.data;
  },
  refresh: async (payload: { refresh: string }) => {
    const response = await api.post<AuthResponse>('/users/refresh/', payload);
    return response.data;
  },
};

// Admin Dashboard API
export const adminApi = {
  getDashboardSummary: async () => {
    const response = await api.get<DashboardSummary>('/admin/dashboard/summary/');
    return response.data;
  },

  getAlerts: async () => {
    const response = await api.get<DashboardAlert[]>('/admin/dashboard/alerts/');
    return response.data;
  },

  getRecentOrders: async (limit: number = 10, status?: string) => {
    const params: Record<string, any> = { limit };
    if (status) params.status = status;
    const response = await api.get<AdminOrder[]>('/admin/dashboard/recent_orders/', { params });
    return response.data;
  },

  getRecentMessages: async (limit: number = 10, status?: string) => {
    const params: Record<string, any> = { limit };
    if (status) params.status = status;
    const response = await api.get<AdminMessage[]>('/admin/dashboard/recent_messages/', { params });
    return response.data;
  },

  updateOrderStatus: async (orderId: number, status: string, notes?: string) => {
    const payload: any = { status };
    if (notes) payload.notes = notes;
    const response = await api.post<{ message: string; order: AdminOrder }>(
      `/admin/dashboard/orders/${orderId}/status/`,
      payload
    );
    return response.data;
  },

  markOrderPaid: async (orderId: number) => {
    const response = await api.post<{ message: string; order: AdminOrder }>(
      `/admin/dashboard/orders/${orderId}/mark-paid/`
    );
    return response.data;
  },

  replyToMessage: async (messageId: number, replyText: string, status?: string) => {
    const payload: any = { reply_text: replyText };
    if (status) payload.status = status;
    const response = await api.post<{ message: string; data: AdminMessage }>(
      `/admin/dashboard/messages/${messageId}/reply/`,
      payload
    );
    return response.data;
  },

  resolveMessage: async (messageId: number) => {
    const response = await api.post<{ message: string; data: AdminMessage }>(
      `/admin/dashboard/messages/${messageId}/resolve/`
    );
    return response.data;
  },

  getAuditLogs: async (limit: number = 50) => {
    const response = await api.get<any[]>('/admin/dashboard/audit_logs/', {
      params: { limit }
    });
    return response.data;
  },

  getTopProducts: async (limit: number = 10) => {
    const response = await api.get<any[]>('/admin/dashboard/top-products/', {
      params: { limit }
    });
    return response.data;
  },

  getProducts: async (page: number = 1, limit: number = 20, search?: string, category?: string) => {
    const params: Record<string, any> = { page, limit };
    if (search) params.search = search;
    if (category) params.category = category;
    const response = await api.get<any>('/admin/dashboard/products/', { params });
    return response.data;
  },

  createProduct: async (data: any) => {
    const formData = new FormData();
    
    // Add all fields to form data
    for (const [key, value] of Object.entries(data)) {
      if (key === 'main_image' && value instanceof File) {
        formData.append(key, value);
      } else if (key === 'gallery' && Array.isArray(value)) {
        value.forEach((item: any, index: number) => {
          if (item instanceof File) {
            formData.append(`gallery_${index}`, item);
          }
        });
      } else if (value !== null && value !== undefined && !(value instanceof File)) {
        if (typeof value === 'object') {
          formData.append(key, JSON.stringify(value));
        } else {
          formData.append(key, String(value));
        }
      }
    }
    
    const response = await api.post<any>('/admin/dashboard/products/', formData, {
    });
    return response.data;
  },

  updateProduct: async (productId: number, data: any) => {
    const formData = new FormData();
    
    // Add all fields to form data
    for (const [key, value] of Object.entries(data)) {
      if (key === 'main_image' && value instanceof File) {
        formData.append(key, value);
      } else if (key === 'gallery' && Array.isArray(value)) {
        value.forEach((item: any, index: number) => {
          if (item instanceof File) {
            formData.append(`gallery_${index}`, item);
          }
        });
      } else if (value !== null && value !== undefined && !(value instanceof File)) {
        if (typeof value === 'object') {
          formData.append(key, JSON.stringify(value));
        } else {
          formData.append(key, String(value));
        }
      }
    }
    
    const response = await api.patch<any>(`/admin/dashboard/products/${productId}/`, formData, {
    });
    return response.data;
  },

  deleteProduct: async (productId: number) => {
    const response = await api.delete<any>(`/admin/dashboard/products/${productId}/`);
    return response.data;
  },
};

// Cart API
export const cartApi = {
  getCart: async () => {
    const response = await api.get<CartResponse>('/cart/');
    return response.data;
  },
  addToCart: async (productId: number, quantity: number = 1) => {
    const response = await api.post<any>('/cart/add/', { product_id: productId, quantity });
    return response.data;
  },
  updateItem: async (itemId: number, quantity: number) => {
    const response = await api.patch<any>(`/cart/item/${itemId}/`, { quantity });
    return response.data;
  },
  removeItem: async (itemId: number) => {
    const response = await api.delete<any>(`/cart/item/${itemId}/`);
    return response.data;
  },
  mergeGuestCart: async (items: Array<{ product_id: number; quantity: number }>) => {
    const response = await api.post<CartResponse>('/cart/merge/', { items });
    return response.data;
  },
};

// Export API_URL for use in manual fetch calls (like in auth components)
// This removes the /api/ suffix to get the base backend URL for auth endpoints
export const API_URL = API_BASE_URL.endsWith('/api/') 
  ? API_BASE_URL.slice(0, -5)  // Remove '/api/' (5 characters)
  : API_BASE_URL;

export default api;
