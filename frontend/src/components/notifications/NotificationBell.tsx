/**
 * NotificationBell Component
 * Displays notification bell with badge and dropdown
 * Features:
 * - Real-time badge count updates via WebSocket
 * - Click to mark as read
 * - Badge positioned at top-right corner (critical requirement)
 * - Responsive design
 * - Loading and error states
 */

import React, { useRef, useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { FaBell, FaCheck } from 'react-icons/fa';
import { useNotifications } from '@/hooks/useNotifications';
import type { Notification } from '@/services/notificationService';

interface NotificationBellProps {
  onNotificationClick?: (notification: Notification) => void;
  className?: string;
}

export const NotificationBell: React.FC<NotificationBellProps> = ({
  onNotificationClick,
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const bellButtonRef = useRef<HTMLButtonElement>(null);

  const {
    notifications,
    unreadCount,
    isLoading,
    error,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    handleNotificationClick,
  } = useNotifications({ enabled: true });

  /**
   * Close dropdown when clicking outside
   */
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        bellButtonRef.current &&
        !bellButtonRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  /**
   * Format time relative to now
   */
  const getRelativeTime = (createdAt: string) => {
    const now = new Date();
    const notifTime = new Date(createdAt);
    const diffMs = now.getTime() - notifTime.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return notifTime.toLocaleDateString();
  };

  /**
   * Handle notification click with custom callback
   */
  const handleClick = async (notification: Notification) => {
    handleNotificationClick(notification);
    onNotificationClick?.(notification);
    setIsOpen(false);
  };

  const hasUnread = unreadCount > 0;
  const displayCount = unreadCount > 99 ? '99+' : unreadCount;
  const portalRoot = typeof document !== 'undefined' ? document.getElementById('portal-root') : null;

  return (
    <div className={`relative ${className}`}>
      {/* Bell Button */}
      <button
        ref={bellButtonRef}
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-700 hover:text-primary-600 transition-colors duration-200 rounded-lg hover:bg-gray-100"
        aria-label={`Open notifications (${unreadCount} unread)`}
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        <FaBell size={20} />

        {/* Badge - Top Right Corner (CRITICAL POSITIONING) */}
        {hasUnread && (
          <div
            className={`
              absolute
              flex items-center justify-center
              w-5 h-5 rounded-full
              bg-red-500
              text-white text-xs font-bold
              border-2 border-white
              shadow-md
              transition-transform duration-200
              hover:scale-110
            `}
            style={{
              top: '-6px',
              right: '-6px',
              zIndex: 20,
            }}
            aria-label={`${unreadCount} unread notifications`}
          >
            {displayCount}
          </div>
        )}

        {/* Connection status is intentionally silent; polling fallback handles updates */}
      </button>

      {/* Dropdown Menu */}
      {isOpen && portalRoot && createPortal(
        <div
          ref={dropdownRef}
          className="fixed right-4 top-20 md:right-6 w-96 max-w-[calc(100vw-2rem)] bg-white shadow-2xl border border-gray-200 rounded-2xl overflow-hidden z-[9999] animate-in fade-in slide-in-from-top-2 duration-200"
        >
          {/* Header */}
          <div className="px-4 py-3 border-b border-gray-100 bg-gradient-to-r from-gray-50 to-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold text-gray-900">Notifications</p>
                <p className="text-xs text-gray-500">
                  {unreadCount > 0 ? `${unreadCount} unread` : 'All caught up!'}
                </p>
              </div>
              {unreadCount > 0 && (
                <button
                  type="button"
                  onClick={markAllAsRead}
                  className="px-3 py-1 text-xs font-medium text-primary-600 bg-primary-50 rounded-full hover:bg-primary-100 transition-colors"
                >
                  Mark all read
                </button>
              )}
            </div>
          </div>

          {/* Content */}
          <div>
            {/* Loading State */}
            {isLoading && (
              <div className="py-8 px-4 text-center">
                <div className="inline-block">
                  <div className="animate-spin">
                    <FaBell className="text-primary-400" size={24} />
                  </div>
                </div>
                <p className="mt-2 text-sm text-gray-500">Loading...</p>
              </div>
            )}

            {/* Error State */}
            {error && !isLoading && (
              <div className="py-4 px-4 text-center">
                <p className="text-sm text-red-600">{error}</p>
                <p className="text-xs text-gray-500 mt-1">Please refresh or try again</p>
              </div>
            )}

            {/* Empty State */}
            {!isLoading && !error && notifications.length === 0 && (
              <div className="py-8 px-4 text-center">
                <FaBell className="mx-auto text-gray-300 mb-2" size={32} />
                <p className="text-sm font-medium text-gray-600">No notifications yet</p>
                <p className="text-xs text-gray-500 mt-1">
                  We'll notify you when something important happens
                </p>
              </div>
            )}

            {/* Notifications List */}
            {!isLoading && !error && notifications.length > 0 && (
              <div className="max-h-96 overflow-y-auto divide-y divide-gray-100">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`px-4 py-3 hover:bg-gray-50 transition-colors cursor-pointer group ${
                      notification.is_read ? 'bg-white' : 'bg-blue-50'
                    }`}
                    onClick={() => handleClick(notification)}
                  >
                    <div className="flex items-start gap-3">
                      {/* Status Indicator */}
                      <div className="mt-1 flex-shrink-0">
                        {notification.is_read ? (
                          <div className="w-2.5 h-2.5 rounded-full bg-gray-300" />
                        ) : (
                          <div className="w-2.5 h-2.5 rounded-full bg-primary-500 animate-pulse" />
                        )}
                      </div>

                      {/* Content */}
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-gray-900 group-hover:text-primary-600 transition-colors">
                          {notification.title}
                        </p>
                        <p className="text-sm text-gray-600 mt-0.5 line-clamp-2">
                          {notification.description || notification.message || ''}
                        </p>
                        <p className="mt-1.5 text-xs text-gray-400">
                          {getRelativeTime(notification.created_at)}
                        </p>

                        {/* Type Badge */}
                        <div className="mt-2">
                          <span className="inline-block px-2 py-1 text-xs font-medium text-gray-600 bg-gray-100 rounded">
                            {(notification.type || notification.notification_type || 'notification')
                              .replace(/_/g, ' ')
                              .toUpperCase()}
                          </span>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex-shrink-0 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        {!notification.is_read && (
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              markAsRead(notification.id);
                            }}
                            className="p-1 text-gray-400 hover:text-primary-600 transition-colors"
                            title="Mark as read"
                          >
                            <FaCheck size={14} />
                          </button>
                        )}
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteNotification(notification.id);
                          }}
                          className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                          title="Delete"
                        >
                          <span className="text-sm">✕</span>
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          {!isLoading && notifications.length > 0 && (
            <div className="px-4 py-3 bg-gray-50 border-t border-gray-100">
              <a
                href="/notifications"
                onClick={() => setIsOpen(false)}
                className="block text-center w-full py-2 rounded-lg bg-primary-600 text-white text-sm font-semibold hover:bg-primary-700 transition-colors"
              >
                View all notifications
              </a>
            </div>
          )}

          {/* Connection status is intentionally hidden for silent reconnect UX */}
        </div>,
        portalRoot
      )}
    </div>
  );
};

export default NotificationBell;
