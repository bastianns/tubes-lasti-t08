// src/pages/dashboard/DashboardPage.tsx
import { useEffect, useState } from 'react';
import { subMonths, format } from 'date-fns';
import { dashboardApi, LowStockItem } from './api/dashboardApi';
import { SalesChart } from './components/SalesChart';
import { StockStatus } from './components/StockStatus';

interface ChartData {
  date: string;
  sales: number;
}

export const DashboardPage = () => {
  const [salesData, setSalesData] = useState<ChartData[]>([]);
  const [lowStockItems, setLowStockItems] = useState<LowStockItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Fetch sales data for last 12 months
        const currentDate = new Date();
        const monthlyData: ChartData[] = [];

        for (let i = 0; i < 12; i++) {
          const date = subMonths(currentDate, i);
          const year = date.getFullYear();
          const month = date.getMonth() + 1;

          const salesResponse = await dashboardApi.getMonthlySales(year, month);
          monthlyData.unshift({
            date: format(date, 'MMM yyyy'),
            sales: salesResponse.total_sales
          });
        }

        setSalesData(monthlyData);

        // Fetch low stock items
        const lowStockResponse = await dashboardApi.getLowStockItems();
        setLowStockItems(lowStockResponse);

      } catch (err) {
        setError('Failed to fetch dashboard data');
        console.error('Error fetching dashboard data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []); // Empty dependency array means this runs once on mount

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 text-red-600 p-4 rounded-md">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-8 px-4">
      <SalesChart data={salesData} />
      <StockStatus items={lowStockItems} />
    </div>
  );
};