import React from 'react';
import { useNavigate } from 'react-router-dom';
import { OrderStatusBadge } from './StatusBadge';
import type { AdminOrder } from '@/types';

interface RecentOrdersTableProps {
  orders: AdminOrder[];
  loading?: boolean;
  onViewDetails?: (orderId: number) => void;
  onStatusChange?: (orderId: number, status: string) => void;
}

export const RecentOrdersTable: React.FC<RecentOrdersTableProps> = ({
  orders,
  loading = false,
  onViewDetails,
}) => {
  const navigate = useNavigate();

  const handleViewDetails = (orderId: number) => {
    if (onViewDetails) {
      onViewDetails(orderId);
    } else {
      navigate(`/admin/orders/${orderId}`);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="px-6 py-4">
          <h3 className="text-lg font-semibold text-gray-900">Recent Orders</h3>
        </div>
        <div className="px-6 py-8 space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-12 bg-gray-100 rounded animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Recent Orders</h3>
      </div>

      {orders.length === 0 ? (
        <div className="px-6 py-8 text-center text-gray-500">
          <p>No orders yet</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left font-semibold text-gray-900">Order #</th>
                <th className="px-6 py-3 text-left font-semibold text-gray-900">Customer</th>
                <th className="px-6 py-3 text-left font-semibold text-gray-900">Amount</th>
                <th className="px-6 py-3 text-left font-semibold text-gray-900">Status</th>
                <th className="px-6 py-3 text-left font-semibold text-gray-900">Date</th>
                <th className="px-6 py-3 text-left font-semibold text-gray-900">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {orders.map((order) => (
                <tr key={order.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 font-medium text-gray-900">#{order.id}</td>
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-medium text-gray-900">{order.name}</p>
                      <p className="text-xs text-gray-500">{order.email}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4 font-semibold text-gray-900">
                    ${parseFloat(String(order.total_amount)).toFixed(2)}
                  </td>
                  <td className="px-6 py-4">
                    <OrderStatusBadge status={order.status || 'pending'} />
                  </td>
                  <td className="px-6 py-4 text-gray-600">
                    {new Date(order.created_at || '').toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => handleViewDetails(order.id)}
                      className="text-blue-600 hover:text-blue-800 font-medium text-xs"
                    >
                      View Details →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
