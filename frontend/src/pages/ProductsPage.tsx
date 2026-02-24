import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { productsApi } from '@/services/api';
import type { Product } from '@/types';
import { useSEO } from '@/hooks';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ImageWithFallback from '@/components/common/ImageWithFallback';

const ProductsPage = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchTerm, setSearchTerm] = useState<string>(searchParams.get('q') || '');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(false);
  const [totalCount, setTotalCount] = useState<number | null>(null);

  useSEO({
    title: 'Shop Furniture - Pie Global Furniture',
    description: 'Browse our wide selection of quality furniture. Sofas, beds, tables, wardrobes, and more. Affordable prices and fast delivery in Nairobi.',
    keywords: 'furniture shop, buy furniture Nairobi, sofas, beds, office furniture, dining tables',
  });

  const buildParams = (pageToLoad: number) => {
    const params: Record<string, any> = { page: pageToLoad };
    if (selectedCategory) params.category = selectedCategory;
    if (searchTerm.trim()) params.search = searchTerm.trim();
    return params;
  };

  const fetchProducts = async (pageToLoad: number, append = false) => {
    try {
      if (append) {
        setLoadingMore(true);
      } else {
        setLoading(true);
      }
      console.debug('[ProductsPage] Fetching products...', {
        category: selectedCategory,
        search: searchTerm,
        page: pageToLoad,
      });
      const data = await productsApi.getAll(buildParams(pageToLoad));
      const pageResults = Array.isArray(data) ? data : data.results || [];
      setProducts((prev) => (append ? [...prev, ...pageResults] : pageResults));
      const nextPageExists = !Array.isArray(data) && Boolean(data.next);
      setHasMore(nextPageExists);
      setTotalCount(!Array.isArray(data) && typeof data.count === 'number' ? data.count : pageResults.length);
      setPage(pageToLoad);
      console.debug('[ProductsPage] Products loaded:', pageResults.length);
    } catch (error) {
      console.error('[ProductsPage] Error fetching products:', error);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  useEffect(() => {
    fetchProducts(1, false);
  }, [selectedCategory, searchTerm]);

  useEffect(() => {
    setSearchTerm(searchParams.get('q') || '');
  }, [searchParams]);

  const handleSearchChange = (value: string) => {
    setSearchTerm(value);
    const params = new URLSearchParams(searchParams);
    if (value.trim()) {
      params.set('q', value.trim());
    } else {
      params.delete('q');
    }
    setSearchParams(params, { replace: true });
  };

  const categories = [
    { value: '', label: 'All Products' },
    { value: 'sofa', label: 'Sofas' },
    { value: 'bed', label: 'Beds' },
    { value: 'table', label: 'Tables' },
    { value: 'wardrobe', label: 'Wardrobes' },
    { value: 'office', label: 'Office Furniture' },
    { value: 'dining', label: 'Dining' },
    { value: 'outdoor', label: 'Outdoor' },
  ];

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  return (
    <div className="container-custom py-8 sm:py-12">
      <h1 className="text-3xl sm:text-4xl font-bold text-center mb-8 sm:mb-12 text-gray-900">
        Our Products
      </h1>

      {/* Search bar */}
      <div className="max-w-2xl mx-auto mb-6 sm:mb-8">
        <input
          value={searchTerm}
          onChange={(e) => handleSearchChange(e.target.value)}
          placeholder="Search products..."
          className="w-full px-4 py-3 text-base border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
        />
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2 sm:gap-3 justify-center mb-8 sm:mb-10">
        {categories.map((cat) => (
          <button
            key={cat.value}
            onClick={() => setSelectedCategory(cat.value)}
            className={`px-3 sm:px-4 py-1.5 sm:py-2 text-sm font-medium rounded-full transition-all duration-200 whitespace-nowrap ${
              selectedCategory === cat.value
                ? 'bg-primary-600 text-white shadow-md'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Products Grid */}
      {products.length > 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-6 mb-10 sm:mb-12"
        >
          {products.map((product, index) => (
            <motion.div
              key={product.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: Math.min(index * 0.02, 0.2) }}
            >
              <Link
                to={`/products/${product.slug}`}
                className="group flex flex-col h-full bg-white rounded-lg sm:rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 overflow-hidden"
              >
                {/* Image Container - Fixed Aspect Ratio */}
                <div className="relative w-full overflow-hidden bg-gray-100 aspect-square flex-shrink-0">
                  <ImageWithFallback
                    src={product.main_image}
                    alt={product.name}
                    loading="lazy"
                    decoding="async"
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300 will-change-transform"
                  />
                  
                  {/* Sale Badge */}
                  {product.on_sale && (
                    <span className="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 text-xs font-bold rounded">
                      SALE
                    </span>
                  )}
                  
                  {/* Featured Badge */}
                  {product.featured && (
                    <span className="absolute top-2 left-2 bg-yellow-500 text-white px-2 py-1 text-xs font-bold rounded">
                      Featured
                    </span>
                  )}
                </div>

                {/* Product Info */}
                <div className="flex flex-col flex-grow p-3 sm:p-4">
                  {/* Title */}
                  <h3 className="text-sm sm:text-base font-semibold text-gray-900 line-clamp-2 mb-1.5 sm:mb-2 group-hover:text-primary-600 transition-colors">
                    {product.name}
                  </h3>

                  {/* Short Description - Hidden on very small screens for performance */}
                  {product.short_description && (
                    <p className="hidden sm:block text-gray-600 text-xs mb-2 line-clamp-2 flex-grow">
                      {product.short_description}
                    </p>
                  )}

                  {/* Price Section */}
                  <div className="flex items-baseline gap-2 mt-auto">
                    <span className="text-primary-600 font-bold text-sm sm:text-base">
                      KSh {product.price}
                    </span>
                    {product.compare_at_price && (
                      <span className="text-gray-400 line-through text-xs">
                        {product.compare_at_price}
                      </span>
                    )}
                  </div>

                  {/* Discount Badge */}
                  {product.discount_percentage && (
                    <span className="text-green-600 text-xs font-semibold mt-1">
                      Save {product.discount_percentage}%
                    </span>
                  )}
                </div>
              </Link>
            </motion.div>
          ))}
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-16 sm:py-20"
        >
          <p className="text-gray-600 text-base sm:text-lg mb-4">
            No products found{searchTerm ? ` for "${searchTerm}"` : ''} in this category.
          </p>
          <button
            onClick={() => setSelectedCategory('')}
            className="btn-primary"
          >
            View All Products
          </button>
        </motion.div>
      )}

      {/* Load More Button */}
      {hasMore && (
        <div className="flex justify-center mb-6">
          <button
            onClick={() => fetchProducts(page + 1, true)}
            className="btn-primary"
            disabled={loadingMore}
          >
            {loadingMore ? 'Loading...' : 'Load More'}
          </button>
        </div>
      )}

      {/* Product Count */}
      {totalCount !== null && (
        <p className="text-center text-xs sm:text-sm text-gray-500">
          Showing {products.length} of {totalCount} products
        </p>
      )}
    </div>
  );
};

export default ProductsPage;
