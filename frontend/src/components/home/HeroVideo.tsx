import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { memo, useRef, useEffect, useState } from 'react';
import { getImageUrl, getVideoUrl } from '@/utils/imageUrl';
import type { HomeVideo, SliderImage } from '@/types';

interface HeroVideoProps {
  video?: HomeVideo;
  slider?: SliderImage;
}

const HeroVideo = memo(({ video, slider }: HeroVideoProps) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const sectionRef = useRef<HTMLElement>(null);
  const [shouldLoadVideo, setShouldLoadVideo] = useState(true); // Default to true to avoid desktop not loading
  const [videoFailed, setVideoFailed] = useState(false);

  useEffect(() => {
    // Defer video loading until hero is in viewport while keeping eager default
    const observer = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        if (entry.isIntersecting) {
          setShouldLoadVideo(true);
        }
      },
      { rootMargin: '0px', threshold: 0.1 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    // Ensure video plays smoothly once loaded and visible
    const playVideo = async () => {
      if (!shouldLoadVideo || !videoRef.current) return;
      try {
        videoRef.current.playbackRate = 1.0;

        if ('connection' in navigator) {
          const conn = (navigator as any).connection;
          if (conn && conn.effectiveType !== '4g') {
            videoRef.current.playbackRate = 1.0;
          }
        }

        await videoRef.current.play();
      } catch (err) {
        setTimeout(() => {
          videoRef.current?.play().catch(() => {});
        }, 800);
      }
    };
    playVideo();
  }, [shouldLoadVideo]);

  return (
    <section ref={sectionRef} className="relative h-[90vh] min-h-[600px] w-full overflow-hidden">
      {/* Background Media */}
      {video && video.video && !videoFailed ? (
        <video
          ref={videoRef}
          src={shouldLoadVideo ? getVideoUrl(video.video) || undefined : undefined}
          autoPlay
          loop
          muted
          playsInline
          preload="metadata"
          crossOrigin="anonymous"
          disablePictureInPicture
          disableRemotePlayback
          className="absolute inset-0 w-full h-full object-cover"
          style={{
            willChange: 'auto',
            backfaceVisibility: 'hidden',
            WebkitBackfaceVisibility: 'hidden',
          }}
          onError={(e) => {
            console.error('Video error:', e);
            console.error('Video src:', video.video);
            console.error('Attempted URL:', getVideoUrl(video.video));
            setVideoFailed(true);
          }}
        />
      ) : slider && slider.image ? (
        <img
          src={getImageUrl(slider.image)}
          alt={slider.title}
          className="absolute inset-0 w-full h-full object-cover"
          loading="eager"
          onError={(e) => console.error('Slider image failed to load:', slider.image, e)}
        />
      ) : (
        <div className="absolute inset-0 bg-gradient-to-br from-primary-600 via-primary-700 to-secondary-600" />
      )}

      {/* Overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-black/30 to-black/60" />

      {/* Animated Particles Background - Reduced for performance */}
      <div className="absolute inset-0 opacity-10">
        {[...Array(8)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1.5 h-1.5 bg-white rounded-full"
            initial={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
            }}
            animate={{
              y: [null, Math.random() * window.innerHeight],
              x: [null, Math.random() * window.innerWidth],
            }}
            transition={{
              duration: 15 + Math.random() * 20,
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
});

HeroVideo.displayName = 'HeroVideo';

export default HeroVideo;
