import { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { FaShoppingCart, FaBars, FaTimes, FaSearch, FaUser, FaSignOutAlt } from 'react-icons/fa';
import { useCartStore } from '@/store/cartStore';
import { useUIStore } from '@/store/uiStore';
import { useOnClickOutside, useScrollPosition } from '@/hooks';
import { NotificationBell } from '@/components/notifications';
import { clearAuthState, getStoredAuthUser, isAdminUser, type StoredAuthUser } from '@/utils/auth';
import { authApi } from '@/services/api';
import logoImage from './logo photo.jpeg';

const Header = () => {
  const totalItems = useCartStore((state) => state.totalItems);
  const isMobileMenuOpen = useUIStore((state) => state.isMobileMenuOpen);
  const toggleMobileMenu = useUIStore((state) => state.toggleMobileMenu);
  const closeMobileMenu = useUIStore((state) => state.closeMobileMenu);
  const toggleCart = useUIStore((state) => state.toggleCart);
  const scrollY = useScrollPosition();
  const [isScrolled, setIsScrolled] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authUser, setAuthUser] = useState<StoredAuthUser | null>(null);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLFormElement>(null);
  const navigate = useNavigate();
  const closeUserMenu = useCallback(() => setIsUserMenuOpen(false), []);

  useEffect(() => {
    setIsScrolled(scrollY > 50);
  }, [scrollY]);

  useEffect(() => {
    const readAuth = () => {
      const currentUser = getStoredAuthUser();
      setAuthUser(currentUser);
      setIsAuthenticated(!!currentUser);
    };
    readAuth();
    const handler = () => readAuth();
    window.addEventListener('pgf-auth-changed', handler as EventListener);
    return () => window.removeEventListener('pgf-auth-changed', handler as EventListener);
  }, []);

  const adminMode = isAdminUser(authUser);

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

  const handleLogout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch {
      // Ignore backend logout errors; local state still must be cleared.
    } finally {
      useCartStore.getState().clearCart();
      clearAuthState();
      navigate('/login', { replace: true });
      closeUserMenu();
      closeMobileMenu();
    }
  }, [closeMobileMenu, closeUserMenu, navigate]);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-40 transition-all duration-300 backdrop-blur-md ${
        isScrolled ? 'bg-white shadow-lg' : 'bg-white/95'
      }`}
    >
      <div className="container-custom h-full">
        <div className="flex h-16 md:h-20 items-center justify-between gap-3 md:gap-4">
          {/* Brand */}
          <Link to="/" className="flex items-center gap-2 shrink-0">
            <img
              src={logoImage}
              alt="PieGlobal logo"
              className="h-9 md:h-12 w-auto object-contain"
              loading="eager"
              decoding="async"
            />
            <div className="hidden sm:block text-xl md:text-2xl font-bold text-primary-600 whitespace-nowrap">
              Pie<span className="text-secondary-600">Global</span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            {adminMode ? (
              <NavLink
                to="/admin/dashboard/"
                className={({ isActive }) =>
                  `text-gray-700 hover:text-primary-600 transition-colors font-medium ${
                    isActive ? 'text-primary-600' : ''
                  }`
                }
              >
                Admin Dashboard
              </NavLink>
            ) : (
              navLinks.map((link) => (
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
              ))
            )}
          </nav>

          {/* Right Actions */}
          <div className="flex items-center space-x-2 sm:space-x-4 relative">
            {/* Search Icon */}
            {!adminMode && (
              <div className="hidden md:block relative">
              <button
                onClick={() => setIsSearchOpen((prev) => !prev)}
                className="text-gray-700 hover:text-primary-600 transition-colors p-1"
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
            )}

            {/* Notification Bell */}
            {!adminMode && <NotificationBell />}

            {/* Cart Icon */}
            {!adminMode && (
              <button
                onClick={toggleCart}
                className="relative text-gray-700 hover:text-primary-600 transition-colors p-1"
              >
                <FaShoppingCart size={22} />
                {totalItems > 0 && (
                  <span className="absolute -top-2 -right-2 bg-primary-600 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                    {totalItems}
                  </span>
                )}
              </button>
            )}

            {/* User Account Menu - Now visible on all screen sizes */}
            <div className="relative" ref={userMenuRef}>
              <button
                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                className="text-gray-700 hover:text-primary-600 transition-colors p-1"
                aria-label="User account menu"
              >
                <span className="relative inline-block">
                  <FaUser size={22} />
                  {isAuthenticated && (
                    <span className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-green-500 border-2 border-white" aria-hidden />
                  )}
                </span>
              </button>
              
              {isUserMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl border border-gray-200 py-2 z-50">
                  {isAuthenticated ? (
                    /* Authenticated User Menu */
                    <>
                      <div className="px-4 py-2 text-xs text-gray-500 border-b border-gray-200">
                        Signed in
                      </div>
                      <button
                        onClick={() => void handleLogout()}
                        className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100 transition-colors flex items-center gap-2"
                      >
                        <FaSignOutAlt size={14} /> Sign out
                      </button>
                    </>
                  ) : (
                    /* Guest User Menu */
                    <>
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
                    </>
                  )}
                </div>
              )}
            </div>

            {/* Mobile Menu Toggle */}
            <button
              onClick={toggleMobileMenu}
              className="md:hidden text-gray-700 hover:text-primary-600 transition-colors p-1"
            >
              {isMobileMenuOpen ? <FaTimes size={24} /> : <FaBars size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden bg-white border-t border-gray-200 max-h-[calc(100vh-var(--header-offset))] overflow-y-auto animate-slide-down">
          <nav className="container-custom py-4 flex flex-col space-y-4">
            {adminMode ? (
              <NavLink
                to="/admin/dashboard/"
                onClick={closeMobileMenu}
                className={({ isActive }) =>
                  `text-gray-700 hover:text-primary-600 transition-colors font-medium ${
                    isActive ? 'text-primary-600' : ''
                  }`
                }
              >
                Admin Dashboard
              </NavLink>
            ) : (
              navLinks.map((link) => (
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
              ))
            )}

            <div className="pt-4 border-t border-gray-200">
              {isAuthenticated ? (
                /* Authenticated Mobile Menu */
                <button
                  onClick={() => void handleLogout()}
                  className="w-full py-2 bg-red-600 text-white rounded-lg font-semibold shadow hover:bg-red-700 flex items-center justify-center gap-2"
                >
                  <FaSignOutAlt size={14} /> Sign out
                </button>
              ) : (
                /* Guest Mobile Menu */
                !adminMode && (
                  <div className="flex items-center gap-3">
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
                )
              )}
            </div>
          </nav>
        </div>
      )}
    </header>
  );
};

export default Header;
