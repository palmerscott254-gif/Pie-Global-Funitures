import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { DashboardOverview } from './DashboardOverview';
import { OrdersManagement } from './OrdersManagement';
import { MessagesManagement } from './MessagesManagement';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { authApi } from '@/services/api';
import toast from 'react-hot-toast';

export const AdminDashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isAuthorized, setIsAuthorized] = useState<boolean | null>(null);
  const [currentTab, setCurrentTab] = useState<'overview' | 'orders' | 'messages'>('overview');

  // Check authorization (reuse backend auth/me for admin flags)
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await authApi.me();
        if (response.user && (response.user.is_staff || response.user.is_superuser)) {
          setIsAuthorized(true);
        } else {
          setIsAuthorized(false);
          toast.error('You do not have admin access');
          navigate('/');
        }
      } catch (err) {
        setIsAuthorized(false);
        toast.error('Please log in as an admin');
        navigate('/login');
      }
    };

    checkAuth();
  }, [navigate]);

  // Determine current tab based on location
  useEffect(() => {
    const pathname = location.pathname;
    if (pathname.includes('/messages')) {
      setCurrentTab('messages');
    } else if (pathname.includes('/orders')) {
      setCurrentTab('orders');
    } else {
      setCurrentTab('overview');
    }
  }, [location.pathname]);

  if (isAuthorized === null) {
    return <LoadingSpinner fullScreen />;
  }

  if (!isAuthorized) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with Navigation */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Admin Panel</h1>
            </div>
            <div className="flex items-center gap-4">
              <button
                onClick={() => {
                  localStorage.removeItem('pgf-auth-access');
                  navigate('/');
                  toast.success('Logged out');
                }}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium text-sm"
              >
                Logout
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-8 border-t border-gray-200">
            <button
              onClick={() => {
                setCurrentTab('overview');
                navigate('/admin/dashboard/');
              }}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                currentTab === 'overview'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Dashboard Overview
            </button>
            <button
              onClick={() => {
                setCurrentTab('orders');
                navigate('/admin/dashboard/orders/');
              }}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                currentTab === 'orders'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Orders Management
            </button>
            <button
              onClick={() => {
                setCurrentTab('messages');
                navigate('/admin/dashboard/messages/');
              }}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                currentTab === 'messages'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Messages Management
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentTab === 'overview' && <DashboardOverview />}
        {currentTab === 'orders' && <OrdersManagement />}
        {currentTab === 'messages' && <MessagesManagement />}
      </main>
    </div>
  );
};

export default AdminDashboardPage;
