/**
 * useNotifications Hook
 * Manages notification state and WebSocket connection
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  Notification,
  notificationAPI,
  notificationWebSocket,
} from '@/services/notificationService';

interface UseNotificationsOptions {
  enabled?: boolean;
  pollInterval?: number; // Fallback polling if WebSocket fails (ms)
}

export const useNotifications = (options: UseNotificationsOptions = {}) => {
  const { enabled = true, pollInterval = 30000 } = options;

  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const unsubscribeRef = useRef<Array<() => void>>([]);

  /**
   * Fetch notifications from API
   */
  const fetchNotifications = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const data = await notificationAPI.listNotifications(1, 20, {
        isRead: false,
      });

      setNotifications(data.results);
    } catch (err) {
      console.error('Error fetching notifications:', err);
      setError('Failed to fetch notifications');
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Fetch unread count from API
   */
  const fetchUnreadCount = useCallback(async () => {
    try {
      const count = await notificationAPI.getUnreadCount();
      setUnreadCount(count);
    } catch (err) {
      console.error('Error fetching unread count:', err);
    }
  }, []);

  /**
   * Initialize WebSocket connection and setup polling
   */
  useEffect(() => {
    if (!enabled) return;

    const token = localStorage.getItem('pgf-auth-access');
    if (!token) {
      console.log('ℹ️ No auth token, skipping notification setup');
      return;
    }

    let isMounted = true;

    /**
     * Connect to WebSocket and setup message handlers
     */
    const setupNotifications = async () => {
      try {
        // Connect to WebSocket
        await notificationWebSocket.connect(token);

        if (!isMounted) return;

        setIsConnected(true);

        // Subscribe to new notifications
        const unsubscribeNotification = notificationWebSocket.on(
          'new_notification',
          (event) => {
            if (isMounted) {
              const notification = event.notification as Notification;
              setNotifications((prev) => [notification, ...prev.slice(0, 19)]);
              setUnreadCount((prev) => prev + 1);
            }
          }
        );

        // Subscribe to unread count updates
        const unsubscribeUnreadCount = notificationWebSocket.on(
          'unread_count_update',
          (event) => {
            if (isMounted) {
              setUnreadCount(event.unread_count);
            }
          }
        );

        // Subscribe to connection established
        const unsubscribeConnectionEstablished = notificationWebSocket.on(
          'connection_established',
          () => {
            console.log('🔐 Authentication confirmed via WebSocket');
            // Fetch initial data after successful authentication
            if (isMounted) {
              fetchNotifications();
              fetchUnreadCount();
            }
          }
        );

        // Subscribe to errors
        const unsubscribeError = notificationWebSocket.on('error', (event) => {
          console.error('WebSocket error:', event.message);
          if (isMounted) {
            setError(event.message || 'Connection error');
          }
        });

        // Store unsubscribe functions
        unsubscribeRef.current = [
          unsubscribeNotification,
          unsubscribeUnreadCount,
          unsubscribeConnectionEstablished,
          unsubscribeError,
        ];

        // Setup keep-alive ping every 30 seconds
        const pingInterval = setInterval(() => {
          if (notificationWebSocket.isConnected()) {
            notificationWebSocket.ping();
          }
        }, 30000);

        // Store interval for cleanup
        pollIntervalRef.current = pingInterval;

        // Setup fallback polling (in case WebSocket fails)
        if (pollInterval > 0) {
          const fallbackPollInterval = setInterval(() => {
            if (!notificationWebSocket.isConnected() && isMounted) {
              fetchUnreadCount();
            }
          }, pollInterval);

          pollIntervalRef.current = fallbackPollInterval;
        }
      } catch (err) {
        console.error('Error setting up notifications:', err);
        if (isMounted) {
          setError('Failed to connect to notification service');
        }

        // Fallback: Setup polling
        if (pollInterval > 0) {
          const fallbackPollInterval = setInterval(() => {
            if (isMounted) {
              fetchUnreadCount();
            }
          }, pollInterval);

          pollIntervalRef.current = fallbackPollInterval;
        }
      }
    };

    setupNotifications();

    // Cleanup on unmount
    return () => {
      isMounted = false;

      // Unsubscribe from WebSocket events
      unsubscribeRef.current.forEach((unsubscribe) => unsubscribe());

      // Clear polling intervals (but keep WebSocket connected)
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [enabled, pollInterval, fetchNotifications, fetchUnreadCount]);

  /**
   * Mark notification as read (both API and WebSocket)
   */
  const markAsRead = useCallback(
    async (notificationId: number) => {
      try {
        // Send via API
        await notificationAPI.markAsRead(notificationId);

        // Update local state optimistically
        setNotifications((prev) =>
          prev.map((notif) =>
            notif.id === notificationId ? { ...notif, is_read: true } : notif
          )
        );

        // Update unread count
        setUnreadCount((prev) => Math.max(0, prev - 1));

        // Update unread count on all open instances via WebSocket
        notificationWebSocket.markAsRead(notificationId);
      } catch (err) {
        console.error('Error marking notification as read:', err);
        setError('Failed to mark notification as read');
      }
    },
    []
  );

  /**
   * Mark all notifications as read
   */
  const markAllAsRead = useCallback(async () => {
    try {
      await notificationAPI.markAllAsRead();

      // Update local state
      setNotifications((prev) =>
        prev.map((notif) => ({ ...notif, is_read: true }))
      );
      setUnreadCount(0);
    } catch (err) {
      console.error('Error marking all as read:', err);
      setError('Failed to mark all as read');
    }
  }, []);

  /**
   * Delete a notification
   */
  const deleteNotification = useCallback(async (notificationId: number) => {
    try {
      await notificationAPI.deleteNotification(notificationId);

      // Update local state
      setNotifications((prev) =>
        prev.filter((notif) => notif.id !== notificationId)
      );

      // Update unread count if deleted notification was unread
      setNotifications((prev) => {
        const deletedNotif = prev.find((n) => n.id === notificationId);
        if (!deletedNotif?.is_read) {
          setUnreadCount((current) => Math.max(0, current - 1));
        }
        return prev;
      });
    } catch (err) {
      console.error('Error deleting notification:', err);
      setError('Failed to delete notification');
    }
  }, []);

  /**
   * Navigate to notification and mark as read
   */
  const handleNotificationClick = useCallback(
    (notification: Notification) => {
      // Mark as read
      if (!notification.is_read) {
        markAsRead(notification.id);
      }

      // Navigate if action_url exists
      if (notification.action_url) {
        window.location.href = notification.action_url;
      }
    },
    [markAsRead]
  );

  return {
    notifications,
    unreadCount,
    isLoading,
    error,
    isConnected,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    handleNotificationClick,
    fetchUnreadCount, // For manual refresh
    fetchNotifications, // For manual refresh
  };
};
