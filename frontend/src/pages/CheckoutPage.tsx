import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaLock, FaShoppingBag } from 'react-icons/fa';
import { useCartStore } from '@/store/cartStore';
import { ordersApi } from '@/services/api';
import { getImageUrl } from '@/utils/imageUrl';
import { useSEO } from '@/hooks';
import { formatPrice } from '@/utils/helpers';
import toast from 'react-hot-toast';
import LoadingSpinner from '@/components/common/LoadingSpinner';

interface CheckoutFormData {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  delivery_notes: string;
}

const CheckoutPage = () => {
  const navigate = useNavigate();
  const items = useCartStore((state) => state.items);
  const totalPrice = useCartStore((state) => state.totalPrice);
  const clearCart = useCartStore((state) => state.clearCart);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<CheckoutFormData>({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    address: '',
    city: 'Nairobi',
    delivery_notes: '',
  });

  useSEO({
    title: 'Checkout - Pie Global Furniture',
    description: 'Complete your furniture order',
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (items.length === 0) {
      toast.error('Your cart is empty');
      return;
    }
    
    // Client-side validation
    if (formData.first_name.trim().length < 2) {
      toast.error('First name must be at least 2 characters');
      return;
    }
    
    if (formData.last_name.trim().length < 2) {
      toast.error('Last name must be at least 2 characters');
      return;
    }
    
    if (formData.phone.trim().length < 8) {
      toast.error('Please provide a valid phone number');
      return;
    }
    
    if (formData.address.trim().length < 5) {
      toast.error('Please provide a complete address');
      return;
    }

    setLoading(true);

    try {
      // Sanitize and validate order data
      const orderData = {
        name: `${formData.first_name.trim()} ${formData.last_name.trim()}`.slice(0, 100),
        email: formData.email.trim().toLowerCase().slice(0, 254),
        phone: formData.phone.trim().slice(0, 20),
        address: formData.address.trim().slice(0, 200),
        city: formData.city.trim().slice(0, 100),
        postal_code: '', // Optional field
        notes: formData.delivery_notes.trim().slice(0, 500),
        payment_method: 'Cash on Delivery',
        items: items.map((item) => ({
          product_id: item.id,
          name: item.name.slice(0, 200),
          price: parseFloat(item.price.toFixed(2)),
          qty: Math.max(1, Math.min(1000, item.quantity)), // Limit quantity range
        })),
        total_amount: parseFloat(totalPrice.toFixed(2)),
      };

      await ordersApi.create(orderData);
      
      clearCart();
      toast.success('Order placed successfully! We will contact you shortly.');
      navigate('/');
    } catch (error: any) {
      // Handle rate limiting
      if (error.message?.includes('Too many requests')) {
        toast.error('Too many requests. Please try again later.');
      } else {
        toast.error(error.response?.data?.detail || 'Failed to place order. Please try again.');
      }
      if (import.meta.env.DEV) {
        console.error('Order error:', error);
      }
    } finally {
      setLoading(false);
    }
  };

  if (items.length === 0) {
    return (
      <div className="container-custom py-20 text-center">
        <FaShoppingBag className="mx-auto text-6xl text-gray-300 mb-4" />
        <h1 className="text-3xl font-bold mb-4">Your Cart is Empty</h1>
        <button onClick={() => navigate('/products')} className="btn-primary">
          Continue Shopping
        </button>
      </div>
    );
  }

  return (
    <div className="container-custom py-12">
      <h1 className="section-title mb-8">Checkout</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Checkout Form */}
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-lg p-8">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <FaLock className="text-primary-600" />
              Delivery Information
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <label className="block text-sm font-medium mb-2">First Name *</label>
                <input
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleInputChange}
                  required
                  maxLength={50}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Last Name *</label>
                <input
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleInputChange}
                  required
                  maxLength={50}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div>
                <label className="block text-sm font-medium mb-2">Email *</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                  maxLength={254}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Phone *</label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  required
                  maxLength={20}
                  placeholder="0712345678"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">Delivery Address *</label>
              <input
                type="text"
                name="address"
                value={formData.address}
                onChange={handleInputChange}
                required
                maxLength={200}
                placeholder="Street address, building, apartment"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">City *</label>
              <input
                type="text"
                name="city"
                value={formData.city}
                onChange={handleInputChange}
                required
                maxLength={100}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">Delivery Notes (Optional)</label>
              <textarea
                name="delivery_notes"
                value={formData.delivery_notes}
                onChange={handleInputChange}
                rows={3}
                maxLength={500}
                placeholder="Special instructions for delivery"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full text-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? <LoadingSpinner size="sm" /> : 'Place Order'}
            </button>
          </form>
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-lg p-8 sticky top-24"
          >
            <h2 className="text-2xl font-bold mb-6">Order Summary</h2>

            <div className="space-y-4 mb-6">
              {items.map((item) => (
                <div key={item.id} className="flex gap-4 pb-4 border-b">
                  <img
                    src={getImageUrl(item.image)}
                    alt={item.name}
                    className="w-16 h-16 object-cover rounded-lg"
                  />
                  <div className="flex-1">
                    <h3 className="font-medium">{item.name}</h3>
                    <p className="text-sm text-gray-600">Qty: {item.quantity}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold">{formatPrice(item.price * item.quantity)}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="space-y-3 mb-6 pt-4 border-t">
              <div className="flex justify-between text-gray-600">
                <span>Subtotal</span>
                <span>{formatPrice(totalPrice)}</span>
              </div>
              <div className="flex justify-between text-gray-600">
                <span>Delivery</span>
                <span className="text-green-600 font-medium">Free</span>
              </div>
            </div>

            <div className="flex justify-between text-xl font-bold pt-4 border-t">
              <span>Total</span>
              <span className="text-primary-600">{formatPrice(totalPrice)}</span>
            </div>

            <p className="text-sm text-gray-500 mt-4 text-center">
              Payment upon delivery • Fast delivery within Nairobi
            </p>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default CheckoutPage;
