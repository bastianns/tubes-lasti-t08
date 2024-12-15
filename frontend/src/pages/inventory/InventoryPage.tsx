// src/pages/inventory/InventoryPage.tsx
import React, { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  useReactTable,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
} from "@tanstack/react-table";
import { format } from "date-fns";
import { PencilIcon, TrashIcon } from "@heroicons/react/24/outline";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Table, Thead, Tbody, Tr, Th, Td } from "../../components/ui/Table";
import { Modal } from "../../components/ui/Modal";
import { InventoryForm } from "./components/InventoryForm";
import {
  InventoryItem,
  inventoryService,
} from "../../services/inventoryService";
import { Card } from "../../components/ui/Card";

const columnHelper = createColumnHelper<InventoryItem>();

const InventoryPage = () => {
  const queryClient = useQueryClient();
  const [searchInput, setSearchInput] = useState(""); 
  const [searchQuery, setSearchQuery] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<InventoryItem | undefined>();
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const {
    data: inventory = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ["inventory", searchQuery],
    queryFn: () =>
      inventoryService.getAllInventory({
        search: searchQuery,
      }),
  });

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchInput(e.target.value);
  };

  const handleSearchSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSearchQuery(searchInput);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      setSearchQuery(searchInput);
    }
  };

  const handleAddNew = () => {
    setSelectedItem(undefined);
    setIsModalOpen(true);
  };

  const handleEdit = (item: InventoryItem) => {
    setSelectedItem(item);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedItem(undefined);
  };

  const handleDelete = async (item: InventoryItem) => {
    if (window.confirm(`Are you sure you want to delete ${item.nama_item}?`)) {
      try {
        await inventoryService.deleteInventory(item.sku, item.batch_number);
        queryClient.invalidateQueries({ queryKey: ["inventory"] });
        setDeleteError(null);
      } catch (error: any) {
        console.error("Error deleting inventory:", error);
        setDeleteError(
          error.response?.data?.message || 
          error.response?.data?.details || 
          "Failed to delete inventory"
        );
      }
    }
  };

  const columns = [
    columnHelper.accessor("sku", {
      header: "SKU",
      cell: (info) => info.getValue(),
    }),
    columnHelper.accessor("batch_number", {
      header: "Batch Number",
      cell: (info) => info.getValue(),
    }),
    columnHelper.accessor("nama_item", {
      header: "Item Name",
      cell: (info) => info.getValue(),
    }),
    columnHelper.accessor("kategori", {
      header: "Category",
      cell: (info) => info.getValue() || "-",
    }),
    columnHelper.accessor("stok_tersedia", {
      header: "Available Stock",
      cell: (info) => info.getValue().toLocaleString(),
    }),
    columnHelper.accessor("stok_minimum", {
      header: "Minimum Stock",
      cell: (info) => info.getValue().toLocaleString(),
    }),
    columnHelper.accessor("harga", {
      header: "Price",
      cell: (info) =>
        new Intl.NumberFormat("id-ID", {
          style: "currency",
          currency: "IDR",
        }).format(info.getValue()),
    }),
    columnHelper.accessor("waktu_pembaruan", {
      header: "Last Updated",
      cell: (info) => {
        const value = info.getValue();
        if (!value) return "-";
        return format(new Date(value), "dd MMM yyyy HH:mm");
      },
    }),
    columnHelper.display({
      id: "actions",
      header: "Actions",
      cell: (info) => (
        <div className="flex items-center space-x-2">
          <Button
            variant="secondary"
            className="p-2"
            onClick={() => handleEdit(info.row.original)}
          >
            <PencilIcon className="h-4 w-4" />
          </Button>
          <Button
            variant="secondary"
            className="p-2 text-red-600 hover:bg-red-50"
            onClick={() => handleDelete(info.row.original)}
          >
            <TrashIcon className="h-4 w-4" />
          </Button>
        </div>
      ),
    }),
  ];

  const table = useReactTable({
    data: inventory,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: {
      pagination: {
        pageSize: 10,
      },
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 p-4 rounded-lg text-red-600">
        An error occurred while fetching inventory data
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4">
      <Card>
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold text-gray-900">Inventory</h1>
          <Button onClick={handleAddNew}>Add New Item</Button>
        </div>

        {deleteError && (
          <div className="mb-4 p-4 bg-red-50 text-red-600 rounded-lg">
            {deleteError}
          </div>
        )}

        <form onSubmit={handleSearchSubmit} className="flex justify-between items-center gap-2 mb-6">
          <div className="flex flex-col flex-1 max-w-sm">
            <div className="flex gap-2">
              <Input
                placeholder="Search Item Name / SKU"
                value={searchInput}
                onChange={handleSearchChange}
                onKeyPress={handleKeyPress}
              />
              <Button type="submit" variant="secondary">
                Search
              </Button>
            </div>
            <p className="text-sm text-gray-500 mt-1">
              Press Enter or Click Search 
            </p>
          </div>
        </form>

        <div className="rounded-lg border border-gray-200 overflow-hidden">
          <Table>
            <Thead>
              {table.getHeaderGroups().map((headerGroup) => (
                <Tr key={headerGroup.id} isHeader>
                  {headerGroup.headers.map((header) => (
                    <Th key={header.id}>
                      {flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                    </Th>
                  ))}
                </Tr>
              ))}
            </Thead>
            <Tbody>
              {table.getRowModel().rows?.length ? (
                table.getRowModel().rows.map((row) => (
                  <Tr key={row.id}>
                    {row.getVisibleCells().map((cell) => (
                      <Td key={cell.id}>
                        {flexRender(
                          cell.column.columnDef.cell,
                          cell.getContext()
                        )}
                      </Td>
                    ))}
                  </Tr>
                ))
              ) : (
                <Tr>
                  <Td colSpan={columns.length} className="text-center">
                    No results found
                  </Td>
                </Tr>
              )}
            </Tbody>
          </Table>
        </div>

        <div className="flex items-center justify-between mt-4">
          <div className="text-sm text-gray-700">
            Page {table.getState().pagination.pageIndex + 1} of{' '}
            {table.getPageCount()}
          </div>
          <div className="space-x-2">
            <Button
              variant="secondary"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
            >
              Previous
            </Button>
            <Button
              variant="secondary"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
            >
              Next
            </Button>
          </div>
        </div>
      </Card>

      <Modal isOpen={isModalOpen} onClose={handleCloseModal}>
        <InventoryForm
          initialData={selectedItem}
          onClose={handleCloseModal}
        />
      </Modal>
    </div>
  );
};

export default InventoryPage;