import { useState } from 'react';
import { motion } from 'framer-motion';

interface ImageWithFallbackProps {
  src: string;
  alt: string;
  className?: string;
  fallbackSrc?: string;
  loading?: 'lazy' | 'eager';
}

const ImageWithFallback = ({
  src,
  alt,
  className = '',
  fallbackSrc = '/placeholder-product.jpg',
  loading = 'lazy',
}: ImageWithFallbackProps) => {
  const [imgSrc, setImgSrc] = useState(src);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  const handleError = () => {
    if (!hasError) {
      setHasError(true);
      setImgSrc(fallbackSrc);
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
      <motion.img
        src={imgSrc}
        alt={alt}
        className={className}
        loading={loading}
        decoding="async"
        onError={handleError}
        onLoad={handleLoad}
        initial={{ opacity: 0 }}
        animate={{ opacity: isLoading ? 0 : 1 }}
        transition={{ duration: 0.3 }}
      />
    </div>
  );
};

export default ImageWithFallback;
