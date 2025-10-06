'use client';

import React, { useState, useRef, useCallback } from 'react';
import { Upload, Camera, X, CheckCircle, AlertCircle, Clock } from 'lucide-react';

interface Receipt {
  id: string;
  filename: string;
  status: 'processing' | 'completed' | 'failed';
  uploadedAt: string;
  amount?: number;
  vendor?: string;
  category?: string;
}

interface ReceiptUploaderProps {
  onUploadComplete?: (receipt: Receipt) => void;
}

export default function ReceiptUploader({ onUploadComplete }: ReceiptUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadedReceipts, setUploadedReceipts] = useState<Receipt[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    handleFileUpload(files);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    handleFileUpload(files);
  };

  const handleFileUpload = async (files: File[]) => {
    if (files.length === 0) return;

    setIsUploading(true);

    for (const file of files) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        alert(`${file.name} is not an image file`);
        continue;
      }

      // Create receipt entry
      const receipt: Receipt = {
        id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
        filename: file.name,
        status: 'processing',
        uploadedAt: new Date().toISOString()
      };

      setUploadedReceipts(prev => [...prev, receipt]);

      try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/ocr/upload-receipt', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: formData
        });

        if (!response.ok) {
          throw new Error('Upload failed');
        }

        const result = await response.json();

        // Update receipt with OCR results
        const updatedReceipt: Receipt = {
          ...receipt,
          status: 'completed',
          amount: result.parsed_data?.total,
          vendor: result.parsed_data?.vendor,
          category: result.parsed_data?.category
        };

        setUploadedReceipts(prev => 
          prev.map(r => r.id === receipt.id ? updatedReceipt : r)
        );

        onUploadComplete?.(updatedReceipt);

      } catch (error) {
        console.error('Upload error:', error);
        
        // Mark as failed
        setUploadedReceipts(prev => 
          prev.map(r => r.id === receipt.id ? { ...r, status: 'failed' } : r)
        );
      }
    }

    setIsUploading(false);
  };

  const getStatusIcon = (status: Receipt['status']) => {
    switch (status) {
      case 'processing':
        return <Clock className="h-4 w-4 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
    }
  };

  const removeReceipt = (id: string) => {
    setUploadedReceipts(prev => prev.filter(r => r.id !== id));
  };

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div
        className={`
          border-2 border-dashed rounded-lg p-8 text-center transition-colors
          ${isDragging 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
          ${isUploading ? 'opacity-50 pointer-events-none' : ''}
        `}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="flex flex-col items-center space-y-4">
          <div className="flex space-x-4">
            <Camera className="h-8 w-8 text-gray-400" />
            <Upload className="h-8 w-8 text-gray-400" />
          </div>
          
          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Upload Receipt Images
            </h3>
            <p className="text-sm text-gray-500 mb-4">
              Drag and drop your receipt images here, or click to browse
            </p>
          </div>

          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {isUploading ? 'Uploading...' : 'Choose Files'}
          </button>
          
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
          />
          
          <p className="text-xs text-gray-400">
            Supported formats: JPG, PNG, GIF • Max 10MB per file
          </p>
        </div>
      </div>

      {/* Uploaded Receipts List */}
      {uploadedReceipts.length > 0 && (
        <div className="bg-white rounded-lg border">
          <div className="px-6 py-4 border-b">
            <h3 className="text-lg font-medium text-gray-900">
              Recent Uploads ({uploadedReceipts.length})
            </h3>
          </div>
          
          <div className="divide-y">
            {uploadedReceipts.map((receipt) => (
              <div key={receipt.id} className="px-6 py-4 flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  {getStatusIcon(receipt.status)}
                  
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {receipt.filename}
                    </p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span>
                        {new Date(receipt.uploadedAt).toLocaleString()}
                      </span>
                      {receipt.vendor && (
                        <span>• {receipt.vendor}</span>
                      )}
                      {receipt.amount && (
                        <span>• KES {receipt.amount.toFixed(2)}</span>
                      )}
                      {receipt.category && (
                        <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                          {receipt.category}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                
                <button
                  onClick={() => removeReceipt(receipt.id)}
                  className="text-gray-400 hover:text-red-500"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {uploadedReceipts.length === 0 && (
        <div className="text-center py-8">
          <p className="text-gray-500">No receipts uploaded yet</p>
        </div>
      )}
    </div>
  );
}