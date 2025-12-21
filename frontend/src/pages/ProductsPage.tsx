import { useEffect, useState, useMemo } from 'react';
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
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchTerm, setSearchTerm] = useState<string>(searchParams.get('q') || '');

  useSEO({
    title: 'Shop Furniture - Pie Global Furniture',
    description: 'Browse our wide selection of quality furniture. Sofas, beds, tables, wardrobes, and more. Affordable prices and fast delivery in Nairobi.',
    keywords: 'furniture shop, buy furniture Nairobi, sofas, beds, office furniture, dining tables',
  });

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const params = selectedCategory ? { category: selectedCategory } : {};
        const data = await productsApi.getAll(params);
        setProducts(data.results || []);
      } catch (error) {
        console.error('Error fetching products:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, [selectedCategory]);

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

  const filteredProducts = useMemo(() => {
    if (!searchTerm.trim()) return products;
    const term = searchTerm.toLowerCase();
    return products.filter((product) =>
      product.name.toLowerCase().includes(term) ||
      (product.short_description || '').toLowerCase().includes(term)
    );
  }, [products, searchTerm]);

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
    <div className="container-custom py-12">
      <h1 className="section-title">Our Products</h1>

      {/* Search bar */}
      <div className="max-w-2xl mx-auto mb-8">
        <input
          value={searchTerm}
          onChange={(e) => handleSearchChange(e.target.value)}
          placeholder="Search products by name or description"
          className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2 justify-center mb-8">
        {categories.map((cat) => (
          <button
            key={cat.value}
            onClick={() => setSelectedCategory(cat.value)}
            className={`px-4 py-2 rounded-full transition-colors ${
              selectedCategory === cat.value
                ? 'bg-primary-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Products Grid */}
      {filteredProducts.length > 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
        >
          {filteredProducts.map((product, index) => (
            <motion.div
              key={product.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: index * 0.05 }}
            >
              <Link
                to={`/products/${product.slug}`}
                className="block bg-white rounded-xl shadow-md hover:shadow-2xl transition-all duration-300 overflow-hidden group"
              >
                <div className="relative h-56 overflow-hidden bg-gray-100">
                  <ImageWithFallback
                    src={product.main_image}
                    alt={product.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                  {product.on_sale && (
                    <span className="absolute top-3 right-3 bg-gradient-to-r from-red-500 to-pink-500 text-white px-3 py-1 text-xs font-bold rounded-full shadow-lg">
                      SALE
                    </span>
                  )}
                  {product.featured && (
                    <span className="absolute top-3 left-3 bg-gradient-to-r from-yellow-400 to-orange-400 text-white px-3 py-1 text-xs font-bold rounded-full shadow-lg">
                      ⭐ Featured
                    </span>
                  )}
                </div>
                <div className="p-4">
                  <h3 className="font-bold text-lg mb-2 text-gray-800 group-hover:text-primary-600 transition-colors">
                    {product.name}
                  </h3>
                  <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                    {product.short_description}
                  </p>
                  <div className="flex items-center gap-2">
                    <span className="text-primary-600 font-bold text-xl">KSh {product.price}</span>
                    {product.compare_at_price && (
                      <span className="text-gray-400 line-through text-sm">
                        KSh {product.compare_at_price}
                      </span>
                    )}
                  </div>
                  {product.discount_percentage && (
                    <div className="mt-2">
                      <span className="text-green-600 text-sm font-semibold">
                        Save {product.discount_percentage}%
                      </span>
                    </div>
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
          className="text-center py-20"
        >
          <p className="text-gray-600 text-lg">No products found{searchTerm ? ` for "${searchTerm}"` : ''} in this category.</p>
          <button
            onClick={() => setSelectedCategory('')}
            className="mt-4 btn-primary"
          >
            View All Products
          </button>
        </motion.div>
      )}
    </div>
  );
};

export default ProductsPage;
