import React, { useState } from 'react';
import { Button } from '../../../components/ui/Button';
import { Input } from '../../../components/ui/Input';
import { Table, Thead, Tbody, Tr, Th, Td } from '../../../components/ui/Table';
import { XMarkIcon, XCircleIcon } from '@heroicons/react/24/outline';
import { transactionService } from '../../../services/transactionService';
import { inventoryService } from '../../../services/inventoryService';
import { useMutation, useQueryClient } from '@tanstack/react-query';

interface CartItem {
  sku: string;
  batch_number: string;
  nama_item: string;
  kategori: string;
  stok_tersedia: number;
  jumlah: number;
  harga: number;
  subtotal: number;
}

interface TransactionFormProps {
  transaction: any;
  onClose: () => void;
}

export const TransactionForm: React.FC<TransactionFormProps> = ({ 
  transaction,
  onClose 
}) => {
  const queryClient = useQueryClient();
  const [cart, setCart] = useState<CartItem[]>(
    transaction.items.map((item: any) => ({
      sku: item.sku,
      batch_number: item.batch_number,
      jumlah: item.jumlah,
      harga: item.harga_satuan,
      subtotal: item.subtotal,
      nama_item: '',
      kategori: '',
      stok_tersedia: 0
    }))
  );
  
  const [currentItem, setCurrentItem] = useState({
    sku: '',
    batch_number: '',
    jumlah: 1
  });
  
  const [itemDetails, setItemDetails] = useState<any>(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Load initial item details
  React.useEffect(() => {
    const loadItemDetails = async () => {
      try {
        const inventory = await inventoryService.getAllInventory();
        const updatedCart = await Promise.all(
          cart.map(async (item) => {
            const inventoryItem = inventory.find(
              (i) => i.sku === item.sku && i.batch_number === item.batch_number
            );
            if (inventoryItem) {
              return {
                ...item,
                nama_item: inventoryItem.nama_item,
                kategori: inventoryItem.kategori,
                stok_tersedia: inventoryItem.stok_tersedia + item.jumlah // Add current quantity to available stock
              };
            }
            return item;
          })
        );
        setCart(updatedCart);
      } catch (error) {
        console.error('Error loading item details:', error);
        setError('Failed to load item details');
      }
    };
    
    loadItemDetails();
  }, []);

  const updateTransaction = useMutation({
    mutationFn: async () => {
      const payload = {
        items: cart.map(item => ({
          sku: item.sku,
          batch_number: item.batch_number,
          jumlah: item.jumlah
        }))
      };
      return await transactionService.updateTransaction(transaction.id_transaksi, payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      onClose();
    },
    onError: (error: any) => {
      setError(error.response?.data?.message || 'Failed to update transaction');
    }
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setCurrentItem(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const searchItem = async () => {
    if (!currentItem.sku || !currentItem.batch_number) {
      setError('Please enter both SKU and Batch Number');
      return;
    }

    try {
      setIsLoading(true);
      setError('');
      const inventory = await inventoryService.getAllInventory();
      const item = inventory.find(
        i => i.sku === currentItem.sku && i.batch_number === currentItem.batch_number
      );

      if (!item) {
        setError('Item not found');
        return;
      }

      setItemDetails(item);
    } catch (err) {
      setError('Failed to fetch item details');
    } finally {
      setIsLoading(false);
    }
  };

  const addToCart = () => {
    if (!itemDetails) {
      setError('Please search for an item first');
      return;
    }

    const quantity = Number(currentItem.jumlah);
    if (isNaN(quantity) || quantity <= 0) {
      setError('Please enter a valid quantity');
      return;
    }

    if (quantity > itemDetails.stok_tersedia) {
      setError('Quantity exceeds available stock');
      return;
    }

    const subtotal = quantity * itemDetails.harga;

    const newItem: CartItem = {
      sku: itemDetails.sku,
      batch_number: itemDetails.batch_number,
      nama_item: itemDetails.nama_item,
      kategori: itemDetails.kategori,
      stok_tersedia: itemDetails.stok_tersedia,
      jumlah: quantity,
      harga: itemDetails.harga,
      subtotal
    };

    setCart(prev => [...prev, newItem]);
    setCurrentItem({ sku: '', batch_number: '', jumlah: 1 });
    setItemDetails(null);
  };

  const removeFromCart = (index: number) => {
    setCart(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (cart.length === 0) {
      setError('Cart is empty');
      return;
    }
    updateTransaction.mutate();
  };

  const totalAmount = cart.reduce((sum, item) => sum + item.subtotal, 0);

  return (
    <div className="w-full">
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">
          Edit Transaction #{transaction.id_transaksi}
        </h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-500"
        >
          <XMarkIcon className="h-6 w-6" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="p-6">
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              label="SKU"
              name="sku"
              value={currentItem.sku}
              onChange={handleInputChange}
              placeholder="Enter SKU"
            />
            <Input
              label="Batch Number"
              name="batch_number"
              value={currentItem.batch_number}
              onChange={handleInputChange}
              placeholder="Enter Batch Number"
            />
            <div className="flex items-end">
              <Button
                type="button"
                onClick={searchItem}
                disabled={!currentItem.sku || !currentItem.batch_number}
                isLoading={isLoading}
              >
                Search Item
              </Button>
            </div>
          </div>

          {itemDetails && (
            <div className="bg-gray-50 p-4 rounded-lg space-y-4">
              <h3 className="font-medium">Item Details</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Item Name
                  </label>
                  <p className="mt-1">{itemDetails.nama_item}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Available Stock
                  </label>
                  <p className="mt-1">{itemDetails.stok_tersedia}</p>
                </div>
                <Input
                  label="Quantity"
                  name="jumlah"
                  type="number"
                  value={currentItem.jumlah}
                  onChange={handleInputChange}
                  min="1"
                  max={itemDetails.stok_tersedia}
                />
                <div className="flex items-end">
                  <Button type="button" onClick={addToCart}>Add to Cart</Button>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 text-red-600 p-4 rounded-md">
              {error}
            </div>
          )}

          <div className="border rounded-lg overflow-hidden">
            <Table>
              <Thead>
                <Tr>
                  <Th>SKU</Th>
                  <Th>Batch</Th>
                  <Th>Item Name</Th>
                  <Th>Quantity</Th>
                  <Th>Price</Th>
                  <Th>Subtotal</Th>
                  <Th>Action</Th>
                </Tr>
              </Thead>
              <Tbody>
                {cart.map((item, index) => (
                  <Tr key={`${item.sku}-${item.batch_number}`}>
                    <Td>{item.sku}</Td>
                    <Td>{item.batch_number}</Td>
                    <Td>{item.nama_item}</Td>
                    <Td>{item.jumlah}</Td>
                    <Td>
                      {new Intl.NumberFormat('id-ID', {
                        style: 'currency',
                        currency: 'IDR'
                      }).format(item.harga)}
                    </Td>
                    <Td>
                      {new Intl.NumberFormat('id-ID', {
                        style: 'currency',
                        currency: 'IDR'
                      }).format(item.subtotal)}
                    </Td>
                    <Td>
                      <Button
                        type="button"
                        variant="secondary"
                        className="p-2 text-red-600 hover:bg-red-50"
                        onClick={() => removeFromCart(index)}
                      >
                        <XCircleIcon className="h-5 w-5" />
                      </Button>
                    </Td>
                  </Tr>
                ))}
                <Tr>
                  <Td colSpan={5} className="text-right font-medium">
                    Total Amount:
                  </Td>
                  <Td colSpan={2} className="font-medium">
                    {new Intl.NumberFormat('id-ID', {
                      style: 'currency',
                      currency: 'IDR'
                    }).format(totalAmount)}
                  </Td>
                </Tr>
              </Tbody>
            </Table>
          </div>

          <div className="mt-6 flex justify-end space-x-3 border-t border-gray-200 pt-6">
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
              disabled={updateTransaction.isPending}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={updateTransaction.isPending || cart.length === 0}
            >
              {updateTransaction.isPending ? 'Updating...' : 'Update Transaction'}
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
};