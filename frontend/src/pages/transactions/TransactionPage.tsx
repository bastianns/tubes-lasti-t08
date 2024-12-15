// src/pages/transactions/TransactionPage.tsx
import React, { useState } from "react";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Button } from "../../components/ui/Button";
import { Table, Thead, Tbody, Tr, Th, Td } from "../../components/ui/Table";
import { inventoryService } from "../../services/inventoryService";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { format, parseISO, isWithinInterval, addDays } from "date-fns";
import {
  transactionService,
  Transaction,
} from "../../services/transactionService";
import { TransactionForm } from "./components/TransactionForm";
import {
  TrashIcon,
  PlusCircleIcon,
  ClockIcon,
  PencilIcon,
} from "@heroicons/react/24/outline";
import { Modal } from "../../components/ui/Modal";

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

type Mode = "add" | "history";

const ITEMS_PER_PAGE = 10;

const TransactionPage = () => {
  const [mode, setMode] = useState<Mode>("add");
  const [cart, setCart] = useState<CartItem[]>([]);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedTransaction, setSelectedTransaction] =
    useState<Transaction | null>(null);
  const [currentItem, setCurrentItem] = useState({
    sku: "",
    batch_number: "",
    jumlah: 1,
  });
  const [itemDetails, setItemDetails] = useState<any>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const queryClient = useQueryClient();

  const [filters, setFilters] = useState({
    startDate: "",
    endDate: "",
    transactionId: "",
  });
  const [currentPage, setCurrentPage] = useState(0);

  const handleKeyPress = async (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      if (!itemDetails) {
        await searchItem();
      } else {
        addToCart();
      }
    }
  };

  // Fetch transaction history
  const { data: allTransactions = [], isLoading: isLoadingHistory } = useQuery({
    queryKey: ["transactions"],
    queryFn: transactionService.getAllTransactions,
    enabled: mode === "history",
    select: (data) => {
      // Sort transactions by date in descending order
      return [...data].sort((a, b) => {
        const dateA = new Date(a.waktu_transaksi || 0);
        const dateB = new Date(b.waktu_transaksi || 0);
        return dateB.getTime() - dateA.getTime();
      });
    },
  });

  // Filter and paginate transactions
  const filteredTransactions = React.useMemo(() => {
    return allTransactions.filter((transaction) => {
      // Filter by transaction ID
      if (
        filters.transactionId &&
        !transaction.id_transaksi.toString().includes(filters.transactionId)
      ) {
        return false;
      }

      // Filter by date range
      if (filters.startDate && filters.endDate) {
        const transactionDate = new Date(transaction.waktu_transaksi);
        const startDate = parseISO(filters.startDate);
        const endDate = addDays(parseISO(filters.endDate), 1);

        try {
          if (
            !isWithinInterval(transactionDate, {
              start: startDate,
              end: endDate,
            })
          ) {
            return false;
          }
        } catch (error) {
          // Handle invalid date ranges
          return true;
        }
      }

      return true;
    });
  }, [allTransactions, filters]);

  // Calculate pagination
  const pageCount = Math.ceil(filteredTransactions.length / ITEMS_PER_PAGE);
  const paginatedTransactions = filteredTransactions.slice(
    currentPage * ITEMS_PER_PAGE,
    (currentPage + 1) * ITEMS_PER_PAGE
  );

  // Handle filter changes
  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFilters((prev) => ({
      ...prev,
      [name]: value,
    }));
    setCurrentPage(0); // Reset to first page when filters change
  };

  // Clear filters
  const handleClearFilters = () => {
    setFilters({
      startDate: "",
      endDate: "",
      transactionId: "",
    });
    setCurrentPage(0);
  };

  const createTransaction = useMutation({
    mutationFn: async (cart: CartItem[]) => {
      const payload = {
        items: cart.map((item) => ({
          sku: item.sku,
          batch_number: item.batch_number,
          jumlah: item.jumlah,
        })),
      };
      return await transactionService.createTransaction(payload);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      setCart([]);
      setError("");
    },
    onError: (error: any) => {
      setError(error.response?.data?.message || "Failed to create transaction");
    },
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setCurrentItem((prev) => ({
      ...prev,
      [name]: value,
    }));
    setError("");
  };

  const searchItem = async () => {
    if (!currentItem.sku || !currentItem.batch_number) {
      setError("Please enter both SKU and Batch Number");
      return;
    }

    try {
      setIsLoading(true);
      setError("");
      const inventory = await inventoryService.getAllInventory();
      const item = inventory.find(
        (i) =>
          i.sku === currentItem.sku &&
          i.batch_number === currentItem.batch_number
      );

      if (!item) {
        setError("Item not found");
        setItemDetails(null);
        return;
      }

      setItemDetails(item);
    } catch (err) {
      setError("Failed to fetch item details");
    } finally {
      setIsLoading(false);
    }
  };

  const addToCart = () => {
    if (!itemDetails) {
      setError("Please search for an item first");
      return;
    }

    const quantity = Number(currentItem.jumlah);
    if (isNaN(quantity) || quantity <= 0) {
      setError("Please enter a valid quantity");
      return;
    }

    if (quantity > itemDetails.stok_tersedia) {
      setError("Quantity exceeds available stock");
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
      subtotal,
    };

    setCart((prev) => [...prev, newItem]);
    setCurrentItem({ sku: "", batch_number: "", jumlah: 1 });
    setItemDetails(null);
  };

  const removeFromCart = (index: number) => {
    setCart((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = () => {
    if (cart.length === 0) {
      setError("Cart is empty");
      return;
    }
    createTransaction.mutate(cart);
  };

  const totalAmount = cart.reduce((sum, item) => sum + item.subtotal, 0);

  return (
    <div className="space-y-6">
      {/* Mode Toggle */}
      <div className="flex space-x-4 bg-white p-4 rounded-lg shadow">
        <Button
          variant={mode === "add" ? "primary" : "secondary"}
          onClick={() => setMode("add")}
          className="flex items-center"
        >
          <PlusCircleIcon className="h-5 w-5 mr-2" />
          Add Transaction
        </Button>
        <Button
          variant={mode === "history" ? "primary" : "secondary"}
          onClick={() => setMode("history")}
          className="flex items-center"
        >
          <ClockIcon className="h-5 w-5 mr-2" />
          Transaction History
        </Button>
      </div>

      {mode === "add" ? (
        <Card>
          <div className="space-y-6">
            <h1 className="text-2xl font-bold text-gray-900">
              Add Transaction
            </h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Input
                label="SKU"
                name="sku"
                value={currentItem.sku}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
                placeholder="Enter SKU"
              />
              <Input
                label="Batch Number"
                name="batch_number"
                value={currentItem.batch_number}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
                placeholder="Enter Batch Number"
              />
              <div className="flex items-end">
                <Button
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
                      Category
                    </label>
                    <p className="mt-1">{itemDetails.kategori}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Available Stock
                    </label>
                    <p className="mt-1">{itemDetails.stok_tersedia}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Price
                    </label>
                    <p className="mt-1">
                      {new Intl.NumberFormat("id-ID", {
                        style: "currency",
                        currency: "IDR",
                      }).format(itemDetails.harga)}
                    </p>
                  </div>
                  <Input
                    label="Quantity"
                    name="jumlah"
                    type="number"
                    value={currentItem.jumlah}
                    onChange={handleInputChange}
                    onKeyPress={handleKeyPress}
                    min="1"
                    max={itemDetails.stok_tersedia}
                  />
                  <div className="flex items-end">
                    <Button onClick={addToCart}>Add to Cart</Button>
                  </div>
                </div>
              </div>
            )}

            {error && (
              <div className="bg-red-50 text-red-600 p-4 rounded-md">
                {error}
              </div>
            )}

            {cart.length > 0 && (
              <div className="space-y-4">
                <h3 className="font-medium">Cart Items</h3>
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
                            {new Intl.NumberFormat("id-ID", {
                              style: "currency",
                              currency: "IDR",
                            }).format(item.harga)}
                          </Td>
                          <Td>
                            {new Intl.NumberFormat("id-ID", {
                              style: "currency",
                              currency: "IDR",
                            }).format(item.subtotal)}
                          </Td>
                          <Td>
                            <Button
                              variant="secondary"
                              className="p-2 text-red-600 hover:bg-red-50"
                              onClick={() => removeFromCart(index)}
                            >
                              <TrashIcon className="h-5 w-5" />
                            </Button>
                          </Td>
                        </Tr>
                      ))}
                      <Tr>
                        <Td colSpan={5} className="text-right font-medium">
                          Total Amount:
                        </Td>
                        <Td colSpan={2} className="font-medium">
                          {new Intl.NumberFormat("id-ID", {
                            style: "currency",
                            currency: "IDR",
                          }).format(totalAmount)}
                        </Td>
                      </Tr>
                    </Tbody>
                  </Table>
                </div>

                <div className="flex justify-end">
                  <Button
                    onClick={handleSubmit}
                    disabled={cart.length === 0}
                    isLoading={createTransaction.isPending}
                  >
                    Submit Transaction
                  </Button>
                </div>
              </div>
            )}
          </div>
        </Card>
      ) : (
        <Card>
          <div className="space-y-6">
            <h1 className="text-2xl font-bold text-gray-900">
              Transaction History
            </h1>

            {/* Add Filters */}
            <div className="bg-gray-50 p-4 rounded-lg space-y-4">
              <h3 className="font-medium">Filters</h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Input
                  label="Start Date"
                  type="date"
                  name="startDate"
                  value={filters.startDate}
                  onChange={handleFilterChange}
                />
                <Input
                  label="End Date"
                  type="date"
                  name="endDate"
                  value={filters.endDate}
                  onChange={handleFilterChange}
                />
                <Input
                  label="Transaction ID"
                  name="transactionId"
                  value={filters.transactionId}
                  onChange={handleFilterChange}
                  placeholder="Search Transaction ID"
                />
                <div className="flex items-end">
                  <Button variant="secondary" onClick={handleClearFilters}>
                    Clear Filters
                  </Button>
                </div>
              </div>
            </div>

            {isLoadingHistory ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : (
              <>
                <div className="border rounded-lg overflow-hidden">
                  <Table>
                    <Thead>
                      <Tr>
                        <Th>Transaction ID</Th>
                        <Th>Date</Th>
                        <Th>Total Amount</Th>
                        <Th>Items</Th>
                        <Th>Actions</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {paginatedTransactions.length > 0 ? (
                        paginatedTransactions.map((transaction) => (
                          <Tr key={transaction.id_transaksi}>
                            <Td>{transaction.id_transaksi}</Td>
                            <Td>
                              {transaction.waktu_transaksi
                                ? format(
                                    new Date(transaction.waktu_transaksi),
                                    "dd MMM yyyy HH:mm"
                                  )
                                : "-"}
                            </Td>
                            <Td>
                              {new Intl.NumberFormat("id-ID", {
                                style: "currency",
                                currency: "IDR",
                              }).format(transaction.total_amount)}
                            </Td>
                            <Td>
                              <div className="max-w-md">
                                {transaction.items.map((item, index) => (
                                  <div
                                    key={`${item.sku}-${item.batch_number}`}
                                    className="text-sm"
                                  >
                                    {index + 1}. {item.sku} ({item.jumlah}{" "}
                                    units)
                                  </div>
                                ))}
                              </div>
                            </Td>
                            <Td>
                              <div className="flex items-center space-x-2">
                                <Button
                                  variant="secondary"
                                  className="p-2"
                                  onClick={() => {
                                    setSelectedTransaction(transaction);
                                    setIsEditModalOpen(true);
                                  }}
                                >
                                  <PencilIcon className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="secondary"
                                  className="p-2 text-red-600 hover:bg-red-50"
                                  onClick={() => {
                                    if (
                                      window.confirm(
                                        "Are you sure you want to delete this transaction?"
                                      )
                                    ) {
                                      transactionService
                                        .deleteTransaction(
                                          transaction.id_transaksi
                                        )
                                        .then(() => {
                                          queryClient.invalidateQueries({
                                            queryKey: ["transactions"],
                                          });
                                        })
                                        .catch((error) => {
                                          console.error(
                                            "Error deleting transaction:",
                                            error
                                          );
                                          setError(
                                            "Failed to delete transaction"
                                          );
                                        });
                                    }
                                  }}
                                >
                                  <TrashIcon className="h-4 w-4" />
                                </Button>
                              </div>
                            </Td>
                          </Tr>
                        ))
                      ) : (
                        <Tr>
                          <Td colSpan={5} className="text-center py-8">
                            No transactions found
                          </Td>
                        </Tr>
                      )}
                    </Tbody>
                  </Table>
                </div>

                {/* Pagination */}
                <div className="flex items-center justify-between mt-4">
                  <div className="text-sm text-gray-700">
                    Showing {paginatedTransactions.length} of{" "}
                    {filteredTransactions.length} transactions
                  </div>
                  <div className="space-x-2">
                    <Button
                      variant="secondary"
                      onClick={() =>
                        setCurrentPage((prev) => Math.max(0, prev - 1))
                      }
                      disabled={currentPage === 0}
                    >
                      Previous
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={() =>
                        setCurrentPage((prev) =>
                          Math.min(pageCount - 1, prev + 1)
                        )
                      }
                      disabled={currentPage >= pageCount - 1}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              </>
            )}
          </div>
        </Card>
      )}

      {/* Edit Transaction Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false);
          setSelectedTransaction(null);
        }}
      >
        {selectedTransaction && (
          <TransactionForm
            transaction={selectedTransaction}
            onClose={() => {
              setIsEditModalOpen(false);
              setSelectedTransaction(null);
            }}
          />
        )}
      </Modal>
    </div>
  );
};

export default TransactionPage;
