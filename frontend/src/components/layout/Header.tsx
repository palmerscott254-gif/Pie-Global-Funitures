import { useState, useEffect } from 'react';
import { Link, NavLink } from 'react-router-dom';
import { FaShoppingCart, FaBars, FaTimes, FaSearch } from 'react-icons/fa';
import { useCartStore } from '@/store/cartStore';
import { useUIStore } from '@/store/uiStore';
import { useScrollPosition } from '@/hooks';
import logoImage from './logo photo.jpeg';

const Header = () => {
  const totalItems = useCartStore((state) => state.getTotalItems());
  const { isMobileMenuOpen, isCartOpen, toggleMobileMenu, toggleCart, closeMobileMenu } = useUIStore();
  const scrollY = useScrollPosition();
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    setIsScrolled(scrollY > 50);
  }, [scrollY]);

  const navLinks = [
    { to: '/', label: 'Home' },
    { to: '/products', label: 'Products' },
    { to: '/about', label: 'About' },
    { to: '/contact', label: 'Contact' },
  ];

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled ? 'bg-white shadow-lg' : 'bg-white/95'
      }`}
    >
      <div className="container-custom">
        <div className="flex items-center justify-between h-20">
          {/* Brand */}
          <Link to="/" className="flex items-center space-x-2">
            <img src={logoImage} alt="PieGlobal logo" className="h-7 md:h-9 w-auto object-contain" />
            <div className="text-2xl font-bold text-primary-600">
              Pie<span className="text-secondary-600">Global</span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            {navLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `text-gray-700 hover:text-primary-600 transition-colors font-medium ${
                    isActive ? 'text-primary-600' : ''
                  }`
                }
              >
                {link.label}
              </NavLink>
            ))}
          </nav>

          {/* Right Actions */}
          <div className="flex items-center space-x-4">
            {/* Search Icon */}
            <button className="hidden md:block text-gray-700 hover:text-primary-600 transition-colors">
              <FaSearch size={20} />
            </button>

            {/* Cart Icon */}
            <button
              onClick={toggleCart}
              className="relative text-gray-700 hover:text-primary-600 transition-colors"
            >
              <FaShoppingCart size={22} />
              {totalItems > 0 && (
                <span className="absolute -top-2 -right-2 bg-primary-600 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                  {totalItems}
                </span>
              )}
            </button>

            {/* Mobile Menu Toggle */}
            <button
              onClick={toggleMobileMenu}
              className="md:hidden text-gray-700 hover:text-primary-600 transition-colors"
            >
              {isMobileMenuOpen ? <FaTimes size={24} /> : <FaBars size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-white border-t border-gray-200 animate-slide-down">
          <nav className="container-custom py-4 flex flex-col space-y-4">
            {navLinks.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                onClick={closeMobileMenu}
                className={({ isActive }) =>
                  `text-gray-700 hover:text-primary-600 transition-colors font-medium ${
                    isActive ? 'text-primary-600' : ''
                  }`
                }
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
};

export default Header;
