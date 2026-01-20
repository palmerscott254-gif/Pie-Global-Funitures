import { useState } from 'react';
import { getImageUrl, getPlaceholderImageUrl } from '@/utils/imageUrl';

interface ImageWithFallbackProps {
  src: string;
  alt: string;
  className?: string;
  fallbackSrc?: string;
  loading?: 'lazy' | 'eager';
}

/**
 * Image component with fallback handling and loading states
 * Optimized for performance with lazy loading support
 */
const ImageWithFallback = ({
  src,
  alt,
  className = '',
  fallbackSrc,
  loading = 'lazy',
}: ImageWithFallbackProps) => {
  const [imgSrc, setImgSrc] = useState(getImageUrl(src));
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  const handleError = () => {
    if (!hasError) {
      setHasError(true);
      // Use provided fallback or default placeholder
      setImgSrc(fallbackSrc || getPlaceholderImageUrl());
    }
  };

  const handleLoad = () => {
    setIsLoading(false);
  };

  return (
    <div className="relative">
      {isLoading && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse flex items-center justify-center">
          <div className="w-8 h-8 border-3 border-gray-400 border-t-transparent rounded-full animate-spin" />
        </div>
      )}
      <img
        src={imgSrc}
        alt={alt}
        className={`${className} ${isLoading ? 'opacity-0' : 'opacity-100 transition-opacity duration-300'}`}
        loading={loading}
        decoding="async"
        onError={handleError}
        onLoad={handleLoad}
      />
    </div>
  );
};

export default ImageWithFallback;
