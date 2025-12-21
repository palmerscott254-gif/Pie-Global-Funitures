import { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { FaShoppingCart, FaBars, FaTimes, FaSearch, FaUser, FaSignOutAlt } from 'react-icons/fa';
import { shallow } from 'zustand/shallow';
import { useCartStore } from '@/store/cartStore';
import { useUIStore } from '@/store/uiStore';
import { useOnClickOutside, useScrollPosition } from '@/hooks';
import logoImage from './logo photo.jpeg';

const Header = () => {
  const totalItems = useCartStore((state) => state.getTotalItems());
  const { isMobileMenuOpen, toggleMobileMenu, toggleCart, closeMobileMenu } = useUIStore(
    (state) => ({
      isMobileMenuOpen: state.isMobileMenuOpen,
      toggleMobileMenu: state.toggleMobileMenu,
      closeMobileMenu: state.closeMobileMenu,
      toggleCart: state.toggleCart,
    }),
    shallow
  );
  const scrollY = useScrollPosition();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const userMenuRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLFormElement>(null);
  const navigate = useNavigate();
  const closeUserMenu = useCallback(() => setIsUserMenuOpen(false), []);

  useEffect(() => {
    setIsScrolled(scrollY > 50);
  }, [scrollY]);

  const navLinks = useMemo(
    () => [
      { to: '/', label: 'Home' },
      { to: '/products', label: 'Products' },
      { to: '/about', label: 'About' },
      { to: '/contact', label: 'Contact' },
    ],
    []
  );

  useOnClickOutside(userMenuRef, closeUserMenu);
  useOnClickOutside(searchRef, () => setIsSearchOpen(false));

  const handleSearchSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      const term = searchTerm.trim();
      if (!term) return;
      navigate(`/products?q=${encodeURIComponent(term)}`);
      setIsSearchOpen(false);
    },
    [navigate, searchTerm]
  );

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled ? 'bg-white shadow-lg' : 'bg-white/95'
      }`}
    >
      <div className="container-custom">
        <div className="flex items-center justify-between h-20">
          {/* Brand */}
          <Link to="/" className="flex items-center space-x-1">
            <img src={logoImage} alt="PieGlobal logo" className="h-10 md:h-12 w-auto object-contain" />
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
          <div className="flex items-center space-x-4 relative">
            {/* Search Icon */}
            <div className="hidden md:block">
              <button
                onClick={() => setIsSearchOpen((prev) => !prev)}
                className="text-gray-700 hover:text-primary-600 transition-colors"
                aria-label="Search products"
              >
                <FaSearch size={20} />
              </button>

              {isSearchOpen && (
                <form
                  ref={searchRef}
                  onSubmit={handleSearchSubmit}
                  className="absolute right-0 mt-3 w-72 bg-white shadow-xl border border-gray-200 rounded-xl p-3 flex items-center gap-2"
                >
                  <input
                    autoFocus
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Search products..."
                    className="flex-1 px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                  <button
                    type="submit"
                    className="px-3 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                  >
                    Go
                  </button>
                </form>
              )}
            </div>

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

            {/* User Account Menu */}
            <div className="relative hidden md:block" ref={userMenuRef}>
              <button
                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                className="text-gray-700 hover:text-primary-600 transition-colors"
                aria-label="User account menu"
              >
                <FaUser size={22} />
              </button>
              
              {isUserMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl border border-gray-200 py-2 z-50">
                  <Link
                    to="/login"
                    onClick={closeUserMenu}
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                  >
                    Sign in
                  </Link>
                  <Link
                    to="/register"
                    onClick={closeUserMenu}
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                  >
                    Create account
                  </Link>
                  <hr className="my-2" />
                  <button
                    className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100 transition-colors flex items-center gap-2"
                  >
                    <FaSignOutAlt size={14} /> Sign out
                  </button>
                </div>
              )}
            </div>

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

            <div className="flex items-center gap-3 pt-4 border-t border-gray-200">
              <Link
                to="/login"
                onClick={closeMobileMenu}
                className="flex-1 text-center py-2 border border-gray-200 rounded-lg font-medium text-gray-700 hover:text-primary-600"
              >
                Sign in
              </Link>
              <Link
                to="/register"
                onClick={closeMobileMenu}
                className="flex-1 text-center py-2 bg-primary-600 text-white rounded-lg font-semibold shadow hover:bg-primary-700"
              >
                Create account
              </Link>
            </div>
          </nav>
        </div>
      )}
    </header>
  );
};

export default Header;
