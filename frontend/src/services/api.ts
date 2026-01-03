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

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Validate API URL to prevent SSRF attacks
const isValidApiUrl = (url: string): boolean => {
  try {
    const parsedUrl = new URL(url);
    // Only allow http and https protocols
    return ['http:', 'https:'].includes(parsedUrl.protocol);
  } catch {
    return false;
  }
};

if (!isValidApiUrl(API_BASE_URL)) {
  throw new Error('Invalid API URL configuration');
}

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000, // Increased timeout for better UX
  headers: {
    'Content-Type': 'application/json',
  },
  // Security: Prevent credentials from being sent to untrusted origins
  withCredentials: false,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add CSRF token if available (for session-based auth)
    const csrfToken = document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]')?.content;
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
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
    const response = await api.get<PaginatedResponse<Product>>('/products/', { params });
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
    const response = await api.get<AboutPage[]>('/about/');
    return response.data[0]; // Assuming single about page
  },
};

export default api;
