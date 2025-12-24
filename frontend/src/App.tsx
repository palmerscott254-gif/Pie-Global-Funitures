import { Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import CartDrawer from './components/cart/CartDrawer';
import WhatsAppButton from './components/layout/WhatsAppButton';
import ErrorBoundary from './components/common/ErrorBoundary';
import LoadingSpinner from './components/common/LoadingSpinner';
import ScrollToTop from './components/common/ScrollToTop';

// Lazy load pages for better performance
import { lazy, Suspense } from 'react';

const HomePage = lazy(() => import('./pages/HomePage').catch(() => ({ default: () => <div>Failed to load page</div> })));
const ProductsPage = lazy(() => import('./pages/ProductsPage').catch(() => ({ default: () => <div>Failed to load page</div> })));
const ProductDetailPage = lazy(() => import('./pages/ProductDetailPage').catch(() => ({ default: () => <div>Failed to load page</div> })));
const AboutPage = lazy(() => import('./pages/AboutPage').catch(() => ({ default: () => <div>Failed to load page</div> })));
const ContactPage = lazy(() => import('./pages/ContactPage').catch(() => ({ default: () => <div>Failed to load page</div> })));
const CheckoutPage = lazy(() => import('./pages/CheckoutPage').catch(() => ({ default: () => <div>Failed to load page</div> })));
const PrivacyPolicyPage = lazy(() => import('./pages/PrivacyPolicyPage').catch(() => ({ default: () => <div>Failed to load page</div> })));
const TermsOfServicePage = lazy(() => import('./pages/TermsOfServicePage').catch(() => ({ default: () => <div>Failed to load page</div> })));
const LoginPage = lazy(() => import('./pages/LoginPage').catch(() => ({ default: () => <div>Failed to load page</div> })));
const RegisterPage = lazy(() => import('./pages/RegisterPage').catch(() => ({ default: () => <div>Failed to load page</div> })));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage').catch(() => ({ default: () => <div>404 - Page not found</div> })));

function App() {
  return (
    <ErrorBoundary>
      <div className="flex flex-col min-h-screen">
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              iconTheme: {
                primary: '#10b981',
                secondary: '#fff',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
        
        <Header />
        <CartDrawer />
        <WhatsAppButton />
        <ScrollToTop />
        
        <main className="flex-grow pt-20">
          <Suspense fallback={<LoadingSpinner fullScreen />}>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/products" element={<ProductsPage />} />
              <Route path="/products/:slug" element={<ProductDetailPage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="/contact" element={<ContactPage />} />
              <Route path="/checkout" element={<CheckoutPage />} />
              <Route path="/privacy" element={<PrivacyPolicyPage />} />
              <Route path="/terms" element={<TermsOfServicePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </Suspense>
        </main>
        
        <Footer />
      </div>
    </ErrorBoundary>
  );
}

export default App;
