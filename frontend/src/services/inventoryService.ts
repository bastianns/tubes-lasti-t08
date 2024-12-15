// src/services/inventoryService.ts
import api from '../utils/axios';

export interface InventoryItem {
  sku: string;
  batch_number: string;
  nama_item: string;
  kategori: string;
  stok_tersedia: number;
  stok_minimum: number;
  harga: number;
  waktu_pembaruan?: string;
}

export const inventoryService = {
  getAllInventory: async (params?: { 
    category?: string; 
    search?: string;
  }) => {
    const response = await api.get<InventoryItem[]>('/inventory', { params });
    return response.data;
  },

  createInventory: async (data: Omit<InventoryItem, 'waktu_pembaruan'>) => {
    try {
      console.log('Sending create inventory request with data:', data);
      const response = await api.post<InventoryItem>('/inventory', data);
      console.log('Create inventory response:', response);
      return response.data;
    } catch (error: any) {
      console.error('Create inventory error in service:', {
        error,
        response: error.response?.data,
        status: error.response?.status,
        requestData: data
      });
      throw error;
    }
  },

  updateInventory: async (sku: string, batch_number: string, data: Partial<InventoryItem>) => {
    const response = await api.put<InventoryItem>(`/inventory/${sku}/${batch_number}`, data);
    return response.data;
  },

  deleteInventory: async (sku: string, batch_number: string) => {
    const response = await api.delete(`/inventory/${sku}/${batch_number}`);
    return response.data;
  }
};