import { useState, useEffect } from 'react';
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

  useEffect(() => {
    if (images.length <= 1 || !autoplay) return;

    const interval = setInterval(() => {
      setDirection(1);
      setCurrentIndex((prev) => (prev + 1) % images.length);
    }, 6000);

    return () => clearInterval(interval);
  }, [images.length, autoplay]);

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
      const next = prev + newDirection;
      if (next < 0) return images.length - 1;
      if (next >= images.length) return 0;
      return next;
    });
    setAutoplay(true);
  };

  if (images.length === 0) return null;

  const currentImage = images[currentIndex];
  if (!currentImage) return null;

  return (
    <section 
      className="relative w-full h-[22vh] sm:h-[25vh] md:h-[28vh] lg:h-[30vh] bg-gradient-to-b from-gray-50 to-gray-100 overflow-hidden flex items-center justify-center"
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
            <img
              src={getImageUrl(currentImage.image)}
              alt="Gallery"
              className="w-full h-full object-cover"
              loading="eager"
              decoding="async"
              sizes="100vw"
              crossOrigin="anonymous"
              onError={() => {
                console.error('Image failed to load:', currentImage.image);
              }}
            />
          ) : (
            <div className="w-full h-full bg-gray-200" />
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
