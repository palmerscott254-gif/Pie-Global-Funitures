import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaChevronLeft, FaChevronRight } from 'react-icons/fa';
import type { SliderImage } from '@/types';

interface SliderProps {
  images: SliderImage[];
}

const Slider = ({ images }: SliderProps) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [direction, setDirection] = useState(0);

  useEffect(() => {
    if (images.length <= 1) return;

    const interval = setInterval(() => {
      setDirection(1);
      setCurrentIndex((prev) => (prev + 1) % images.length);
    }, 5000);

    return () => clearInterval(interval);
  }, [images.length]);

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
  };

  if (images.length === 0) return null;

  return (
    <section className="relative h-[600px] bg-gray-900 overflow-hidden">
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
            opacity: { duration: 0.2 },
          }}
          drag="x"
          dragConstraints={{ left: 0, right: 0 }}
          dragElastic={1}
          onDragEnd={(_, { offset, velocity }) => {
            const swipe = swipePower(offset.x, velocity.x);

            if (swipe < -swipeConfidenceThreshold) {
              paginate(1);
            } else if (swipe > swipeConfidenceThreshold) {
              paginate(-1);
            }
          }}
          className="absolute inset-0"
        >
          <img
            src={images[currentIndex].image}
            alt={images[currentIndex].title}
            className="w-full h-full object-cover"
          />
          
          {/* Gradient Overlay */}
          <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />

          {/* Slide Content */}
          {images[currentIndex].title && (
            <div className="absolute bottom-20 left-0 right-0 text-center">
              <motion.h2
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2, duration: 0.6 }}
                className="text-4xl md:text-6xl font-bold text-white mb-4"
              >
                {images[currentIndex].title}
              </motion.h2>
            </div>
          )}
        </motion.div>
      </AnimatePresence>

      {/* Navigation Arrows */}
      {images.length > 1 && (
        <>
          <button
            onClick={() => paginate(-1)}
            className="absolute left-4 top-1/2 transform -translate-y-1/2 z-10 p-4 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full transition-all duration-300 hover:scale-110 group"
            aria-label="Previous slide"
          >
            <FaChevronLeft className="text-white text-2xl group-hover:text-primary-400 transition-colors" />
          </button>

          <button
            onClick={() => paginate(1)}
            className="absolute right-4 top-1/2 transform -translate-y-1/2 z-10 p-4 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full transition-all duration-300 hover:scale-110 group"
            aria-label="Next slide"
          >
            <FaChevronRight className="text-white text-2xl group-hover:text-primary-400 transition-colors" />
          </button>
        </>
      )}

      {/* Dots Indicator */}
      {images.length > 1 && (
        <div className="absolute bottom-8 left-0 right-0 flex justify-center gap-3 z-10">
          {images.map((_, index) => (
            <button
              key={index}
              onClick={() => {
                setDirection(index > currentIndex ? 1 : -1);
                setCurrentIndex(index);
              }}
              className={`h-2 rounded-full transition-all duration-300 ${
                index === currentIndex
                  ? 'w-12 bg-white'
                  : 'w-2 bg-white/50 hover:bg-white/70'
              }`}
              aria-label={`Go to slide ${index + 1}`}
            />
          ))}
        </div>
      )}
    </section>
  );
};

export default Slider;
