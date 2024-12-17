// src/components/ui/Card.tsx
import { FC, HTMLAttributes } from 'react';
import classNames from 'classnames';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'outline';
}

export const Card: FC<CardProps> = ({
  children,
  variant = 'default',
  className,
  ...props
}) => {
  return (
    <div
      className={classNames(
        'rounded-lg p-6',
        {
          'bg-white shadow-lg': variant === 'default',
          'border border-gray-200': variant === 'outline',
        },
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};