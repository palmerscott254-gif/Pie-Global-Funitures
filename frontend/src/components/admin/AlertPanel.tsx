import React from 'react';
import { useNavigate } from 'react-router-dom';
import type { DashboardAlert } from '@/types';

interface AlertPanelProps {
  alerts: DashboardAlert[];
  loading?: boolean;
}

export const AlertPanel: React.FC<AlertPanelProps> = ({ alerts, loading = false }) => {
  const navigate = useNavigate();

  const severityColors = {
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    danger: 'bg-red-50 border-red-200 text-red-800',
  };

  const severityBgColors = {
    info: 'bg-blue-100',
    warning: 'bg-yellow-100',
    danger: 'bg-red-100',
  };

  const severityTextColors = {
    info: 'text-blue-600',
    warning: 'text-yellow-600',
    danger: 'text-red-600',
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Alerts</h3>
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-16 bg-gray-100 rounded animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Alerts</h3>
      {alerts.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No active alerts ✓</p>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div
              key={alert.type}
              className={`border rounded-lg p-4 ${severityColors[alert.severity]} flex items-start justify-between`}
            >
              <div className="flex items-start gap-3">
                <span
                  className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-white text-sm font-bold ${
                    severityBgColors[alert.severity]
                  }`}
                  style={{
                    color:
                      alert.severity === 'info'
                        ? '#2563eb'
                        : alert.severity === 'warning'
                          ? '#dc2626'
                          : '#ca8a04',
                  }}
                >
                  {alert.count}
                </span>
                <div>
                  <p className="font-medium">{alert.message}</p>
                  <p className={`text-xs mt-1 ${severityTextColors[alert.severity]}`}>
                    Requires attention
                  </p>
                </div>
              </div>
              {alert.action_url && (
                <button
                  onClick={() => navigate(alert.action_url!)}
                  className={`px-3 py-1 rounded text-xs font-semibold hover:opacity-80 transition-opacity ${
                    severityBgColors[alert.severity]
                  } ${severityTextColors[alert.severity]}`}
                >
                  View
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
