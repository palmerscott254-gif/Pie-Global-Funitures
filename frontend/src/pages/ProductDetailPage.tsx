import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaShoppingCart, FaArrowLeft, FaCheck, FaTimes } from 'react-icons/fa';
import { productsApi } from '@/services/api';
import { getImageUrl } from '@/utils/imageUrl';
import { useCartStore } from '@/store/cartStore';
import { useSEO } from '@/hooks';
import type { Product } from '@/types';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ImageWithFallback from '@/components/common/ImageWithFallback';
import toast from 'react-hot-toast';

const ProductDetailPage = () => {
  const { slug } = useParams<{ slug: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState<string>('');
  const addToCart = useCartStore((state) => state.addItem);

  useEffect(() => {
    const fetchProduct = async () => {
      if (!slug) return;
      
      try {
        const data = await productsApi.getBySlug(slug);
        setProduct(data);
        setSelectedImage(data.main_image);
      } catch (error) {
        console.error('Error fetching product:', error);
        toast.error('Product not found');
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [slug]);

  useSEO({
    title: product ? `${product.name} - Pie Global Furniture` : 'Product Details',
    description: product?.short_description || product?.description || 'View product details',
    keywords: product ? `${product.name}, ${product.category}, furniture` : 'furniture',
  });

  const handleAddToCart = () => {
    if (!product) return;
    
    addToCart({
      id: product.id,
      name: product.name,
      slug: product.slug,
      price: parseFloat(product.price),
      image: product.main_image,
    });
    toast.success('Added to cart!');
  };

  if (loading) {
    return <LoadingSpinner fullScreen />;
  }

  if (!product) {
    return (
      <div className="container-custom py-20 text-center">
        <h1 className="text-3xl font-bold mb-4">Product Not Found</h1>
        <Link to="/products" className="btn-primary inline-block">
          Browse Products
        </Link>
      </div>
    );
  }

  const galleryImages = product.gallery ? [product.main_image, ...product.gallery] : [product.main_image];

  return (
    <div className="container-custom py-12">
      <Link to="/products" className="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 mb-8">
        <FaArrowLeft /> Back to Products
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Image Gallery */}
        <div>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-gray-100 rounded-2xl overflow-hidden mb-4"
          >
            <ImageWithFallback
              src={selectedImage}
              alt={product.name}
              className="w-full h-[500px] object-cover"
              loading="eager"
            />
          </motion.div>
          
          {galleryImages.length > 1 && (
            <div className="grid grid-cols-4 gap-4">
              {galleryImages.map((img, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedImage(img)}
                  className={`rounded-lg overflow-hidden border-2 transition-all ${
                    selectedImage === img ? 'border-primary-600' : 'border-transparent'
                  }`}
                >
                  <img
                    src={getImageUrl(img)}
                    alt={`${product.name} ${idx + 1}`}
                    className="w-full h-20 object-cover"
                    loading="lazy"
                    decoding="async"
                    sizes="(max-width: 768px) 25vw, 10vw"
                  />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Product Info */}
        <div>
          <h1 className="text-4xl font-bold mb-4">{product.name}</h1>
          
          <div className="flex items-center gap-4 mb-6">
            <span className="text-3xl font-bold text-primary-600">
              KSh {parseFloat(product.price).toLocaleString()}
            </span>
            {product.compare_at_price && (
              <>
                <span className="text-xl text-gray-400 line-through">
                  KSh {parseFloat(product.compare_at_price).toLocaleString()}
                </span>
                {product.discount_percentage > 0 && (
                  <span className="bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold">
                    Save {product.discount_percentage}%
                  </span>
                )}
              </>
            )}
          </div>

          <div className="mb-6">
            <span className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${
              product.in_stock ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {product.in_stock ? <FaCheck /> : <FaTimes />}
              {product.in_stock ? `In Stock (${product.stock} available)` : 'Out of Stock'}
            </span>
          </div>

          <p className="text-gray-700 mb-8 leading-relaxed">{product.description}</p>

          {product.dimensions && (
            <div className="mb-4">
              <strong className="text-gray-900">Dimensions:</strong> {product.dimensions}
            </div>
          )}
          {product.material && (
            <div className="mb-4">
              <strong className="text-gray-900">Material:</strong> {product.material}
            </div>
          )}
          {product.color && (
            <div className="mb-4">
              <strong className="text-gray-900">Color:</strong> {product.color}
            </div>
          )}

          <button
            onClick={handleAddToCart}
            disabled={!product.in_stock}
            className="btn-primary w-full lg:w-auto flex items-center justify-center gap-3 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <FaShoppingCart />
            {product.in_stock ? 'Add to Cart' : 'Out of Stock'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailPage;
