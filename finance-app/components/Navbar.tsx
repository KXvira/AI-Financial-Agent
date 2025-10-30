// components/Navbar.tsx

"use client";

import { useState } from 'react';
import Link from "next/link";
import { useAuth } from '../contexts/AuthContext';

export default function Navbar() {
  const { user, logout, loading } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <header className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="font-bold text-xl text-blue-600 hover:text-blue-700">
              Fin Guard
            </Link>
          </div>

          {/* Navigation Links - Only show if authenticated */}
          {user && (
            <nav className="hidden md:flex space-x-8">
              <Link 
                href="/" 
                className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium transition-colors"
              >
                Dashboard
              </Link>
              <Link 
                href="/invoices" 
                className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium transition-colors"
              >
                Invoices
              </Link>
              <Link 
                href="/payments" 
                className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium transition-colors"
              >
                Payments
              </Link>
              <Link 
                href="/customers" 
                className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium transition-colors"
              >
                Customers
              </Link>
              <Link 
                href="/receipts" 
                className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium transition-colors"
              >
                Receipts
              </Link>
              <Link 
                href="/reports"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium transition-colors"
              >
                Reports
              </Link>
              <Link 
                href="/ai-insights"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                AI Insights
              </Link>
              <Link 
                href="/expenses"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                Expenses
              </Link>
            </nav>
          )}

          {/* User Menu or Login */}
          <div className="flex items-center space-x-4">
            {loading ? (
              <div className="animate-pulse h-8 w-8 bg-gray-200 rounded-full"></div>
            ) : user ? (
              <div className="relative">
                {/* User Avatar */}
                <button
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center space-x-3 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-md p-2"
                >
                  <div className="h-8 w-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-sm font-semibold text-blue-600">
                      {user.full_name.split(' ').map(n => n[0]).join('').toUpperCase()}
                    </span>
                  </div>
                  <div className="hidden md:block text-left">
                    <div className="text-sm font-medium text-gray-900">{user.full_name}</div>
                    <div className="text-xs text-gray-500 capitalize">{user.role}</div>
                  </div>
                  <svg className="h-4 w-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>

                {/* Dropdown Menu */}
                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-50">
                    <div className="py-1">
                      <div className="px-4 py-2 text-xs text-gray-500 border-b">
                        Signed in as<br />
                        <span className="font-medium text-gray-900">{user.email}</span>
                      </div>
                      
                      <Link
                        href="/auth/profile"
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        onClick={() => setShowUserMenu(false)}
                      >
                        Profile Settings
                      </Link>
                      
                      {(user.role === 'owner' || user.role === 'admin') && (
                        <Link
                          href="/admin"
                          className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                          onClick={() => setShowUserMenu(false)}
                        >
                          Admin Panel
                        </Link>
                      )}
                      
                      <div className="border-t border-gray-100">
                        <button
                          onClick={handleLogout}
                          className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                        >
                          Sign Out
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <Link
                  href="/auth/login"
                  className="text-gray-600 hover:text-gray-900 text-sm font-medium hover:underline transition-all"
                >
                  Sign In
                </Link>
                <Link
                  href="/auth/register"
                  className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700 hover:shadow-md transition-all transform hover:scale-105 active:scale-95"
                >
                  Get Started
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Navigation Menu */}
      {user && (
        <div className="md:hidden border-t bg-gray-50">
          <nav className="px-4 py-2 space-y-1">
            <Link href="/" className="block px-3 py-2 text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md">
              Dashboard
            </Link>
            <Link href="/invoices" className="block px-3 py-2 text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md">
              Invoices
            </Link>
            <Link href="/payments" className="block px-3 py-2 text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md">
              Payments
            </Link>
            <Link href="/customers" className="block px-3 py-2 text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md">
              Customers
            </Link>
            <Link href="/ai-insights" className="block px-3 py-2 text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md">
              AI Insights
            </Link>
          </nav>
        </div>
      )}
    </header>
  );
}
  