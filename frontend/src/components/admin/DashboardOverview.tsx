import React, { useMemo } from 'react';
import {
  ShoppingCart,
  Package,
  CheckCircle,
  XCircle,
  MessageSquare,
  DollarSign,
  TrendingUp,
} from 'lucide-react';
import { KPICard } from './KPICard';
import { AlertPanel } from './AlertPanel';
import { RecentOrdersTable } from './RecentOrdersTable';
import { RecentMessagesPanel } from './RecentMessagesPanel';
import { RevenueChart } from './RevenueChart';
import { useDashboardSummary, useDashboardAlerts, useAdminOrders, useAdminMessages } from '@/hooks';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import toast from 'react-hot-toast';

export const DashboardOverview: React.FC = () => {
  // Fetch dashboard data with polling
  const { data: dashboardData, loading: summaryLoading, error: summaryError } =
    useDashboardSummary(true, 10000);
  const { alerts, loading: alertsLoading, error: alertsError } = useDashboardAlerts(true, 10000);
  const {
    orders,
    loading: ordersLoading,
    error: ordersError,
    updateStatus,
  } = useAdminOrders(true, 10000, 5);
  const {
    messages,
    loading: messagesLoading,
    error: messagesError,
    reply,
    resolve,
  } = useAdminMessages(true, 10000, 5);

  // Show error toast if any API errors
  React.useEffect(() => {
    if (summaryError) toast.error(`Summary error: ${summaryError}`);
  }, [summaryError]);

  React.useEffect(() => {
    if (alertsError) toast.error(`Alerts error: ${alertsError}`);
  }, [alertsError]);

  React.useEffect(() => {
    if (ordersError) toast.error(`Orders error: ${ordersError}`);
  }, [ordersError]);

  React.useEffect(() => {
    if (messagesError) toast.error(`Messages error: ${messagesError}`);
  }, [messagesError]);

  const isLoading = useMemo(
    () => summaryLoading || alertsLoading || ordersLoading || messagesLoading,
    [summaryLoading, alertsLoading, ordersLoading, messagesLoading]
  );

  if (isLoading && !dashboardData) {
    return <LoadingSpinner fullScreen />;
  }

  return (
    <div className="space-y-8 pb-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-gray-500 mt-1">Real-time business monitoring and management</p>
        </div>
        <div className="text-xs text-gray-500">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* KPI Cards */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <KPICard
            label="Total Orders"
            value={dashboardData?.total_orders || 0}
            icon={<ShoppingCart />}
            color="blue"
          />
          <KPICard
            label="Pending Orders"
            value={dashboardData?.pending_orders || 0}
            icon={<Package />}
            color="yellow"
          />
          <KPICard
            label="Delivered Orders"
            value={dashboardData?.delivered_orders || 0}
            icon={<CheckCircle />}
            color="green"
          />
          <KPICard
            label="Cancelled Orders"
            value={dashboardData?.cancelled_orders || 0}
            icon={<XCircle />}
            color="red"
          />
        </div>
      </div>

      {/* Messages and Revenue Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <KPICard
          label="Unread Messages"
          value={dashboardData?.unread_messages || 0}
          icon={<MessageSquare />}
          color="purple"
        />
        <KPICard
          label="Revenue Today"
          value={`$${parseFloat(String(dashboardData?.revenue_today || 0)).toFixed(2)}`}
          icon={<DollarSign />}
          color="green"
        />
        <KPICard
          label="Revenue This Month"
          value={`$${parseFloat(String(dashboardData?.revenue_this_month || 0)).toFixed(2)}`}
          icon={<TrendingUp />}
          color="purple"
        />
      </div>

      {/* Alerts */}
      <AlertPanel alerts={alerts} loading={alertsLoading} />

      {/* Recent Orders and Messages - Two Column */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <RecentOrdersTable
            orders={orders}
            loading={ordersLoading}
            onStatusChange={(orderId, status) => updateStatus(orderId, status)}
          />
        </div>
        <div>
          <RecentMessagesPanel
            messages={messages}
            loading={messagesLoading}
            onReply={async (messageId, replyText) => {
              await reply(messageId, replyText);
            }}
            onResolve={async (messageId) => {
              await resolve(messageId);
            }}
          />
        </div>
      </div>

      {/* Revenue Analytics */}
      <RevenueChart
        revenueToday={dashboardData?.revenue_today || 0}
        revenueMonth={dashboardData?.revenue_this_month || 0}
        revenueAllTime={dashboardData?.revenue_all_time || 0}
        averageOrderValue={dashboardData?.average_order_value || 0}
      />
    </div>
  );
};
