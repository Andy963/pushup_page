import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import { Activity } from '@/utils/utils';
import { IS_CHINESE } from '@/utils/const';

interface PushupChartProps {
  activities: Activity[];
}

const PushupChart: React.FC<PushupChartProps> = ({ activities }) => {
  // Process activities data for charts
  const chartData = activities
    .map((activity) => ({
      date: new Date(activity.start_date_local).toLocaleDateString(),
      pushups: Math.round(activity.distance),
      fullDate: new Date(activity.start_date_local),
    }))
    .sort((a, b) => a.fullDate.getTime() - b.fullDate.getTime())
    .slice(-30); // Show last 30 activities

  // Monthly aggregation
  const monthlyData = activities.reduce((acc, activity) => {
    const date = new Date(activity.start_date_local);
    const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    
    if (!acc[monthKey]) {
      acc[monthKey] = { month: monthKey, pushups: 0, count: 0 };
    }
    
    acc[monthKey].pushups += Math.round(activity.distance);
    acc[monthKey].count += 1;
    
    return acc;
  }, {} as Record<string, { month: string; pushups: number; count: number }>);

  const monthlyChartData = Object.values(monthlyData).slice(-12); // Last 12 months

  if (activities.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 mb-8">
        <h3 className="text-lg font-semibold mb-4">
          {IS_CHINESE ? '俯卧撑进度' : 'Pushup Progress'}
        </h3>
        <p className="text-gray-500 text-center">
          {IS_CHINESE ? '暂无数据可显示' : 'No data to display'}
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-6 mb-8">
      <h3 className="text-lg font-semibold mb-6">
        {IS_CHINESE ? '俯卧撑进度' : 'Pushup Progress'}
      </h3>
      
      {/* Daily Progress Chart */}
      <div className="mb-8">
        <h4 className="text-md font-medium mb-4">
          {IS_CHINESE ? '最近30次活动' : 'Last 30 Activities'}
        </h4>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 12 }}
              interval="preserveStartEnd"
            />
            <YAxis 
              label={{ 
                value: IS_CHINESE ? '俯卧撑次数' : 'Pushups', 
                angle: -90, 
                position: 'insideLeft' 
              }}
            />
            <Tooltip 
              labelFormatter={(value) => `${IS_CHINESE ? '日期' : 'Date'}: ${value}`}
              formatter={(value) => [value, IS_CHINESE ? '俯卧撑' : 'Pushups']}
            />
            <Line 
              type="monotone" 
              dataKey="pushups" 
              stroke="#47b8e0" 
              strokeWidth={2}
              dot={{ fill: '#47b8e0', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Monthly Summary */}
      {monthlyChartData.length > 0 && (
        <div>
          <h4 className="text-md font-medium mb-4">
            {IS_CHINESE ? '月度汇总' : 'Monthly Summary'}
          </h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="month" 
                tick={{ fontSize: 12 }}
              />
              <YAxis 
                label={{ 
                  value: IS_CHINESE ? '总俯卧撑' : 'Total Pushups', 
                  angle: -90, 
                  position: 'insideLeft' 
                }}
              />
              <Tooltip 
                labelFormatter={(value) => `${IS_CHINESE ? '月份' : 'Month'}: ${value}`}
                formatter={(value, name) => [
                  value,
                  name === 'pushups' ? (IS_CHINESE ? '总俯卧撑' : 'Total Pushups') : (IS_CHINESE ? '活动次数' : 'Activities')
                ]}
              />
              <Bar dataKey="pushups" fill="#47b8e0" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default PushupChart;