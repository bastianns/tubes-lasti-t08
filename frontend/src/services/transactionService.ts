// src/services/transactionService.ts
import api from '../utils/axios';

// src/services/transactionService.ts

interface TransactionItem {
  sku: string;
  nama_item: string;
  batch_number: string;
  jumlah: number;
  harga_satuan: number;
  subtotal: number;
}

export interface Transaction {
  id_transaksi: number;
  total_amount: number;
  waktu_transaksi: string;
  items: TransactionItem[];
}

export const transactionService = {
  getAllTransactions: async () => {
    const response = await api.get<Transaction[]>('/transactions');
    return response.data;
  },

  createTransaction: async (data: { items: { sku: string; batch_number: string; jumlah: number; }[] }) => {
    const response = await api.post<Transaction>('/transactions', data);
    return response.data;
  },

  updateTransaction: async (transactionId: number, data: { items: { sku: string; batch_number: string; jumlah: number; }[] }) => {
    const response = await api.put<Transaction>(`/transactions/${transactionId}`, data);
    return response.data;
  },

  deleteTransaction: async (transactionId: number) => {
    const response = await api.delete(`/transactions/${transactionId}`);
    return response.data;
  }
};