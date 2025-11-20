import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import type { HomeVideo, SliderImage } from '@/types';

interface HeroVideoProps {
  video?: HomeVideo;
  slider?: SliderImage;
}

const HeroVideo = ({ video, slider }: HeroVideoProps) => {
  return (
    <section className="relative h-[90vh] min-h-[600px] w-full overflow-hidden">
      {/* Background Media */}
      {video ? (
        <video
          src={video.video}
          autoPlay
          loop
          muted
          playsInline
          className="absolute inset-0 w-full h-full object-cover"
        />
      ) : slider ? (
        <img
          src={slider.image}
          alt={slider.title}
          className="absolute inset-0 w-full h-full object-cover"
        />
      ) : (
        <div className="absolute inset-0 bg-gradient-to-br from-primary-600 via-primary-700 to-secondary-600" />
      )}

      {/* Overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-black/30 to-black/60" />

      {/* Animated Particles Background */}
      <div className="absolute inset-0 opacity-20">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-white rounded-full"
            initial={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
            }}
            animate={{
              y: [null, Math.random() * window.innerHeight],
              x: [null, Math.random() * window.innerWidth],
            }}
            transition={{
              duration: 10 + Math.random() * 20,
              repeat: Infinity,
              ease: 'linear',
            }}
          />
        ))}
      </div>

      {/* Hero Content */}
      <div className="relative z-10 h-full flex items-center justify-center">
        <div className="container-custom text-center text-white px-4">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <motion.h1
              className="text-5xl md:text-7xl lg:text-8xl font-bold mb-6 leading-tight"
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, delay: 0.3 }}
            >
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-300">
                Redefine Your Space
              </span>
            </motion.h1>

            <motion.p
              className="text-xl md:text-2xl lg:text-3xl mb-8 text-gray-200 font-light max-w-3xl mx-auto"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, delay: 0.5 }}
            >
              Premium furniture crafted for modern living
            </motion.p>

            <motion.div
              className="flex flex-col sm:flex-row gap-4 justify-center items-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, delay: 0.7 }}
            >
              <Link
                to="/products"
                className="group relative px-8 py-4 bg-white text-primary-600 rounded-full font-semibold text-lg overflow-hidden transition-all duration-300 hover:scale-105 hover:shadow-2xl"
              >
                <span className="relative z-10">Explore Collection</span>
                <div className="absolute inset-0 bg-gradient-to-r from-primary-600 to-secondary-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                <span className="absolute inset-0 flex items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  Explore Collection
                </span>
              </Link>

              <Link
                to="/about"
                className="px-8 py-4 bg-transparent border-2 border-white text-white rounded-full font-semibold text-lg hover:bg-white hover:text-primary-600 transition-all duration-300 hover:scale-105"
              >
                Our Story
              </Link>
            </motion.div>
          </motion.div>

          {/* Scroll Indicator */}
          <motion.div
            className="absolute bottom-10 left-1/2 transform -translate-x-1/2"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              duration: 1,
              delay: 1,
              repeat: Infinity,
              repeatType: 'reverse',
            }}
          >
            <div className="w-6 h-10 border-2 border-white rounded-full flex justify-center">
              <div className="w-1 h-3 bg-white rounded-full mt-2 animate-bounce" />
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default HeroVideo;
