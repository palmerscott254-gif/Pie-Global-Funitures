import { Link } from 'react-router-dom';
import { FaPhone, FaEnvelope, FaFacebookF, FaInstagram, FaTwitter, FaLinkedinIn } from 'react-icons/fa';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-gray-300">
      {/* Main Footer */}
      <div className="container-custom py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Company Info */}
          <div>
            <h3 className="text-white text-xl font-bold mb-4">Pie Global Furniture</h3>
            <p className="mb-4 text-sm">
              Premium furniture for your home and office. Quality craftsmanship, modern designs, and exceptional service.
            </p>
            <div className="flex space-x-3">
              <a href="#" className="hover:text-primary-500 transition-colors">
                <FaFacebookF size={18} />
              </a>
              <a href="#" className="hover:text-primary-500 transition-colors">
                <FaInstagram size={18} />
              </a>
              <a href="#" className="hover:text-primary-500 transition-colors">
                <FaTwitter size={18} />
              </a>
              <a href="#" className="hover:text-primary-500 transition-colors">
                <FaLinkedinIn size={18} />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-white text-lg font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/" className="hover:text-primary-500 transition-colors">Home</Link></li>
              <li><Link to="/products" className="hover:text-primary-500 transition-colors">Products</Link></li>
              <li><Link to="/about" className="hover:text-primary-500 transition-colors">About Us</Link></li>
              <li><Link to="/contact" className="hover:text-primary-500 transition-colors">Contact</Link></li>
            </ul>
          </div>

          {/* Categories */}
          <div>
            <h4 className="text-white text-lg font-semibold mb-4">Categories</h4>
            <ul className="space-y-2 text-sm">
              <li><Link to="/products?category=sofa" className="hover:text-primary-500 transition-colors">Sofas</Link></li>
              <li><Link to="/products?category=bed" className="hover:text-primary-500 transition-colors">Beds</Link></li>
              <li><Link to="/products?category=table" className="hover:text-primary-500 transition-colors">Tables</Link></li>
              <li><Link to="/products?category=wardrobe" className="hover:text-primary-500 transition-colors">Wardrobes</Link></li>
              <li><Link to="/products?category=office" className="hover:text-primary-500 transition-colors">Office Furniture</Link></li>
            </ul>
          </div>

          {/* Contact Info */}
          <div>
            <h4 className="text-white text-lg font-semibold mb-4">Contact Us</h4>
            <ul className="space-y-3 text-sm">
              <li className="flex items-center space-x-2">
                <FaPhone className="text-primary-500" />
                <span>+254704456788</span>
              </li>
              <li className="flex items-center space-x-2">
                <FaEnvelope className="text-primary-500" />
                <span>pieglobal308@gmail.com</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-gray-800">
        <div className="container-custom py-6">
          <div className="flex flex-col md:flex-row justify-between items-center text-sm">
            <p>&copy; {currentYear} Pie Global Furniture. All rights reserved.</p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <Link to="/privacy" className="hover:text-primary-500 transition-colors">Privacy Policy</Link>
              <Link to="/terms" className="hover:text-primary-500 transition-colors">Terms of Service</Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
