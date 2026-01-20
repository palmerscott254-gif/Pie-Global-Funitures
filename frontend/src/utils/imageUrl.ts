/**
 * Centralized media URL handling for frontend
 * Handles both S3 and backend-served media
 * 
 * IMPORTANT: Backend serializers now return absolute URLs in production,
 * so the frontend should trust those URLs instead of reconstructing them.
 */

/**
 * Get image URL with proper fallback handling
 * 
 * @param url - Image URL from backend (absolute or relative)
 * @returns Absolute image URL or placeholder
 */
export const getImageUrl = (url: string | null | undefined): string => {
  if (!url) {
    return '/placeholder-product.jpg'; // Fallback placeholder
  }

  // Backend sends absolute URLs in production (S3 or backend-served)
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }

  // Development fallback: prepend backend URL for relative paths
  const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
  const baseUrl = backendUrl.replace('/api', '').replace(/\/$/, '');
  
  const normalizedUrl = url.startsWith('/') ? url : `/${url}`;
  return `${baseUrl}${normalizedUrl}`;
};

/**
 * Get video URL with proper fallback handling
 * 
 * @param url - Video URL from backend (absolute or relative)
 * @returns Absolute video URL or empty string
 */
export const getVideoUrl = (url: string | null | undefined): string => {
  if (!url) {
    console.warn('[VideoUrl] Video URL is null or undefined');
    return ''; // Empty string prevents video element errors
  }

  // Backend sends absolute URLs in production (S3 or backend-served)
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }

  // Development fallback: prepend backend URL for relative paths
  const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
  const baseUrl = backendUrl.replace('/api', '').replace(/\/$/, '');
  
  const normalizedUrl = url.startsWith('/') ? url : `/${url}`;
  return `${baseUrl}${normalizedUrl}`;
};

/**
 * Get placeholder image URL
 */
export const getPlaceholderImageUrl = (): string => {
  return '/placeholder-product.jpg';
};
