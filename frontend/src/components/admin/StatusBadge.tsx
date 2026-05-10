import React from 'react';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

export const OrderStatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const statusStyles: Record<string, { bg: string; text: string; label: string }> = {
    pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Pending' },
    received: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Received' },
    confirmed: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Confirmed' },
    processing: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Processing' },
    shipped: { bg: 'bg-purple-100', text: 'text-purple-800', label: 'Out for Delivery' },
    delivered: { bg: 'bg-green-100', text: 'text-green-800', label: 'Delivered' },
    cancelled: { bg: 'bg-red-100', text: 'text-red-800', label: 'Cancelled' },
  };

  const style = statusStyles[status] || statusStyles.pending;
  const sizeClass = size === 'sm' ? 'px-2 py-1 text-xs' : 'px-3 py-1 text-sm';

  return (
    <span className={`inline-block ${sizeClass} rounded-full font-semibold ${style.bg} ${style.text}`}>
      {style.label}
    </span>
  );
};

interface MessageStatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

export const MessageStatusBadge: React.FC<MessageStatusBadgeProps> = ({ status, size = 'md' }) => {
  const statusStyles: Record<string, { bg: string; text: string; label: string }> = {
    new: { bg: 'bg-red-100', text: 'text-red-800', label: 'New' },
    read: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Read' },
    replied: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Replied' },
    resolved: { bg: 'bg-green-100', text: 'text-green-800', label: 'Resolved' },
  };

  const style = statusStyles[status] || statusStyles.new;
  const sizeClass = size === 'sm' ? 'px-2 py-1 text-xs' : 'px-3 py-1 text-sm';

  return (
    <span className={`inline-block ${sizeClass} rounded-full font-semibold ${style.bg} ${style.text}`}>
      {style.label}
    </span>
  );
};
