import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaChevronLeft, FaChevronRight } from 'react-icons/fa';
import { getImageUrl } from '@/utils/imageUrl';
import type { SliderImage } from '@/types';

interface SliderProps {
  images: SliderImage[];
}

/**
 * Premium horizontal strip-style image slider
 * - Compact height (25-30% viewport)
 * - Full width, edge-to-edge images
 * - Clean, minimal design with no text overlays
 * - Smooth horizontal scrolling with subtle controls
 * - Mobile-first optimized
 */
const Slider = ({ images }: SliderProps) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [direction, setDirection] = useState(0);
  const [autoplay, setAutoplay] = useState(true);
  const [broken, setBroken] = useState<Set<number>>(new Set());
  const brokenRef = useRef(broken);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [wrapperHeight, setWrapperHeight] = useState<number | null>(null);
  const [currentAspect, setCurrentAspect] = useState<number | null>(null);

  useEffect(() => {
    if (images.length <= 1 || !autoplay) return;

    const interval = setInterval(() => {
      setDirection(1);
      setCurrentIndex((prev) => (prev + 1) % images.length);
    }, 6000);

    return () => clearInterval(interval);
  }, [images.length, autoplay]);

  // Keep ref in sync for handlers
  useEffect(() => {
    brokenRef.current = broken;
  }, [broken]);

  // Reset broken cache when images change
  useEffect(() => {
    setBroken(new Set());
    setCurrentIndex(0);
  }, [images]);

  const getMaxVhPx = () => {
    const w = typeof window !== 'undefined' ? window.innerWidth : 1280;
    const h = typeof window !== 'undefined' ? window.innerHeight : 800;
    if (w >= 1024) return h * 0.3; // lg
    if (w >= 768) return h * 0.28; // md
    if (w >= 640) return h * 0.25; // sm
    return h * 0.22; // base
  };

  const getMinHeightPx = () => {
    const w = typeof window !== 'undefined' ? window.innerWidth : 1280;
    if (w >= 1024) return 360;
    if (w >= 768) return 320;
    if (w >= 640) return 280;
    return 240;
  };

  const recomputeHeight = (aspect?: number | null) => {
    const a = aspect ?? currentAspect;
    if (!a || !containerRef.current) return;
    const containerWidth = containerRef.current.clientWidth || window.innerWidth;
    const maxH = getMaxVhPx();
    const desired = Math.min(containerWidth * a, maxH);
    setWrapperHeight(Math.round(Math.max(desired, getMinHeightPx())));
  };

  useEffect(() => {
    const onResize = () => recomputeHeight();
    window.addEventListener('resize', onResize);
    return () => window.removeEventListener('resize', onResize);
  }, [currentAspect]);

  const getNextValidIndex = (start: number, dir: number) => {
    if (images.length === 0) return -1;
    for (let i = 0; i < images.length; i++) {
      const candidate = (start + (dir > 0 ? i : -i) + images.length) % images.length;
      if (!brokenRef.current.has(candidate)) return candidate;
    }
    return -1;
  };

  const slideVariants = {
    enter: (direction: number) => ({
      x: direction > 0 ? 1000 : -1000,
      opacity: 0,
    }),
    center: {
      zIndex: 1,
      x: 0,
      opacity: 1,
    },
    exit: (direction: number) => ({
      zIndex: 0,
      x: direction < 0 ? 1000 : -1000,
      opacity: 0,
    }),
  };

  const swipeConfidenceThreshold = 10000;
  const swipePower = (offset: number, velocity: number) => {
    return Math.abs(offset) * velocity;
  };

  const paginate = (newDirection: number) => {
    setDirection(newDirection);
    setCurrentIndex((prev) => {
      const next = getNextValidIndex((prev + newDirection + images.length) % images.length, newDirection);
      if (next >= 0) return next;
      return prev;
    });
    setAutoplay(true);
  };

  if (images.length === 0) return null;

  const currentImage = images[currentIndex];
  if (!currentImage) return null;

  return (
    <section 
      className="relative w-full h-[22vh] sm:h-[25vh] md:h-[28vh] lg:h-[30vh] min-h-[240px] sm:min-h-[280px] md:min-h-[320px] lg:min-h-[360px] bg-gradient-to-b from-gray-50 to-gray-100 overflow-hidden flex items-center justify-center"
      onMouseEnter={() => setAutoplay(false)}
      onMouseLeave={() => setAutoplay(true)}
    >
      {/* Image Container */}
      <AnimatePresence initial={false} custom={direction}>
        <motion.div
          key={currentIndex}
          custom={direction}
          variants={slideVariants}
          initial="enter"
          animate="center"
          exit="exit"
          transition={{
            x: { type: 'spring', stiffness: 300, damping: 30 },
            opacity: { duration: 0.3 },
          }}
          drag="x"
          dragConstraints={{ left: 0, right: 0 }}
          dragElastic={0.2}
          onDragEnd={(_, { offset, velocity }) => {
            const swipe = swipePower(offset.x, velocity.x);
            if (swipe < -swipeConfidenceThreshold) {
              paginate(1);
            } else if (swipe > swipeConfidenceThreshold) {
              paginate(-1);
            }
          }}
          className="absolute inset-0 cursor-grab active:cursor-grabbing flex items-center justify-center"
        >
          {currentImage.image ? (
            <div ref={containerRef} className="w-full h-full flex items-center justify-center px-4 sm:px-6" style={{ height: wrapperHeight ? `${wrapperHeight}px` : '100%', transition: 'height 240ms ease' }}>
              <img
                src={getImageUrl(currentImage.image)}
                alt={currentImage.title || 'Gallery'}
                className="max-w-full max-h-full object-contain object-center"
                loading="eager"
                decoding="async"
                sizes="100vw"
                crossOrigin="anonymous"
                onLoad={(e) => {
                  try {
                    const img = e.currentTarget as HTMLImageElement;
                    const aspect = img.naturalHeight / img.naturalWidth;
                    setCurrentAspect(aspect);
                    recomputeHeight(aspect);
                  } catch (err) {
                    console.error('Error computing image aspect', err);
                  }
                }}
                onError={() => {
                  console.error('Image failed to load:', currentImage.image);
                  setBroken((s) => {
                    const n = new Set(s);
                    n.add(currentIndex);
                    return n;
                  });
                  const next = getNextValidIndex(currentIndex, 1);
                  if (next >= 0) setCurrentIndex(next);
                }}
              />
            </div>
          ) : (
            <div className="w-full h-full bg-gray-200 flex items-center justify-center">
              <div className="text-gray-500">Image unavailable</div>
            </div>
          )}
        </motion.div>
      </AnimatePresence>

      {/* Subtle Navigation Arrows */}
      {images.length > 1 && (
        <>
          {/* Left Arrow */}
          <motion.button
            onClick={() => paginate(-1)}
            className="absolute left-0 top-1/2 transform -translate-y-1/2 z-20 px-3 py-2 text-gray-700 hover:text-gray-900 transition-colors duration-200 group"
            aria-label="Previous"
            whileHover={{ x: -2 }}
            whileTap={{ scale: 0.95 }}
          >
            <FaChevronLeft className="text-xl sm:text-2xl opacity-60 group-hover:opacity-100 transition-opacity" />
          </motion.button>

          {/* Right Arrow */}
          <motion.button
            onClick={() => paginate(1)}
            className="absolute right-0 top-1/2 transform -translate-y-1/2 z-20 px-3 py-2 text-gray-700 hover:text-gray-900 transition-colors duration-200 group"
            aria-label="Next"
            whileHover={{ x: 2 }}
            whileTap={{ scale: 0.95 }}
          >
            <FaChevronRight className="text-xl sm:text-2xl opacity-60 group-hover:opacity-100 transition-opacity" />
          </motion.button>
        </>
      )}

      {/* Minimal Progress Dots */}
      {images.length > 1 && (
        <div className="absolute bottom-3 left-1/2 transform -translate-x-1/2 z-10 flex gap-1.5 sm:gap-2">
          {images.map((_, index) => (
            <motion.button
              key={index}
              onClick={() => {
                setDirection(index > currentIndex ? 1 : -1);
                setCurrentIndex(index);
                setAutoplay(true);
              }}
              className="transition-all duration-300"
              whileHover={{ scale: 1.2 }}
              whileTap={{ scale: 0.9 }}
              aria-label={`Go to slide ${index + 1}`}
            >
              <div
                className={`rounded-full transition-all duration-300 ${
                  index === currentIndex
                    ? 'h-1.5 w-4 sm:h-2 sm:w-5 bg-gray-800'
                    : 'h-1.5 w-1.5 sm:h-2 sm:w-2 bg-gray-400 hover:bg-gray-600'
                }`}
              />
            </motion.button>
          ))}
        </div>
      )}
    </section>
  );
};

export default Slider;
