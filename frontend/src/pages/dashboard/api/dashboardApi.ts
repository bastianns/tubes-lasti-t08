// src/pages/dashboard/api/dashboardApi.ts
import api from '../../../utils/axios';

export interface MonthlySales {
  month: number;
  year: number;
  total_sales: number;
}

export interface LowStockItem {
  sku: string;
  nama_item: string;
  stok_tersedia: number;
  stok_minimum: number;
}

export const dashboardApi = {
  getMonthlySales: async (year: number, month: number) => {
    try {
      const response = await api.get<MonthlySales>(`/transactions/monthly-sales?year=${year}&month=${month}`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to fetch monthly sales:', error.response?.data || error.message);
      throw error;
    }
  },

  getLowStockItems: async () => {
    try {
      const response = await api.get<LowStockItem[]>('/inventory/low-stock');
      return response.data;
    } catch (error: any) {
      console.error('Failed to fetch low stock items:', error.response?.data || error.message);
      throw error;
    }
  }
};