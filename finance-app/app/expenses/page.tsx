'use client';

import React from 'react';
import { useState } from 'react';
import ReceiptUploader from '@/components/ReceiptUploader';
import ExpenseDashboard from '@/components/ExpenseDashboard';
import { FileText, BarChart3 } from 'lucide-react';

type TabType = 'dashboard' | 'upload';

export default function ExpensesPage() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Expense Management
        </h1>
        <p className="text-gray-600">
          Upload receipts and track your business expenses with AI-powered OCR
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6">
        <button
          onClick={() => setActiveTab('dashboard')}
          className={`
            flex items-center space-x-2 px-4 py-2 rounded-md font-medium transition-colors
            ${activeTab === 'dashboard' 
              ? 'bg-blue-600 text-white' 
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }
          `}
        >
          <BarChart3 className="h-4 w-4" />
          <span>Dashboard</span>
        </button>
        
        <button
          onClick={() => setActiveTab('upload')}
          className={`
            flex items-center space-x-2 px-4 py-2 rounded-md font-medium transition-colors
            ${activeTab === 'upload' 
              ? 'bg-blue-600 text-white' 
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
            }
          `}
        >
          <FileText className="h-4 w-4" />
          <span>Upload Receipts</span>
        </button>
      </div>

      {/* Tab Content */}
      <div className="min-h-[600px]">
        {activeTab === 'dashboard' && (
          <ExpenseDashboard />
        )}
        
        {activeTab === 'upload' && (
          <ReceiptUploader 
            onUploadComplete={(receipt) => {
              console.log('Receipt uploaded:', receipt);
              // You can add notification here or refresh dashboard
            }}
          />
        )}
      </div>
    </div>
  );
}