// src/pages/dashboard/components/StockStatus.tsx
import clsx from 'clsx';
import { LowStockItem } from '../api/dashboardApi';

interface Props {
  items: LowStockItem[];
}

export const StockStatus = ({ items }: Props) => {
  const getStockLevelColor = (item: LowStockItem) => {
    if (item.stok_tersedia === 0) return 'bg-red-100 border-red-500 text-red-700';
    if (item.stok_tersedia < item.stok_minimum) return 'bg-yellow-100 border-yellow-500 text-yellow-700';
    return 'bg-green-100 border-green-500 text-green-700';
  };

  // Helper function to truncate text
  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return `${text.substring(0, maxLength)}...`;
  };

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-gray-800">Inventory Status</h2>
      
      {items.length === 0 ? (
        <div className="bg-green-100 border border-green-500 text-green-700 px-6 py-4 rounded-lg">
          <div className="flex items-center">
            <svg className="h-5 w-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <p className="font-medium">All items are well stocked</p>
          </div>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <div
              key={item.sku}
              className={clsx(
                'rounded-lg border p-4 transition-all overflow-hidden',
                getStockLevelColor(item)
              )}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1 min-w-0"> {/* Add min-w-0 to allow text truncation */}
                  <h3 className="font-semibold truncate" title={item.nama_item}>
                    {truncateText(item.nama_item, 25)}
                  </h3>
                  <p className="text-sm mt-1 truncate">SKU: {item.sku}</p>
                </div>
                <div className="text-right ml-4 flex-shrink-0">
                  <p className="text-2xl font-bold">{item.stok_tersedia}</p>
                  <p className="text-sm">of {item.stok_minimum} min</p>
                </div>
              </div>
              <div className="mt-4">
                <div className="w-full bg-white rounded-full h-2.5">
                  <div 
                    className="h-2.5 rounded-full transition-all"
                    style={{
                      width: `${Math.min((item.stok_tersedia / item.stok_minimum) * 100, 100)}%`,
                      backgroundColor: item.stok_tersedia === 0 ? '#EF4444' : 
                        item.stok_tersedia < item.stok_minimum ? '#F59E0B' : '#10B981'
                    }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};