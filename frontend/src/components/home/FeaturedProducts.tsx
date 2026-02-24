import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { FaShoppingCart, FaEye } from 'react-icons/fa';
import { getImageUrl } from '@/utils/imageUrl';
import type { Product } from '@/types';
import { useCartStore } from '@/store/cartStore';
import toast from 'react-hot-toast';

interface FeaturedProductsProps {
  products: Product[];
}

const FeaturedProducts = ({ products }: FeaturedProductsProps) => {
  const addToCart = useCartStore((state) => state.addItem);

  const handleAddToCart = (product: Product, e: React.MouseEvent) => {
    e.preventDefault();
    addToCart({
      id: product.id,
      name: product.name,
      slug: product.slug,
      price: parseFloat(product.price),
      image: product.main_image,
    });
    toast.success('Added to cart!');
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
      },
    },
  };

  if (products.length === 0) {
    return (
      <section className="py-20 bg-gray-50">
        <div className="container-custom text-center">
          <h2 className="text-4xl font-bold mb-4">Featured Products</h2>
          <p className="text-gray-600 mb-8">Check back soon for our curated collection!</p>
          <Link to="/products" className="btn-primary inline-block">
            Browse All Products
          </Link>
        </div>
      </section>
    );
  }

  return (
    <section className="py-12 sm:py-16 md:py-20 bg-gradient-to-b from-white to-gray-50">
      <div className="container-custom">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center mb-10 sm:mb-12 md:mb-16"
        >
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-3 sm:mb-4 text-gray-900">
            Featured Collection
          </h2>
          <p className="text-base sm:text-lg text-gray-600 max-w-2xl mx-auto px-4">
            Handpicked pieces that define modern elegance
          </p>
        </motion.div>

        {/* Products Grid */}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 sm:gap-4 md:gap-6 mb-10 sm:mb-12 md:mb-16"
        >
          {products.map((product) => (
            <motion.div key={product.id} variants={itemVariants}>
              <Link
                to={`/products/${product.slug}`}
                className="group flex flex-col h-full bg-white rounded-lg sm:rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-300"
              >
                {/* Image Container - Fixed Aspect Ratio */}
                <div className="relative w-full overflow-hidden bg-gray-100 aspect-square flex-shrink-0">
                  <img
                    src={getImageUrl(product.main_image)}
                    alt={product.name}
                    loading="lazy"
                    decoding="async"
                    crossOrigin="anonymous"
                    onError={(e) => {
                      e.currentTarget.src = '/placeholder-product.jpg';
                    }}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300 will-change-transform"
                  />
                  
                  {/* Quick Action Overlay - Only show on hover for desktop */}
                  <div className="hidden sm:flex absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity duration-300 items-center justify-center gap-3">
                    <button
                      onClick={(e) => handleAddToCart(product, e)}
                      className="p-2.5 sm:p-3 bg-white rounded-full text-primary-600 hover:bg-primary-600 hover:text-white transition-all duration-300 transform hover:scale-110"
                      title="Add to Cart"
                    >
                      <FaShoppingCart size={18} />
                    </button>
                    <a
                      href={`/products/${product.slug}`}
                      className="p-2.5 sm:p-3 bg-white rounded-full text-primary-600 hover:bg-primary-600 hover:text-white transition-all duration-300 transform hover:scale-110"
                      title="View Details"
                    >
                      <FaEye size={18} />
                    </a>
                  </div>

                  {/* Badges */}
                  {product.on_sale && (
                    <span className="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 text-xs font-bold rounded">
                      Sale
                    </span>
                  )}
                  {product.featured && (
                    <span className="absolute top-2 left-2 bg-primary-600 text-white px-2 py-1 text-xs font-bold rounded">
                      Featured
                    </span>
                  )}
                </div>

                {/* Product Info */}
                <div className="flex flex-col flex-grow p-3 sm:p-4">
                  {/* Title */}
                  <h3 className="text-sm sm:text-base font-semibold mb-1.5 text-gray-900 line-clamp-2 group-hover:text-primary-600 transition-colors">
                    {product.name}
                  </h3>

                  {/* Description - Responsive */}
                  {product.short_description && (
                    <p className="hidden sm:block text-xs text-gray-600 line-clamp-2 mb-2 flex-grow">
                      {product.short_description}
                    </p>
                  )}

                  {/* Price and Stock */}
                  <div className="mt-auto">
                    <div className="flex items-baseline gap-2 mb-1">
                      <span className="font-bold text-primary-600 text-sm sm:text-base">
                        KSh {product.price}
                      </span>
                      {product.compare_at_price && (
                        <span className="text-xs text-gray-400 line-through">
                          KSh {product.compare_at_price}
                        </span>
                      )}
                    </div>

                    {!product.in_stock && (
                      <span className="text-xs text-red-500 font-semibold">
                        Out of Stock
                      </span>
                    )}
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </motion.div>

        {/* View All Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-center"
        >
          <Link
            to="/products"
            className="inline-block px-8 sm:px-10 py-3 sm:py-4 bg-primary-600 hover:bg-primary-700 text-white rounded-lg sm:rounded-full font-semibold text-base sm:text-lg transition-all duration-300 hover:shadow-lg active:scale-95"
          >
            Explore All Products
          </Link>
        </motion.div>
      </div>
    </section>
  );
};

export default FeaturedProducts;
