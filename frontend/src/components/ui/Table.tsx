// src/components/ui/Table.tsx
import { FC, ThHTMLAttributes, TdHTMLAttributes, HTMLAttributes } from 'react';
import classNames from 'classnames';

// Table Header Cell
interface ThProps extends ThHTMLAttributes<HTMLTableHeaderCellElement> {
  align?: 'left' | 'center' | 'right';
}

export const Th: FC<ThProps> = ({ 
  children, 
  className, 
  align = 'left',
  ...props 
}) => (
  <th
    className={classNames(
      'px-6 py-3 bg-gray-50 text-sm font-medium text-gray-500 border-b border-gray-200',
      {
        'text-left': align === 'left',
        'text-center': align === 'center',
        'text-right': align === 'right',
      },
      className
    )}
    {...props}
  >
    {children}
  </th>
);

// Table Cell
interface TdProps extends TdHTMLAttributes<HTMLTableDataCellElement> {
  align?: 'left' | 'center' | 'right';
}

export const Td: FC<TdProps> = ({ 
  children, 
  className, 
  align = 'left',
  ...props 
}) => (
  <td
    className={classNames(
      'px-6 py-4 text-sm text-gray-900 whitespace-nowrap',
      {
        'text-left': align === 'left',
        'text-center': align === 'center',
        'text-right': align === 'right',
      },
      className
    )}
    {...props}
  >
    {children}
  </td>
);

// Table Row
interface TrProps extends HTMLAttributes<HTMLTableRowElement> {
  isHeader?: boolean;
}

export const Tr: FC<TrProps> = ({ 
  children, 
  className, 
  isHeader,
  ...props 
}) => (
  <tr
    className={classNames(
      'hover:bg-gray-50 transition-colors duration-200',
      {
        'bg-white': !isHeader,
      },
      className
    )}
    {...props}
  >
    {children}
  </tr>
);

// Table Header
export const Thead: FC<HTMLAttributes<HTMLTableSectionElement>> = ({ 
  children, 
  className,
  ...props 
}) => (
  <thead className={classNames('bg-gray-50', className)} {...props}>
    {children}
  </thead>
);

// Table Body
export const Tbody: FC<HTMLAttributes<HTMLTableSectionElement>> = ({ 
  children, 
  className,
  ...props 
}) => (
  <tbody className={classNames('divide-y divide-gray-200', className)} {...props}>
    {children}
  </tbody>
);

// Main Table Component
interface TableProps extends HTMLAttributes<HTMLTableElement> {
  striped?: boolean;
}

export const Table: FC<TableProps> = ({ 
  children, 
  className,
  striped,
  ...props 
}) => (
  <div className="w-full overflow-x-auto">
    <table 
      className={classNames(
        'min-w-full divide-y divide-gray-200',
        {
          'stripe-rows': striped,
        },
        className
      )}
      {...props}
    >
      {children}
    </table>
  </div>
);

// Export all components
export const TableComponents = {
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
};