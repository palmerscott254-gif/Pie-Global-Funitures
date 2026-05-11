/**
 * Notification Service
 * Handles API calls and WebSocket communication with backend notification system
 */

import { API_URL } from './api';

export interface Notification {
  id: number;
  uuid: string;
  title: string;
  description: string;
  type: string;
  priority: 'LOW' | 'NORMAL' | 'HIGH' | 'URGENT';
  is_read: boolean;
  read_at: string | null;
  action_url: string | null;
  metadata: Record<string, any>;
  created_at: string;
}

export interface UnreadCountResponse {
  unread_count: number;
}

export interface NotificationListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Notification[];
}

/**
 * REST API methods for notification management
 */
export const notificationAPI = {
  /**
   * Get paginated list of notifications
   */
  listNotifications: async (
    page: number = 1,
    pageSize: number = 20,
    filters?: { isRead?: boolean; notificationType?: string }
  ): Promise<NotificationListResponse> => {
    const url = new URL(`${API_URL}/api/notifications/`);
    url.searchParams.append('page', page.toString());
    url.searchParams.append('page_size', pageSize.toString());

    if (filters?.isRead !== undefined) {
      url.searchParams.append('is_read', filters.isRead.toString());
    }
    if (filters?.notificationType) {
      url.searchParams.append('notification_type', filters.notificationType);
    }

    const response = await fetch(url.toString(), {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('pgf-auth-access')}`,
      },
    });

    if (!response.ok) throw new Error('Failed to fetch notifications');
    return response.json();
  },

  /**
   * Get unread notification count (for badge)
   * CRITICAL: This is called frequently to update the badge
   */
  getUnreadCount: async (): Promise<number> => {
    const response = await fetch(`${API_URL}/api/notifications/unread-count/`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('pgf-auth-access')}`,
      },
    });

    if (!response.ok) throw new Error('Failed to fetch unread count');
    const data: UnreadCountResponse = await response.json();
    return data.unread_count;
  },

  /**
   * Mark single notification as read
   */
  markAsRead: async (notificationId: number): Promise<Notification> => {
    const response = await fetch(`${API_URL}/api/notifications/${notificationId}/mark-read/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('pgf-auth-access')}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) throw new Error('Failed to mark notification as read');
    return response.json();
  },

  /**
   * Mark all notifications as read
   */
  markAllAsRead: async (): Promise<void> => {
    const response = await fetch(`${API_URL}/api/notifications/mark-all-read/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('pgf-auth-access')}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) throw new Error('Failed to mark all as read');
  },

  /**
   * Delete (soft delete) a notification
   */
  deleteNotification: async (notificationId: number): Promise<void> => {
    const response = await fetch(`${API_URL}/api/notifications/${notificationId}/`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('pgf-auth-access')}`,
      },
    });

    if (!response.ok) throw new Error('Failed to delete notification');
  },

  /**
   * Bulk action on multiple notifications
   */
  bulkAction: async (
    notificationIds: number[],
    action: 'mark_read' | 'mark_unread' | 'delete'
  ): Promise<void> => {
    const response = await fetch(`${API_URL}/api/notifications/bulk-action/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('pgf-auth-access')}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        notification_ids: notificationIds,
        action,
      }),
    });

    if (!response.ok) throw new Error(`Failed to perform bulk action: ${action}`);
  },
};

/**
 * WebSocket Manager for real-time notifications
 * Handles connection, authentication, and message routing
 */
export class NotificationWebSocket {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private messageHandlers: Map<string, Set<(data: any) => void>> = new Map();
  private isIntentionallyClosed = false;

  constructor() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    this.url = `${protocol}//${host}/ws/notifications/`;
  }

  /**
   * Connect to WebSocket with JWT authentication
   */
  connect(token: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        // Include token in URL query parameter
        const connectionUrl = `${this.url}?token=${encodeURIComponent(token)}`;
        this.ws = new WebSocket(connectionUrl);

        // Connection established
        this.ws.onopen = () => {
          console.log('✅ Connected to notification service');
          this.reconnectAttempts = 0;
          resolve();
        };

        // Handle incoming messages
        this.ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('❌ Error parsing WebSocket message:', error);
          }
        };

        // Handle errors
        this.ws.onerror = (error) => {
          console.error('🔴 WebSocket error:', error);
          reject(error);
        };

        // Handle disconnection
        this.ws.onclose = () => {
          console.log('⚠️ Disconnected from notification service');
          if (!this.isIntentionallyClosed) {
            this.attemptReconnect(token);
          }
        };
      } catch (error) {
        console.error('❌ Error creating WebSocket:', error);
        reject(error);
      }
    });
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage(message: any) {
    const { type } = message;

    // Emit to all subscribed handlers for this message type
    const handlers = this.messageHandlers.get(type);
    if (handlers) {
      handlers.forEach((handler) => {
        try {
          handler(message);
        } catch (error) {
          console.error(`Error in handler for message type "${type}":`, error);
        }
      });
    }
  }

  /**
   * Subscribe to a message type
   */
  on(messageType: string, callback: (data: any) => void) {
    if (!this.messageHandlers.has(messageType)) {
      this.messageHandlers.set(messageType, new Set());
    }
    this.messageHandlers.get(messageType)!.add(callback);

    // Return unsubscribe function
    return () => {
      const handlers = this.messageHandlers.get(messageType);
      if (handlers) {
        handlers.delete(callback);
      }
    };
  }

  /**
   * Send command to server
   */
  send(action: string, payload: Record<string, any> = {}) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action, ...payload }));
    } else {
      console.warn('⚠️ WebSocket not connected, cannot send message');
    }
  }

  /**
   * Mark notification as read via WebSocket
   */
  markAsRead(notificationId: number) {
    this.send('mark_read', { notification_id: notificationId });
  }

  /**
   * Send keep-alive ping
   */
  ping() {
    this.send('ping');
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  private attemptReconnect(token: string) {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error(
        '❌ Max reconnection attempts reached. Please refresh the page.'
      );
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts - 1), 30000);

    console.log(
      `⏳ Attempting to reconnect... (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`
    );

    setTimeout(() => {
      this.connect(token).catch((error) => {
        console.error('Reconnection attempt failed:', error);
      });
    }, delay);
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect() {
    this.isIntentionallyClosed = true;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Create singleton instance
export const notificationWebSocket = new NotificationWebSocket();
