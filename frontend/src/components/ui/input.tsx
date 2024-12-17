import { FC, InputHTMLAttributes } from "react";
import classNames from "classnames";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  error?: string;
  label?: string;
}

export const Input: FC<InputProps> = ({
  className,
  error,
  label,
  required,
  ...props
}) => {
  return (
    <div className="space-y-1">
      {label && (
        <label className="block text-sm font-medium text-gray-700">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <input
        className={classNames(
          "w-full px-4 py-2 border rounded-lg transition-colors duration-200",
          "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
          {
            "border-gray-300 hover:border-gray-400": !error,
            "border-red-500 hover:border-red-600": error,
          },
          className
        )}
        {...props}
      />
      {error && <p className="text-sm text-red-600">{error}</p>}
    </div>
  );
};
