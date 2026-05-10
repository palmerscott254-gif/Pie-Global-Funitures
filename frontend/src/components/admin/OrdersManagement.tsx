import React, { useState } from 'react';
import { OrderStatusBadge } from './StatusBadge';
import { useAdminOrders } from '@/hooks';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import toast from 'react-hot-toast';

export const OrdersManagement: React.FC = () => {
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [newStatus, setNewStatus] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { orders, loading, error, updateStatus, markPaid, refetch } = useAdminOrders(
    true,
    10000,
    100
  );

  const filteredOrders = statusFilter
    ? orders.filter((o) => o.status === statusFilter)
    : orders;

  const handleStatusChange = async (orderId: number) => {
    if (!newStatus) {
      toast.error('Please select a status');
      return;
    }

    setIsSubmitting(true);
    try {
      await updateStatus(orderId, newStatus);
      setEditingId(null);
      setNewStatus('');
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleMarkPaid = async (orderId: number) => {
    setIsSubmitting(true);
    try {
      await markPaid(orderId);
    } catch (err) {
      console.error('Error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading && !orders.length) {
    return <LoadingSpinner fullScreen />;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
        <p className="font-medium">Error loading orders: {error}</p>
        <button
          onClick={refetch}
          className="mt-2 text-red-600 hover:text-red-700 font-medium underline"
        >
          Try Again
        </button>
      </div>
    );
  }

  const statusOptions = [
    { value: 'pending', label: 'Pending' },
    { value: 'received', label: 'Received' },
    { value: 'confirmed', label: 'Confirmed' },
    { value: 'processing', label: 'Processing' },
    { value: 'shipped', label: 'Out for Delivery' },
    { value: 'delivered', label: 'Delivered' },
    { value: 'cancelled', label: 'Cancelled' },
  ];

  return (
    <div className="space-y-6">
      {/* Header and Filters */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Orders Management</h2>
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setStatusFilter('')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              statusFilter === ''
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            All Orders
          </button>
          {statusOptions.map((status) => (
            <button
              key={status.value}
              onClick={() => setStatusFilter(status.value)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                statusFilter === status.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {status.label}
            </button>
          ))}
        </div>
      </div>

      {/* Orders Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        {filteredOrders.length === 0 ? (
          <div className="px-6 py-12 text-center text-gray-500">
            <p>No orders found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left font-semibold text-gray-900">Order ID</th>
                  <th className="px-6 py-3 text-left font-semibold text-gray-900">Customer</th>
                  <th className="px-6 py-3 text-left font-semibold text-gray-900">Amount</th>
                  <th className="px-6 py-3 text-left font-semibold text-gray-900">Status</th>
                  <th className="px-6 py-3 text-left font-semibold text-gray-900">Paid</th>
                  <th className="px-6 py-3 text-left font-semibold text-gray-900">Date</th>
                  <th className="px-6 py-3 text-left font-semibold text-gray-900">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredOrders.map((order) => (
                  <React.Fragment key={order.id}>
                    <tr className="hover:bg-gray-50 transition-colors">
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
                      <td className="px-6 py-4">
                        <span
                          className={`text-xs font-semibold px-2 py-1 rounded ${
                            order.paid
                              ? 'bg-green-100 text-green-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {order.paid ? 'Yes' : 'No'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-gray-600">
                        {new Date(order.created_at || '').toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4">
                        <button
                          onClick={() =>
                            setExpandedId(expandedId === order.id ? null : order.id)
                          }
                          className="text-blue-600 hover:text-blue-800 font-medium text-xs"
                        >
                          {expandedId === order.id ? 'Hide' : 'Manage'}
                        </button>
                      </td>
                    </tr>

                    {/* Expanded Details */}
                    {expandedId === order.id && (
                      <tr className="bg-gray-50">
                        <td colSpan={7} className="px-6 py-4">
                          <div className="space-y-4">
                            {/* Order Items */}
                            <div>
                              <h4 className="font-semibold text-gray-900 mb-2">Order Items</h4>
                              <div className="space-y-2">
                                {order.items?.map((item: any, idx: number) => (
                                  <div
                                    key={idx}
                                    className="flex justify-between items-start bg-white p-3 rounded border border-gray-200"
                                  >
                                    <div>
                                      <p className="font-medium text-gray-900">{item.name}</p>
                                      <p className="text-xs text-gray-500">
                                        Qty: {item.qty} × ${item.price}
                                      </p>
                                    </div>
                                    <p className="font-semibold text-gray-900">
                                      ${(item.qty * item.price).toFixed(2)}
                                    </p>
                                  </div>
                                ))}
                              </div>
                            </div>

                            {/* Delivery Address */}
                            <div>
                              <h4 className="font-semibold text-gray-900 mb-2">Delivery Address</h4>
                              <div className="bg-white p-3 rounded border border-gray-200 text-sm text-gray-700">
                                <p>{order.address}</p>
                                {order.city && <p>{order.city}</p>}
                                {order.postal_code && <p>Code: {order.postal_code}</p>}
                                <p className="mt-2">Phone: {order.phone}</p>
                              </div>
                            </div>

                            {/* Status Update */}
                            {editingId === order.id ? (
                              <div className="bg-white p-3 rounded border border-gray-200 space-y-3">
                                <div>
                                  <label className="block text-sm font-medium text-gray-900 mb-2">
                                    New Status
                                  </label>
                                  <select
                                    value={newStatus}
                                    onChange={(e) => setNewStatus(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                  >
                                    <option value="">Select a status</option>
                                    {statusOptions.map((status) => (
                                      <option key={status.value} value={status.value}>
                                        {status.label}
                                      </option>
                                    ))}
                                  </select>
                                </div>
                                <div className="flex gap-2">
                                  <button
                                    onClick={() => handleStatusChange(order.id)}
                                    disabled={isSubmitting}
                                    className="flex-1 bg-blue-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:bg-gray-400"
                                  >
                                    {isSubmitting ? 'Updating...' : 'Update Status'}
                                  </button>
                                  <button
                                    onClick={() => setEditingId(null)}
                                    disabled={isSubmitting}
                                    className="flex-1 bg-gray-200 text-gray-900 py-2 rounded-lg text-sm font-medium hover:bg-gray-300 disabled:bg-gray-400"
                                  >
                                    Cancel
                                  </button>
                                </div>
                              </div>
                            ) : (
                              <div className="flex gap-2">
                                <button
                                  onClick={() => {
                                    setEditingId(order.id);
                                    setNewStatus(order.status || 'pending');
                                  }}
                                  className="flex-1 bg-blue-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
                                >
                                  Change Status
                                </button>
                                {order.status === 'delivered' && !order.paid && (
                                  <button
                                    onClick={() => handleMarkPaid(order.id)}
                                    disabled={isSubmitting}
                                    className="flex-1 bg-green-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-green-700 disabled:bg-gray-400"
                                  >
                                    {isSubmitting ? 'Marking...' : 'Mark as Paid'}
                                  </button>
                                )}
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
