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

// Create axios instance with default config
// Timeout increased to 30s to handle Render cold starts
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds for cold start handling
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor with retry logic
let retryCount = 0;
const maxRetries = 1;

api.interceptors.response.use(
  (response) => {
    retryCount = 0; // Reset on success
    return response;
  },
  (error: AxiosError) => {
    if (error.response) {
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      console.error('Network Error:', error.message);
      
      // Retry once on timeout for cold starts
      if (error.code === 'ECONNABORTED' && retryCount < maxRetries) {
        retryCount++;
        console.log(`Retrying request (attempt ${retryCount}/${maxRetries})...`);
        return new Promise((resolve) => {
          setTimeout(() => {
            resolve(api(error.config as any));
          }, 2000); // Wait 2s before retry
        });
      }
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
    const response = await api.get<SliderImage[] | { results: SliderImage[] }>('/sliders/');
    // Handle both array and paginated responses
    const data = Array.isArray(response.data) ? response.data : (response.data as any).results || [];
    return data;
  },

  getVideos: async () => {
    const response = await api.get<HomeVideo[] | { results: HomeVideo[] }>('/videos/');
    // Handle both array and paginated responses
    const data = Array.isArray(response.data) ? response.data : (response.data as any).results || [];
    return data;
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
    const response = await api.get<AboutPage[] | AboutPage | { results: AboutPage[] }>('/about/');
    // Handle different response formats
    if (Array.isArray(response.data)) {
      return response.data[0] || null;
    } else if ((response.data as any).results && Array.isArray((response.data as any).results)) {
      return (response.data as any).results[0] || null;
    } else {
      return (response.data as AboutPage) || null;
    }
  },
};

export default api;
