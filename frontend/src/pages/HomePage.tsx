import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { homeApi, productsApi, aboutApi } from '@/services/api';
import type { SliderImage, Product, HomeVideo, AboutPage } from '@/types';
import HeroVideo from '@/components/home/HeroVideo';
import Slider from '@/components/home/Slider';
import FeaturedProducts from '@/components/home/FeaturedProducts';
import LocationSection from '@/components/home/LocationSection';
import CallToAction from '@/components/home/CallToAction';
import LoadingSpinner from '@/components/common/LoadingSpinner';

const HomePage = () => {
  const [sliders, setSliders] = useState<SliderImage[]>([]);
  const [videos, setVideos] = useState<HomeVideo[]>([]);
  const [featuredProducts, setFeaturedProducts] = useState<Product[]>([]);
  const [about, setAbout] = useState<AboutPage | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [slidersResponse, videosResponse, productsData, aboutData] = await Promise.all([
          homeApi.getSliders(),
          homeApi.getVideos(),
          productsApi.getFeatured(),
          aboutApi.get().catch(() => null),
        ]);
        
        // Handle paginated or array response for sliders
        const slidersData = Array.isArray(slidersResponse) 
          ? slidersResponse 
          : (slidersResponse as any).results || [];
        
        // Handle paginated or array response for videos
        const videosData = Array.isArray(videosResponse) 
          ? videosResponse 
          : (videosResponse as any).results || [];
        
        // Handle paginated or array response for products
        const products = Array.isArray(productsData) 
          ? productsData 
          : (productsData as any).results || [];
        
        setSliders(slidersData);
        setVideos(videosData);
        setFeaturedProducts(products);
        setAbout(aboutData);
      } catch (error) {
        console.error('Error fetching homepage data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  return (
    <div className="overflow-hidden">
      {/* Hero Video or Slider with Premium Component */}
      {videos.length > 0 ? (
        <HeroVideo video={videos[0]} />
      ) : sliders.length > 1 ? (
        <Slider sliders={sliders} />
      ) : sliders.length === 1 ? (
        <HeroVideo slider={sliders[0]} />
      ) : (
        <HeroVideo />
      )}

      {/* Featured Products Section */}
      <FeaturedProducts products={featuredProducts} />

      {/* About Section Preview */}
      {about && (
        <motion.section 
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="bg-gradient-to-br from-gray-50 to-gray-100 py-20"
        >
          <div className="container-custom">
            <div className="max-w-4xl mx-auto text-center">
              <motion.h2 
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="text-5xl font-bold mb-6 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent"
              >
                {about.headline || 'About Us'}
              </motion.h2>
              {about.body && (
                <motion.p 
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: 0.3 }}
                  className="text-lg text-gray-700 mb-8 leading-relaxed"
                >
                  {about.body.substring(0, 300)}...
                </motion.p>
              )}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.4 }}
              >
                <Link 
                  to="/about" 
                  className="inline-block bg-gradient-to-r from-primary-600 to-secondary-600 text-white px-8 py-4 rounded-xl font-semibold hover:shadow-lg hover:scale-105 transition-all duration-300"
                >
                  Learn More About Us
                </Link>
              </motion.div>
            </div>
          </div>
        </motion.section>
      )}

      {/* Location Section */}
      <LocationSection />

      {/* Call to Action */}
      <CallToAction />
    </div>
  );
};

export default HomePage;
