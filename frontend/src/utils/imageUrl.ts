/**
 * Utility function to ensure media URLs are absolute and properly formatted
 */
export const getImageUrl = (url: string | null | undefined): string => {
  if (!url) {
    return '/placeholder-product.jpg'; // Fallback placeholder
  }

  // If already absolute URL, return as-is
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }

  // If backend sent a local /media path, rewrite to S3 bucket directly
  if (url.startsWith('/media/') || url.startsWith('media/')) {
    const s3Base = import.meta.env.VITE_S3_BASE_URL || 'https://pieglobal.s3.amazonaws.com';
    const normalized = url.replace(/^\/?media\//, '');
    return `${s3Base}/${normalized}`;
  }

  // If relative URL, prepend the backend URL
  const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
  const baseUrl = backendUrl.replace('/api', ''); // Remove /api suffix if present
  
  // Ensure URL starts with /
  const normalizedUrl = url.startsWith('/') ? url : `/${url}`;
  
  return `${baseUrl}${normalizedUrl}`;
};

/**
 * Utility function to ensure video URLs are absolute and properly formatted
 */
export const getVideoUrl = (url: string | null | undefined): string => {
  if (!url) {
    console.warn('Video URL is null or undefined');
    return ''; // Return empty string instead of null to prevent video element errors
  }

  // If already absolute URL, return as-is
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return url;
  }

  // If backend sent a local /media path, rewrite to S3 bucket directly
  if (url.startsWith('/media/') || url.startsWith('media/')) {
    const s3Base = import.meta.env.VITE_S3_BASE_URL || 'https://pieglobal.s3.amazonaws.com';
    const normalized = url.replace(/^\/?media\//, '');
    const fullUrl = `${s3Base}/${normalized}`;
    console.log('Video URL rewritten to S3:', fullUrl);
    return fullUrl;
  }

  // If relative URL, prepend the backend URL
  const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
  const baseUrl = backendUrl.replace('/api', ''); // Remove /api suffix if present
  
  // Ensure URL starts with /
  const normalizedUrl = url.startsWith('/') ? url : `/${url}`;
  
  const fullUrl = `${baseUrl}${normalizedUrl}`;
  console.log('Video URL constructed:', fullUrl);
  return fullUrl;
};
