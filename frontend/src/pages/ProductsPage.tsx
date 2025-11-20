import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { productsApi } from '@/services/api';
import type { Product } from '@/types';

const ProductsPage = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('');

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
    return (
      <div className="container-custom py-12 text-center">
        <div className="spinner mx-auto"></div>
      </div>
    );
  }

  return (
    <div className="container-custom py-12">
      <h1 className="section-title">Our Products</h1>

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
      {products.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {products.map((product) => (
            <Link
              key={product.id}
              to={`/products/${product.slug}`}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-4"
            >
              <div className="relative">
                <img
                  src={product.main_image}
                  alt={product.name}
                  className="w-full h-48 object-cover rounded-md mb-4"
                />
                {product.on_sale && (
                  <span className="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 text-xs rounded">
                    Sale
                  </span>
                )}
              </div>
              <h3 className="font-semibold text-lg mb-2">{product.name}</h3>
              <p className="text-gray-600 text-sm mb-2 line-clamp-2">
                {product.short_description}
              </p>
              <div className="flex items-center gap-2">
                <span className="text-primary-600 font-bold">KSh {product.price}</span>
                {product.compare_at_price && (
                  <span className="text-gray-400 line-through text-sm">
                    KSh {product.compare_at_price}
                  </span>
                )}
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <p className="text-center text-gray-600">No products found.</p>
      )}
    </div>
  );
};

export default ProductsPage;
