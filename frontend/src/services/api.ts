import axios, { AxiosError } from 'axios';
import type {
  Product,
  Order,
  SliderImage,
  HomeVideo,
  ContactMessage,
  AboutPage,
  PaginatedResponse,
} from '@/types';

// CRITICAL: API URL configuration with explicit fallback hierarchy
// Priority: 1. import.meta.env.VITE_API_URL (set at build time by Vite/Vercel)
//           2. Browser localhost detection (for local development)
//           3. Hardcoded production URL (final fallback)

const getApiUrl = (): string => {
  // Priority 1: Use build-time environment variable (VITE_API_URL)
  // This is set from:
  // - .env file (local dev)
  // - Vercel Environment Variables (production)
  // - vite.config.ts define option (as fallback)
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl && typeof envUrl === 'string' && envUrl.trim()) {
    return envUrl;
  }

  // Priority 2: Check if we're in browser and detect local environment
  if (typeof window !== 'undefined') {
    const isLocal =
      window.location.hostname === 'localhost' ||
      window.location.hostname === '127.0.0.1' ||
      window.location.hostname.startsWith('192.168.') ||
      window.location.hostname.startsWith('10.');

    if (isLocal) {
      return 'http://localhost:8000/api/';
    }
  }

  // Priority 3: Production fallback (only if env var not set and not localhost)
  // This assumes Render backend is always available in production
  return 'https://pie-global-funitures.onrender.com/api/';
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
  headers: {
    'Content-Type': 'application/json',
  },
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

// Auth API (session-based)
export const authApi = {
  register: async (payload: { name: string; email: string; password: string; password_confirm: string }) => {
    const response = await api.post('/auth/users/register/', payload);
    return response.data;
  },
  login: async (payload: { email: string; password: string }) => {
    const response = await api.post('/auth/users/login/', payload);
    return response.data;
  },
  logout: async () => {
    const response = await api.post('/auth/users/logout/');
    return response.data;
  },
  me: async () => {
    const response = await api.get('/auth/users/me/');
    return response.data;
  },
};

// Export API_URL for use in manual fetch calls (like in auth components)
// This removes the /api/ suffix to get the base backend URL for auth endpoints
export const API_URL = API_BASE_URL.endsWith('/api/') 
  ? API_BASE_URL.slice(0, -5)  // Remove '/api/' (5 characters)
  : API_BASE_URL;

export default api;
