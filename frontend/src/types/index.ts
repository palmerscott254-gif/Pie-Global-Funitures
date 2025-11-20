// Product types
export interface Product {
  id: number;
  name: string;
  slug: string;
  description: string;
  short_description: string;
  price: string;
  compare_at_price: string | null;
  category: string;
  tags: string[] | null;
  main_image: string;
  gallery: string[] | null;
  stock: number;
  sku: string | null;
  dimensions: string;
  material: string;
  color: string;
  weight: string;
  featured: boolean;
  is_active: boolean;
  on_sale: boolean;
  meta_title: string;
  meta_description: string;
  in_stock: boolean;
  discount_percentage: number;
  created_at: string;
  updated_at: string;
}

// Order types
export interface OrderItem {
  product_id: number;
  name: string;
  price: number;
  qty: number;
  image?: string;
}

export interface Order {
  id?: number;
  name: string;
  email?: string;
  phone: string;
  address: string;
  city?: string;
  postal_code?: string;
  items: OrderItem[];
  total_amount: string;
  status?: string;
  paid?: boolean;
  payment_method?: string;
  notes?: string;
  created_at?: string;
  updated_at?: string;
}

// Home slider types
export interface SliderImage {
  id: number;
  title: string;
  image: string;
  order: number;
  active: boolean;
  uploaded_at: string;
}

export interface HomeVideo {
  id: number;
  title: string;
  video: string;
  active: boolean;
  uploaded_at: string;
}

// Contact message types
export interface ContactMessage {
  id?: number;
  name: string;
  email?: string;
  phone?: string;
  message: string;
  replied?: boolean;
  reply_text?: string;
  created_at?: string;
}

// About page types
export interface AboutPage {
  id: number;
  headline: string;
  body: string;
  mission: string;
  vision: string;
  updated_at: string;
}

// Cart item (frontend only)
export interface CartItem {
  id: number;
  name: string;
  price: number;
  quantity: number;
  image: string;
  slug: string;
}

// API response types
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  detail?: string;
  [key: string]: any;
}

// Category choices
export const CATEGORIES = [
  { value: 'sofa', label: 'Sofa' },
  { value: 'bed', label: 'Bed' },
  { value: 'table', label: 'Table' },
  { value: 'wardrobe', label: 'Wardrobe' },
  { value: 'office', label: 'Office Furniture' },
  { value: 'dining', label: 'Dining' },
  { value: 'outdoor', label: 'Outdoor' },
  { value: 'storage', label: 'Storage' },
  { value: 'other', label: 'Other' },
] as const;

export type CategoryValue = typeof CATEGORIES[number]['value'];
