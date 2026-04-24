import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { memo, useRef, useEffect, useMemo, useState } from 'react';
import { getImageUrl, getVideoUrl } from '@/utils/imageUrl';
import type { HomeVideo, SliderImage } from '@/types';

interface HeroVideoProps {
  video?: HomeVideo;
  slider?: SliderImage;
}

const HeroVideo = memo(({ video, slider }: HeroVideoProps) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [videoFailed, setVideoFailed] = useState(false);
  const videoUrl = video?.video ? getVideoUrl(video.video) : '';
  const fallbackImageUrl = slider?.image ? getImageUrl(slider.image) : '';

  const particles = useMemo(() => {
    const width = typeof window !== 'undefined' ? window.innerWidth : 1440;
    const height = typeof window !== 'undefined' ? window.innerHeight : 900;
    return [...Array(8)].map((_, i) => ({
      id: i,
      initialX: Math.random() * width,
      initialY: Math.random() * height,
      animateX: Math.random() * width,
      animateY: Math.random() * height,
      duration: 15 + Math.random() * 20,
    }));
  }, []);

  const getVideoMimeType = (url: string) => {
    const cleanUrl = url.toLowerCase().split('?')[0];
    if (cleanUrl.endsWith('.webm')) return 'video/webm';
    if (cleanUrl.endsWith('.mov')) return 'video/quicktime';
    return 'video/mp4';
  };

  useEffect(() => {
    const playVideo = async () => {
      if (!videoRef.current || !videoUrl || videoFailed) return;
      try {
        videoRef.current.muted = true;
        videoRef.current.defaultMuted = true;
        await videoRef.current.play();
      } catch {
        setTimeout(() => {
          videoRef.current?.play().catch(() => {});
        }, 300);
      }
    };

    playVideo();
    document.addEventListener('visibilitychange', playVideo);
    return () => document.removeEventListener('visibilitychange', playVideo);
  }, [videoUrl, videoFailed]);

  return (
    <section className="relative h-[90vh] min-h-[600px] w-full overflow-hidden">
      {/* Background Media */}
      {fallbackImageUrl ? (
        <img
          src={fallbackImageUrl}
          alt={slider?.title || 'Hero background'}
          className="absolute inset-0 z-0 w-full h-full object-cover"
          loading="eager"
          fetchPriority="high"
          onError={(e) => console.error('Slider fallback image failed to load:', slider?.image, e)}
        />
      ) : (
        <div className="absolute inset-0 z-0 bg-gradient-to-br from-primary-600 via-primary-700 to-secondary-600" />
      )}

      {videoUrl && !videoFailed && (
        <video
          ref={videoRef}
          autoPlay
          loop
          muted
          playsInline
          preload="auto"
          poster={fallbackImageUrl || undefined}
          disablePictureInPicture
          disableRemotePlayback
          className="absolute inset-0 z-[1] w-full h-full object-cover pointer-events-none"
          style={{
            willChange: 'transform',
            backfaceVisibility: 'hidden',
            WebkitBackfaceVisibility: 'hidden',
          }}
          onCanPlay={() => {
            videoRef.current?.play().catch(() => {});
          }}
          onError={(e) => {
            console.error('Video error:', e);
            console.error('Video src:', video?.video);
            console.error('Attempted URL:', videoUrl);
            setVideoFailed(true);
          }}
        >
          <source src={videoUrl} type={getVideoMimeType(videoUrl)} />
        </video>
      )}

      {/* Overlay */}
      <div className="absolute inset-0 z-[2] bg-gradient-to-b from-black/50 via-black/30 to-black/60" />

      {/* Animated Particles Background - Reduced for performance */}
      <div className="absolute inset-0 z-[3] opacity-10">
        {particles.map((particle) => (
          <motion.div
            key={particle.id}
            className="absolute w-1.5 h-1.5 bg-white rounded-full"
            initial={{
              x: particle.initialX,
              y: particle.initialY,
            }}
            animate={{
              y: [null, particle.animateY],
              x: [null, particle.animateX],
            }}
            transition={{
              duration: particle.duration,
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
