import React from 'react';

interface RevenueChartProps {
  revenueToday: number | string;
  revenueMonth: number | string;
  revenueAllTime: number | string;
  averageOrderValue: number | string;
}

export const RevenueChart: React.FC<RevenueChartProps> = ({
  revenueToday,
  revenueMonth,
  revenueAllTime,
  averageOrderValue,
}) => {
  const today = parseFloat(String(revenueToday));
  const month = parseFloat(String(revenueMonth));
  const allTime = parseFloat(String(revenueAllTime));
  const avgOrder = parseFloat(String(averageOrderValue));

  // Simple bar chart representation
  const maxRevenue = Math.max(today, month, allTime, avgOrder * 100);
  const getBarWidth = (value: number) => {
    return (value / maxRevenue) * 100;
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Revenue Analytics</h3>

      <div className="space-y-6">
        {/* Today */}
        <div>
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Revenue Today</span>
            <span className="text-sm font-semibold text-gray-900">${today.toFixed(2)}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-green-500 h-2 rounded-full transition-all"
              style={{ width: `${getBarWidth(today)}%` }}
            />
          </div>
        </div>

        {/* This Month */}
        <div>
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Revenue This Month</span>
            <span className="text-sm font-semibold text-gray-900">${month.toFixed(2)}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all"
              style={{ width: `${getBarWidth(month)}%` }}
            />
          </div>
        </div>

        {/* All Time */}
        <div>
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Revenue All Time</span>
            <span className="text-sm font-semibold text-gray-900">${allTime.toFixed(2)}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-purple-500 h-2 rounded-full transition-all"
              style={{ width: `${getBarWidth(allTime)}%` }}
            />
          </div>
        </div>

        {/* Average Order Value */}
        <div>
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Average Order Value</span>
            <span className="text-sm font-semibold text-gray-900">${avgOrder.toFixed(2)}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-orange-500 h-2 rounded-full transition-all"
              style={{ width: `${getBarWidth(avgOrder)}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
