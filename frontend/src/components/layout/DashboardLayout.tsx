// src/components/layout/DashboardLayout.tsx
import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  HomeIcon,
  CubeIcon,
  ShoppingCartIcon,
  ArrowRightOnRectangleIcon,
} from "@heroicons/react/24/outline";
import { authService } from "../../services/authService";

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: HomeIcon },
  { name: "Inventory", href: "/inventory", icon: CubeIcon },
  { name: "Transactions", href: "/transactions", icon: ShoppingCartIcon },
];

interface DashboardLayoutProps {
  children: React.ReactNode;
}

const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  const location = useLocation();
  const navigate = useNavigate();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const handleLogout = async () => {
    try {
      await authService.logout();
      navigate("/login");
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Sidebar */}
      <div
        className={`fixed top-0 left-0 h-full w-64 bg-white shadow-lg transition-transform ${
          isSidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-800">ERP System</h2>
        </div>
        <nav className="mt-6">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center px-6 py-3 text-gray-600 hover:bg-gray-50 ${
                  isActive
                    ? "bg-blue-50 text-blue-600 border-r-4 border-blue-600"
                    : ""
                }`}
              >
                <item.icon className="h-5 w-5 mr-3" />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Main Content */}
      <div
        className={`${
          isSidebarOpen ? "ml-64" : "ml-0"
        } min-h-screen transition-margin duration-300`}
      >
        {/* Top Bar */}
        <div className="bg-white shadow-sm">
          <div className="flex items-center justify-between px-6 py-4">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="text-gray-600 hover:text-gray-900"
            >
              <svg
                className="h-6 w-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>
            <button
              onClick={handleLogout}
              className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
            >
              <ArrowRightOnRectangleIcon className="h-5 w-5 mr-2" />
              Logout
            </button>
          </div>
        </div>

        {/* Page Content */}
        <div className="p-6">
          {children}  {/* This line was missing - it's crucial for rendering the dashboard content */}
        </div>
      </div>
    </div>
  );
};

export default DashboardLayout;