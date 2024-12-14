// src/components/ui/Button.tsx
import { FC, ButtonHTMLAttributes } from 'react';
import classNames from 'classnames';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline';
  isLoading?: boolean;
}

export const Button: FC<ButtonProps> = ({
  children,
  variant = 'primary',
  isLoading,
  className,
  disabled,
  ...props
}) => {
  return (
    <button
      disabled={disabled || isLoading}
      className={classNames(
        'inline-flex items-center justify-center px-4 py-2 rounded-lg font-medium transition-colors duration-200',
        {
          'bg-primary-600 text-white hover:bg-primary-700': variant === 'primary',
          'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300': variant === 'secondary',
          'text-primary-600 border-2 border-primary-600 hover:bg-primary-50': variant === 'outline',
          'opacity-50 cursor-not-allowed': disabled || isLoading,
        },
        className
      )}
      {...props}
    >
      {isLoading ? (
        <svg
          className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
          />
        </svg>
      ) : null}
      {children}
    </button>
  );
};