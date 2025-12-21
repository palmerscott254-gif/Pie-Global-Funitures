import { useState, useEffect, useRef, useMemo } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaArrowRight, FaCheckCircle, FaShieldAlt, FaUser } from 'react-icons/fa';
import { toast } from 'react-hot-toast';

// This page is intentionally optional: browsing and checkout do not require login.
// We provide a soft opt-in experience with social proof and low friction.
const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const emailInputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  const registeredEmails = useMemo(() => {
    const raw = localStorage.getItem('pgf-auth-users');
    if (!raw) return [];
    const users: Array<{ email: string; name?: string }> = JSON.parse(raw);
    return users.map((u) => u.email);
  }, []);

  const filteredSuggestions = useMemo(() => {
    if (!email.trim()) return registeredEmails;
    const term = email.toLowerCase();
    return registeredEmails.filter((e) => e.toLowerCase().includes(term));
  }, [email, registeredEmails]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        emailInputRef.current && !emailInputRef.current.contains(e.target as Node) &&
        suggestionsRef.current && !suggestionsRef.current.contains(e.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const existingRaw = localStorage.getItem('pgf-auth-users');
      const existingUsers: Array<{ email: string; password: string; name?: string }> = existingRaw ? JSON.parse(existingRaw) : [];

      const user = existingUsers.find((u) => u.email.toLowerCase() === email.toLowerCase());
      if (!user) {
        toast.error('No account found for this email. Please register first.');
        return;
      }

      if (user.password !== password) {
        toast.error('Incorrect password.');
        return;
      }

      toast.success('Signed in — welcome back!');
      // Persist current user and notify header
      localStorage.setItem('pgf-auth-current', JSON.stringify({ email: user.email }));
      window.dispatchEvent(new Event('pgf-auth-changed'));
      const redirectTo = (location.state as { from?: string } | null)?.from || '/';
      navigate(redirectTo, { replace: true });
    } catch (err) {
      toast.error('Could not sign in. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-primary-50">
      <div className="container-custom py-20 grid lg:grid-cols-2 gap-12 items-center">
        {/* Story + Social proof */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="space-y-6"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white shadow-sm border border-gray-100 text-sm text-primary-700">
            <FaShieldAlt className="text-primary-600" />
            <span>Secure, optional sign-in</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 leading-tight">
            Welcome back to curated comfort.
          </h1>
          <p className="text-lg text-gray-600 max-w-xl">
            Sign in to sync your cart, track orders, and get tailored recommendations. Browsing stays open — no lock-in.
          </p>
          <div className="grid sm:grid-cols-3 gap-4 max-w-xl">
            {["2-day delivery", "Trusted by 50k homes", "No-spam privacy"].map((item) => (
              <div key={item} className="flex items-center gap-2 text-sm font-semibold text-gray-700 bg-white/70 backdrop-blur rounded-lg px-3 py-2 shadow-sm">
                <FaCheckCircle className="text-primary-600" />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="bg-white shadow-xl rounded-2xl p-8 md:p-10 border border-gray-100 relative overflow-hidden"
        >
          <div className="absolute -top-20 -right-20 w-48 h-48 bg-primary-100 rounded-full blur-3xl opacity-60" />
          <div className="absolute -bottom-24 -left-10 w-40 h-40 bg-secondary-100 rounded-full blur-3xl opacity-50" />

          <div className="relative flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-full bg-primary-50 text-primary-700 flex items-center justify-center text-2xl">
              <FaUser />
            </div>
            <div>
              <p className="text-sm text-gray-500">Pie Global Accounts</p>
              <h2 className="text-2xl font-bold text-gray-900">Sign in</h2>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                ref={emailInputRef}
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onFocus={() => setShowSuggestions(true)}
                className="input-field"
                placeholder="scott@example.com"
                autoComplete="off"
              />
              {showSuggestions && filteredSuggestions.length > 0 && (
                <div
                  ref={suggestionsRef}
                  className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto"
                >
                  {filteredSuggestions.map((suggestionEmail) => (
                    <button
                      key={suggestionEmail}
                      type="button"
                      onClick={() => {
                        setEmail(suggestionEmail);
                        setShowSuggestions(false);
                        emailInputRef.current?.focus();
                      }}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-primary-50 transition-colors"
                    >
                      {suggestionEmail}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-field"
                placeholder="••••••••"
              />
            </div>

            <div className="flex items-center justify-between text-sm text-gray-600">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="h-4 w-4 text-primary-600" />
                <span>Remember me</span>
              </label>
              <button type="button" className="text-primary-600 hover:text-primary-700 font-semibold">Forgot password?</button>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn btn-primary flex items-center justify-center gap-2 text-base"
            >
              {loading ? 'Signing in...' : 'Continue'}
              {!loading && <FaArrowRight />}
            </button>

            <p className="text-sm text-gray-600 text-center">
              New here? <Link to="/register" className="text-primary-600 font-semibold hover:text-primary-700">Create an account</Link>
            </p>

            <div className="text-xs text-gray-500 text-center leading-relaxed">
              Optional account for convenience. You can browse and checkout as a guest anytime.
            </div>
          </form>
        </motion.div>
      </div>
    </div>
  );
};

export default LoginPage;
