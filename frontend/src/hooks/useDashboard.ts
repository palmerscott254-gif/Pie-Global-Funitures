import { useState, useEffect, useCallback, useRef } from 'react';
import { adminApi } from '@/services/api';
import type { DashboardSummary, DashboardAlert, AdminOrder, AdminMessage } from '@/types';
import toast from 'react-hot-toast';

/**
 * Hook for polling dashboard summary data
 * Automatically refreshes every 10 seconds
 */
export const useDashboardSummary = (enabled: boolean = true, pollInterval: number = 10000) => {
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const result = await adminApi.getDashboardSummary();
      setData(result);
      setError(null);
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Failed to fetch dashboard data';
      setError(message);
      console.error('Dashboard fetch error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!enabled) return;

    // Initial fetch
    fetchData();

    // Setup polling
    intervalRef.current = setInterval(fetchData, pollInterval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [enabled, pollInterval, fetchData]);

  return { data, loading, error, refetch: fetchData };
};

/**
 * Hook for polling dashboard alerts
 */
export const useDashboardAlerts = (enabled: boolean = true, pollInterval: number = 10000) => {
  const [alerts, setAlerts] = useState<DashboardAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchAlerts = useCallback(async () => {
    try {
      const result = await adminApi.getAlerts();
      setAlerts(result);
      setError(null);
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Failed to fetch alerts';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!enabled) return;

    fetchAlerts();
    intervalRef.current = setInterval(fetchAlerts, pollInterval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [enabled, pollInterval, fetchAlerts]);

  return { alerts, loading, error, refetch: fetchAlerts };
};

/**
 * Hook for managing admin orders
 */
export const useAdminOrders = (enabled: boolean = true, pollInterval: number = 10000, limit: number = 10) => {
  const [orders, setOrders] = useState<AdminOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchOrders = useCallback(async (status?: string) => {
    try {
      const result = await adminApi.getRecentOrders(limit, status);
      setOrders(result);
      setError(null);
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Failed to fetch orders';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [limit]);

  const updateStatus = useCallback(async (orderId: number, status: string, notes?: string) => {
    try {
      const result = await adminApi.updateOrderStatus(orderId, status, notes);
      // Update local state
      setOrders(orders.map((o: AdminOrder) => o.id === orderId ? result.order : o));
      toast.success(result.message);
      return result.order;
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Failed to update order';
      toast.error(message);
      throw err;
    }
  }, [orders]);

  const markPaid = useCallback(async (orderId: number) => {
    try {
      const result = await adminApi.markOrderPaid(orderId);
      setOrders(orders.map((o: AdminOrder) => o.id === orderId ? result.order : o));
      toast.success('Order marked as paid');
      return result.order;
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Failed to mark order as paid';
      toast.error(message);
      throw err;
    }
  }, [orders]);

  useEffect(() => {
    if (!enabled) return;

    fetchOrders();
    intervalRef.current = setInterval(() => fetchOrders(), pollInterval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [enabled, pollInterval, fetchOrders]);

  return { orders, loading, error, updateStatus, markPaid, refetch: fetchOrders };
};

/**
 * Hook for managing admin messages
 */
export const useAdminMessages = (enabled: boolean = true, pollInterval: number = 10000, limit: number = 10) => {
  const [messages, setMessages] = useState<AdminMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchMessages = useCallback(async (status?: string) => {
    try {
      const result = await adminApi.getRecentMessages(limit, status);
      setMessages(result);
      setError(null);
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Failed to fetch messages';
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [limit]);

  const reply = useCallback(async (messageId: number, replyText: string, status?: string) => {
    try {
      const result = await adminApi.replyToMessage(messageId, replyText, status);
      setMessages(messages.map((m: AdminMessage) => m.id === messageId ? result.data : m));
      toast.success('Reply sent successfully');
      return result.data;
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Failed to send reply';
      toast.error(message);
      throw err;
    }
  }, [messages]);

  const resolve = useCallback(async (messageId: number) => {
    try {
      const result = await adminApi.resolveMessage(messageId);
      setMessages(messages.map((m: AdminMessage) => m.id === messageId ? result.data : m));
      toast.success('Message marked as resolved');
      return result.data;
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Failed to resolve message';
      toast.error(message);
      throw err;
    }
  }, [messages]);

  useEffect(() => {
    if (!enabled) return;

    fetchMessages();
    intervalRef.current = setInterval(() => fetchMessages(), pollInterval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [enabled, pollInterval, fetchMessages]);

  return { messages, loading, error, reply, resolve, refetch: fetchMessages };
};
