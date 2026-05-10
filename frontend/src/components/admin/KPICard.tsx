import React from 'react';

interface KPICardProps {
  label: string;
  value: number | string;
  icon: React.ReactNode;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
  color?: 'blue' | 'green' | 'red' | 'yellow' | 'purple';
}

const colorMap = {
  blue: 'bg-blue-50 border-blue-200 text-blue-600',
  green: 'bg-green-50 border-green-200 text-green-600',
  red: 'bg-red-50 border-red-200 text-red-600',
  yellow: 'bg-yellow-50 border-yellow-200 text-yellow-600',
  purple: 'bg-purple-50 border-purple-200 text-purple-600',
};

const iconColorMap = {
  blue: 'text-blue-600',
  green: 'text-green-600',
  red: 'text-red-600',
  yellow: 'text-yellow-600',
  purple: 'text-purple-600',
};

export const KPICard: React.FC<KPICardProps> = ({
  label,
  value,
  icon,
  change,
  trend = 'neutral',
  color = 'blue',
}) => {
  return (
    <div className={`border rounded-lg p-6 ${colorMap[color]}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{label}</p>
          <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
          {change !== undefined && (
            <p className={`text-xs font-semibold mt-2 ${
              trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600'
            }`}>
              {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} {Math.abs(change)}% from last period
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg bg-white/50 ${iconColorMap[color]}`}>
          {React.cloneElement(icon as React.ReactElement, { className: 'w-6 h-6' })}
        </div>
      </div>
    </div>
  );
};
