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
    <section className="py-20 bg-gradient-to-b from-white to-gray-50">
      <div className="container-custom">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-secondary-600">
            Featured Collection
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Handpicked pieces that define modern elegance
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8"
        >
          {products.map((product) => (
            <motion.div key={product.id} variants={itemVariants}>
              <Link
                to={`/products/${product.slug}`}
                className="group block bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2"
              >
                {/* Image Container */}
                <div className="relative h-64 overflow-hidden bg-gray-100">
                  <img
                    src={getImageUrl(product.main_image)}
                    alt={product.name}
                    loading="lazy"
                    decoding="async"
                    onError={(e) => {
                      e.currentTarget.src = '/placeholder-product.jpg';
                    }}
                    className="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-500"
                  />
                  
                  {/* Overlay on Hover */}
                  <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center gap-3">
                    <button
                      onClick={(e) => handleAddToCart(product, e)}
                      className="p-3 bg-white rounded-full text-primary-600 hover:bg-primary-600 hover:text-white transition-all duration-300 transform hover:scale-110"
                      title="Add to Cart"
                    >
                      <FaShoppingCart size={20} />
                    </button>
                    <div className="p-3 bg-white rounded-full text-primary-600 hover:bg-primary-600 hover:text-white transition-all duration-300 transform hover:scale-110">
                      <FaEye size={20} />
                    </div>
                  </div>

                  {/* Badges */}
                  {product.on_sale && (
                    <div className="absolute top-4 left-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-semibold">
                      Sale
                    </div>
                  )}
                  {product.featured && (
                    <div className="absolute top-4 right-4 bg-primary-600 text-white px-3 py-1 rounded-full text-sm font-semibold">
                      Featured
                    </div>
                  )}
                </div>

                {/* Content */}
                <div className="p-6">
                  <h3 className="text-xl font-semibold mb-2 text-gray-800 group-hover:text-primary-600 transition-colors">
                    {product.name}
                  </h3>
                  
                  {product.short_description && (
                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                      {product.short_description}
                    </p>
                  )}

                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl font-bold text-primary-600">
                        KSh {product.price}
                      </span>
                      {product.compare_at_price && (
                        <span className="text-sm text-gray-400 line-through">
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
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-center mt-12"
        >
          <Link
            to="/products"
            className="inline-block px-10 py-4 bg-gradient-to-r from-primary-600 to-secondary-600 text-white rounded-full font-semibold text-lg hover:shadow-2xl hover:scale-105 transition-all duration-300"
          >
            Explore All Products
          </Link>
        </motion.div>
      </div>
    </section>
  );
};

export default FeaturedProducts;
