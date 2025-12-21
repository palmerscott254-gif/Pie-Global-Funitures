import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FaArrowRight, FaGift, FaHeart, FaUserPlus } from 'react-icons/fa';
import { toast } from 'react-hot-toast';

// Registration is optional. We highlight the upside but keep a guest-friendly stance.
const RegisterPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Simple client-side registry to prevent logins with unknown emails
      const existingRaw = localStorage.getItem('pgf-auth-users');
      const existingUsers: Array<{ name: string; email: string; password: string }> = existingRaw ? JSON.parse(existingRaw) : [];

      const emailExists = existingUsers.some((u) => u.email.toLowerCase() === email.toLowerCase());
      if (emailExists) {
        toast.error('An account with this email already exists.');
        return;
      }

      const newUsers = [...existingUsers, { name, email, password }];
      localStorage.setItem('pgf-auth-users', JSON.stringify(newUsers));
      localStorage.setItem('pgf-auth-current', JSON.stringify({ email }));
      window.dispatchEvent(new Event('pgf-auth-changed'));

      toast.success('Account created — welcome!');
      const redirectTo = (location.state as { from?: string } | null)?.from || '/';
      navigate(redirectTo, { replace: true });
    } catch (err) {
      toast.error('Could not create account. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary-50 via-white to-primary-50">
      <div className="container-custom py-20 grid lg:grid-cols-2 gap-12 items-center">
        {/* Value pitch */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="space-y-6"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white shadow-sm border border-gray-100 text-sm text-secondary-700">
            <FaGift className="text-secondary-600" />
            <span>Members get early drops</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 leading-tight">
            Join for curated drops, saved carts, and rewards.
          </h1>
          <p className="text-lg text-gray-600 max-w-xl">
            Create an optional account to sync favorites, unlock early access, and get delivery updates. Guest checkout stays open.
          </p>
          <div className="grid sm:grid-cols-3 gap-4 max-w-xl">
            {[{ icon: <FaHeart className="text-secondary-600" />, label: 'Wishlist sync' }, { icon: <FaGift className="text-secondary-600" />, label: 'Member-only drops' }, { icon: <FaUserPlus className="text-secondary-600" />, label: '1-click checkout' }].map((item) => (
              <div key={item.label} className="flex items-center gap-2 text-sm font-semibold text-gray-700 bg-white/70 backdrop-blur rounded-lg px-3 py-2 shadow-sm">
                {item.icon}
                <span>{item.label}</span>
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
          <div className="absolute -top-24 -left-20 w-52 h-52 bg-secondary-100 rounded-full blur-3xl opacity-60" />
          <div className="absolute -bottom-20 -right-10 w-44 h-44 bg-primary-100 rounded-full blur-3xl opacity-50" />

          <div className="relative flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-full bg-secondary-50 text-secondary-700 flex items-center justify-center text-2xl">
              <FaUserPlus />
            </div>
            <div>
              <p className="text-sm text-gray-500">Pie Global Accounts</p>
              <h2 className="text-2xl font-bold text-gray-900">Create account</h2>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full name</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="input-field"
                placeholder="Bruno Fernandes"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-field"
                placeholder="scott@example.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-field"
                placeholder="Create a strong password"
              />
            </div>

            <div className="text-sm text-gray-600">
              <p>By creating an account you agree to our <Link to="/terms" className="text-secondary-600 font-semibold hover:text-secondary-700">Terms</Link> and <Link to="/privacy" className="text-secondary-600 font-semibold hover:text-secondary-700">Privacy</Link>.</p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn btn-secondary flex items-center justify-center gap-2 text-base"
            >
              {loading ? 'Creating...' : 'Create account'}
              {!loading && <FaArrowRight />}
            </button>

            <p className="text-sm text-gray-600 text-center">
              Already have an account? <Link to="/login" className="text-secondary-600 font-semibold hover:text-secondary-700">Sign in</Link>
            </p>

            <div className="text-xs text-gray-500 text-center leading-relaxed">
              No pressure. You can always shop and checkout as a guest.
            </div>
          </form>
        </motion.div>
      </div>
    </div>
  );
};

export default RegisterPage;
