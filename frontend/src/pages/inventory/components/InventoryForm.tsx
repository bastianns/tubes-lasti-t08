import React, { useState } from "react";
import { Button } from "../../../components/ui/Button";
import { Input } from "../../../components/ui/Input";
import {
  inventoryService,
  InventoryItem,
} from "../../../services/inventoryService";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { XMarkIcon } from "@heroicons/react/24/outline";

interface InventoryFormData {
  sku: string;
  batch_number: string;
  nama_item: string;
  kategori: string;
  stok_tersedia: number | null;
  stok_minimum: number | null;
  harga: number | null;
}

interface InventoryFormProps {
  initialData?: InventoryItem;
  onClose: () => void;
}

export const InventoryForm: React.FC<InventoryFormProps> = ({
  initialData,
  onClose,
}) => {
  const queryClient = useQueryClient();
  const isEditing = !!initialData;
  const [errors, setErrors] = useState<
    Partial<Record<keyof InventoryFormData, string>>
  >({});
  const [formData, setFormData] = useState<InventoryFormData>(
    initialData || {
      sku: "",
      batch_number: "",
      nama_item: "",
      kategori: "",
      stok_tersedia: null,
      stok_minimum: null,
      harga: null,
    }
  );

  // Format number to IDR currency
  const formatToIDR = (value: number | null): string => {
    if (value === null) return "";
    return new Intl.NumberFormat("id-ID", {
      style: "currency",
      currency: "IDR",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  // Parse IDR string back to number
  const parseIDR = (value: string): number | null => {
    // Remove currency symbol, dots, and commas
    const numStr = value.replace(/[Rp.,\s]/g, "");
    if (numStr === "") return null;
    const parsed = parseInt(numStr, 10);
    return isNaN(parsed) ? null : parsed;
  };

  const createMutation = useMutation({
    mutationFn: (data: InventoryFormData) => {
      // Convert null values to 0 before sending to API
      const submitData = {
        ...data,
        stok_tersedia: data.stok_tersedia ?? 0,
        stok_minimum: data.stok_minimum ?? 0,
        harga: data.harga ?? 0,
      };
      return inventoryService.createInventory(submitData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
      onClose();
    },
  });

  const updateMutation = useMutation({
    mutationFn: (data: InventoryFormData) => {
      // Convert null values to 0 before sending to API
      const submitData = {
        ...data,
        stok_tersedia: data.stok_tersedia ?? 0,
        stok_minimum: data.stok_minimum ?? 0,
        harga: data.harga ?? 0,
      };
      return inventoryService.updateInventory(
        submitData.sku,
        submitData.batch_number,
        submitData
      );
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
      onClose();
    },
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;

    if (type === "number") {
      // For empty input, set to null
      if (value === "") {
        setFormData((prev) => ({
          ...prev,
          [name]: null,
        }));
        return;
      }

      const numValue = parseFloat(value);
      if (isNaN(numValue)) return;

      setFormData((prev) => ({
        ...prev,
        [name]: numValue,
      }));
    } else if (name === "harga") {
      const numericValue = parseIDR(value);
      setFormData((prev) => ({
        ...prev,
        harga: numericValue,
      }));
    } else {
      setFormData((prev) => ({
        ...prev,
        [name]: value,
      }));
    }

    if (errors[name as keyof InventoryFormData]) {
      setErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };

  const validateForm = () => {
    const newErrors: Partial<Record<keyof InventoryFormData, string>> = {};

    if (!formData.sku) newErrors.sku = "SKU is required";
    if (!formData.batch_number) newErrors.batch_number = "Batch number is required";
    if (!formData.nama_item) newErrors.nama_item = "Item name is required";
    if (!formData.kategori) newErrors.kategori = "Category is required";

    // Only validate numeric fields if they have a value and it's negative
    if (formData.stok_tersedia !== null && formData.stok_tersedia < 0) {
      newErrors.stok_tersedia = "Stock cannot be negative";
    }
    if (formData.stok_minimum !== null && formData.stok_minimum < 0) {
      newErrors.stok_minimum = "Minimum stock cannot be negative";
    }
    if (formData.harga !== null && formData.harga < 0) {
      newErrors.harga = "Price cannot be negative";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    try {
      if (isEditing) {
        await updateMutation.mutateAsync(formData);
      } else {
        await createMutation.mutateAsync(formData);
      }
    } catch (error) {
      console.error("Form submission error:", error);
    }
  };

  const isError = createMutation.isError || updateMutation.isError;
  const error = createMutation.error || updateMutation.error;
  const isSubmitting = createMutation.isPending || updateMutation.isPending;

  return (
    <div className="w-full">
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">
          {isEditing ? "Edit Inventory Item" : "Add New Inventory Item"}
        </h2>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-500">
          <XMarkIcon className="h-6 w-6" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="p-6">
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              name="sku"
              label="SKU"
              value={formData.sku}
              onChange={handleChange}
              disabled={isEditing}
              error={errors.sku}
              required
              placeholder="Enter SKU"
            />

            <Input
              name="batch_number"
              label="Batch Number"
              value={formData.batch_number}
              onChange={handleChange}
              disabled={isEditing}
              error={errors.batch_number}
              required
              placeholder="Enter Batch Number"
            />
          </div>

          <Input
            name="nama_item"
            label="Item Name"
            value={formData.nama_item}
            onChange={handleChange}
            error={errors.nama_item}
            required
            placeholder="Enter Item Name"
          />

          <Input
            name="kategori"
            label="Category"
            value={formData.kategori}
            onChange={handleChange}
            error={errors.kategori}
            required
            placeholder="Enter Category"
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              name="stok_tersedia"
              type="number"
              label="Available Stock"
              onChange={handleChange}
              placeholder="Enter Available Stock"
              value={formData.stok_tersedia === null ? "" : formData.stok_tersedia}
              error={errors.stok_tersedia}
              required
              min="0"
            />

            <Input
              name="stok_minimum"
              type="number"
              label="Minimum Stock"
              onChange={handleChange}
              value={formData.stok_minimum === null ? "" : formData.stok_minimum}
              error={errors.stok_minimum}
              required
              min="0"
              placeholder="Enter Minimum Stock"
            />
          </div>

          <Input
            name="harga"
            label="Price"
            value={formatToIDR(formData.harga)}
            onChange={handleChange}
            error={errors.harga}
            required
            placeholder="Enter Price"
          />

          {isError && (
            <div className="p-4 bg-red-50 text-red-700 rounded-md">
              {error instanceof Error
                ? error.message
                : "An error occurred during submission"}
            </div>
          )}
        </div>

        <div className="mt-6 flex justify-end space-x-3 border-t border-gray-200 pt-6">
          <Button
            type="button"
            variant="secondary"
            onClick={onClose}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting
              ? "Saving..."
              : isEditing
              ? "Update Item"
              : "Create Item"}
          </Button>
        </div>
      </form>
    </div>
  );
};