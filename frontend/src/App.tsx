import { Routes, Route } from 'react-router-dom';
import { useEffect, lazy, Suspense } from 'react';
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import CartDrawer from './components/cart/CartDrawer';
import WhatsAppButton from './components/layout/WhatsAppButton';
import ErrorBoundary from './components/common/ErrorBoundary';
import LoadingSpinner from './components/common/LoadingSpinner';
import ScrollToTop from './components/common/ScrollToTop';
import { csrfApi } from './services/api';
import { Toaster } from './services/toast';

const HomePage = lazy(() => import('./pages/HomePage'));
const ProductsPage = lazy(() => import('./pages/ProductsPage'));
const ProductDetailPage = lazy(() => import('./pages/ProductDetailPage'));
const AboutPage = lazy(() => import('./pages/AboutPage'));
const ContactPage = lazy(() => import('./pages/ContactPage'));
const CheckoutPage = lazy(() => import('./pages/CheckoutPage'));
const PrivacyPolicyPage = lazy(() => import('./pages/PrivacyPolicyPage'));
const TermsOfServicePage = lazy(() => import('./pages/TermsOfServicePage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage'));
const AdminDashboardPage = lazy(() => import('./components/admin/AdminDashboardPage'));

function App() {
  useEffect(() => {
    void csrfApi.bootstrap().catch(() => undefined);
  }, []);

  return (
    <ErrorBoundary>
      <div className="flex flex-col min-h-screen">
        <Toaster
          position="top-right"
          containerStyle={{
            top: '1rem',
            right: '1rem',
            left: '1rem',
          }}
          toastOptions={{
            duration: 3000,
            style: {
              background: '#363636',
              color: '#fff',
              width: 'min(28rem, calc(100vw - 2rem))',
              maxWidth: 'calc(100vw - 2rem)',
              padding: '0.875rem 1rem',
              borderRadius: '0.875rem',
              boxShadow: '0 12px 30px rgba(15, 23, 42, 0.18)',
              whiteSpace: 'normal',
              overflowWrap: 'anywhere',
              wordBreak: 'break-word',
              lineHeight: '1.4',
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
        
        <main className="flex-grow" style={{ paddingTop: 'var(--header-offset)' }}>
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
              <Route path="/admin/dashboard/*" element={<AdminDashboardPage />} />
              <Route path="/admin/orders/*" element={<AdminDashboardPage />} />
              <Route path="/admin/messages/*" element={<AdminDashboardPage />} />
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
