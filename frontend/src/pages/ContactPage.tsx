import { useState, FormEvent } from 'react';
import { messagesApi } from '@/services/api';
import toast from 'react-hot-toast';
import { FaPhone, FaEnvelope, FaWhatsapp } from 'react-icons/fa';

const ContactPage = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    message: '',
  });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      await messagesApi.create(formData);
      toast.success('Thank you! We will get back to you soon.');
      setFormData({ name: '', email: '', phone: '', message: '' });
    } catch (error) {
      toast.error('Failed to send message. Please try again.');
      console.error('Error sending message:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="container-custom py-12">
      <h1 className="section-title">Contact Us</h1>
      
      <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-8">
        {/* Contact Form */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-2xl font-bold mb-4">Send us a message</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Name *
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Message *
              </label>
              <textarea
                name="message"
                value={formData.message}
                onChange={handleChange}
                required
                rows={5}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="btn-primary w-full disabled:opacity-50"
            >
              {submitting ? 'Sending...' : 'Send Message'}
            </button>
          </form>
        </div>

        {/* Contact Info */}
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-2xl font-bold mb-4">Get in touch</h2>
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <FaPhone className="text-primary-600 text-xl" />
                <div>
                  <p className="font-medium">Phone</p>
                  <a href="tel:+254704456788" className="text-gray-600 hover:text-primary-600">
                    +254 704 456 788
                  </a>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <FaWhatsapp className="text-green-600 text-xl" />
                <div>
                  <p className="font-medium">WhatsApp</p>
                  <a
                    href="https://wa.me/254704456788?text=hello%20pie%20funitures"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-600 hover:text-green-600"
                  >
                    Chat with us
                  </a>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <FaEnvelope className="text-primary-600 text-xl" />
                <div>
                  <p className="font-medium">Email</p>
                  <a href="mailto:muthikej392@gmail.com" className="text-gray-600 hover:text-primary-600">
                    muthikej392@gmail.com
                  </a>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-primary-50 p-6 rounded-lg">
            <h3 className="text-lg font-bold mb-2">Business Hours</h3>
            <p className="text-gray-700">Monday - Friday: 8:00 AM - 6:00 PM</p>
            <p className="text-gray-700">Saturday: 9:00 AM - 4:00 PM</p>
            <p className="text-gray-700">Sunday: Closed</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContactPage;
