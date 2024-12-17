// src/pages/dashboard/components/SalesChart.tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface ChartData {
  date: string;
  sales: number;
}

interface Props {
  data: ChartData[];
}

export const SalesChart = ({ data }: Props) => {
  const formatToRupiah = (value: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 max-w-5xl mx-auto">
      <h2 className="text-xl font-semibold text-gray-800 mb-6">Monthly Sales Overview</h2>
      <div className="h-52">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              dataKey="date" 
              stroke="#6B7280"
              fontSize={12}
              tickLine={false}
            />
            <YAxis 
              stroke="#6B7280"
              fontSize={12}
              tickLine={false}
              tickFormatter={formatToRupiah}
            />
            <Tooltip
              contentStyle={{ 
                backgroundColor: '#FFF',
                border: '1px solid #E5E7EB',
                borderRadius: '0.5rem'
              }}
              formatter={(value: number) => [formatToRupiah(value), 'Sales']}
            />
            <Line 
              type="monotone" 
              dataKey="sales" 
              stroke="#2563EB"
              strokeWidth={2}
              dot={{ r: 4, fill: '#2563EB' }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};