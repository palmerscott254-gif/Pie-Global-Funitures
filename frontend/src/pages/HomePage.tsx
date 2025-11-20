import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { homeApi, productsApi, aboutApi } from '@/services/api';
import type { SliderImage, Product, HomeVideo, AboutPage } from '@/types';

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
        
        console.log('Sliders:', slidersData);
        console.log('Videos:', videosData);
        console.log('Featured Products:', products);
        console.log('About:', aboutData);
        
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
    return (
      <div className="container-custom py-12 text-center">
        <div className="spinner mx-auto"></div>
      </div>
    );
  }

  return (
    <div>
      {/* Hero Video or Slider */}
      {videos.length > 0 ? (
        <section className="relative bg-black">
          <video
            src={videos[0].video}
            autoPlay
            loop
            muted
            playsInline
            className="w-full h-[600px] object-cover opacity-80"
          />
          <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-40">
            <div className="text-center text-white">
              <h1 className="text-5xl font-bold mb-4">Welcome to Pie Global Furniture</h1>
              <p className="text-xl mb-8">Premium furniture for your home and office</p>
              <Link to="/products" className="bg-white text-primary-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors inline-block">
                Browse Our Collection
              </Link>
            </div>
          </div>
        </section>
      ) : sliders.length > 0 ? (
        <section className="bg-gray-100 py-16">
          <div className="container-custom">
            <div className="grid grid-cols-1 gap-6">
              {sliders.slice(0, 1).map((slider) => (
                <div key={slider.id} className="relative">
                  <img
                    src={slider.image}
                    alt={slider.title}
                    className="w-full h-96 object-cover rounded-lg"
                  />
                  <div className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-40 rounded-lg">
                    <div className="text-center text-white">
                      <h1 className="text-4xl font-bold mb-4">Welcome to Pie Global Furniture</h1>
                      <p className="text-lg mb-6">Premium furniture for your home and office</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      ) : (
        <section className="bg-gradient-to-r from-primary-600 to-secondary-600 py-24">
          <div className="container-custom text-center text-white">
            <h1 className="text-5xl font-bold mb-4">Welcome to Pie Global Furniture</h1>
            <p className="text-xl mb-8">Premium furniture for your home and office</p>
            <Link to="/products" className="bg-white text-primary-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors inline-block">
              Browse Our Collection
            </Link>
          </div>
        </section>
      )}

      {/* Featured Products */}
      <section className="container-custom py-12">
        <h2 className="text-3xl font-bold text-center mb-8">Featured Products</h2>
        {featuredProducts.length > 0 ? (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {featuredProducts.map((product) => (
                <Link
                  key={product.id}
                  to={`/products/${product.slug}`}
                  className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-4"
                >
                  <img
                    src={product.main_image}
                    alt={product.name}
                    className="w-full h-48 object-cover rounded-md mb-4"
                  />
                  <h3 className="font-semibold text-lg mb-2">{product.name}</h3>
                  <p className="text-primary-600 font-bold">${product.price}</p>
                </Link>
              ))}
            </div>
            <div className="text-center mt-8">
              <Link
                to="/products"
                className="btn-primary inline-block"
              >
                View All Products
              </Link>
            </div>
          </>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-600 mb-4">No featured products yet. Check back soon!</p>
            <Link to="/products" className="btn-primary inline-block">
              Browse All Products
            </Link>
          </div>
        )}
      </section>

      {/* About Section */}
      {about && (
        <section className="bg-gray-50 py-16">
          <div className="container-custom">
            <div className="max-w-4xl mx-auto text-center">
              <h2 className="text-4xl font-bold mb-6">{about.headline || 'About Us'}</h2>
              {about.body && (
                <p className="text-lg text-gray-700 mb-8 leading-relaxed whitespace-pre-line">
                  {about.body.substring(0, 300)}...
                </p>
              )}
              <Link to="/about" className="btn-primary inline-block">
                Learn More About Us
              </Link>
            </div>
          </div>
        </section>
      )}
    </div>
  );
};

export default HomePage;
