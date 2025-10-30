'use client';

import { useState } from 'react';
import { X, User, Mail, Phone, Building, Lock, Shield, AlertCircle } from 'lucide-react';

interface CreateUserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

interface FormData {
  email: string;
  password: string;
  confirm_password: string;
  company_name: string;
  phone_number: string;
  role: string;
}

interface FormErrors {
  email?: string;
  password?: string;
  confirm_password?: string;
  company_name?: string;
  phone_number?: string;
  role?: string;
  general?: string;
}

export default function CreateUserModal({ isOpen, onClose, onSuccess }: CreateUserModalProps) {
  const [formData, setFormData] = useState<FormData>({
    email: '',
    password: '',
    confirm_password: '',
    company_name: '',
    phone_number: '+254',
    role: 'viewer'
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    // Confirm password validation
    if (!formData.confirm_password) {
      newErrors.confirm_password = 'Please confirm password';
    } else if (formData.password !== formData.confirm_password) {
      newErrors.confirm_password = 'Passwords do not match';
    }

    // Company name validation
    if (!formData.company_name) {
      newErrors.company_name = 'Company name is required';
    } else if (formData.company_name.length < 2) {
      newErrors.company_name = 'Company name must be at least 2 characters';
    }

    // Phone number validation
    if (!formData.phone_number) {
      newErrors.phone_number = 'Phone number is required';
    } else if (!/^\+254[0-9]{9}$/.test(formData.phone_number)) {
      newErrors.phone_number = 'Phone must be in format +254XXXXXXXXX';
    }

    // Role validation
    if (!formData.role) {
      newErrors.role = 'Role is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setErrors({ general: 'Not authenticated. Please log in again.' });
        return;
      }

      const response = await fetch('http://localhost:8000/admin/users', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        
        // Handle specific error messages from backend
        if (response.status === 400) {
          if (errorData.detail?.includes('email already exists')) {
            setErrors({ email: 'A user with this email already exists' });
          } else {
            setErrors({ general: errorData.detail || 'Failed to create user' });
          }
        } else if (response.status === 403) {
          setErrors({ general: 'You do not have permission to create users' });
        } else {
          setErrors({ general: errorData.detail || 'Failed to create user' });
        }
        return;
      }

      // Success - close modal and refresh user list
      onSuccess();
      onClose();
      
      // Reset form
      setFormData({
        email: '',
        password: '',
        confirm_password: '',
        company_name: '',
        phone_number: '+254',
        role: 'viewer'
      });

    } catch (error) {
      console.error('Error creating user:', error);
      setErrors({ general: 'Network error. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setErrors({});
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <User className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Create New User</h2>
              <p className="text-sm text-gray-600">Add a new user to the system</p>
            </div>
          </div>
          <button
            onClick={handleClose}
            disabled={loading}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6">
          {/* General Error */}
          {errors.general && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-red-800">Error</p>
                <p className="text-sm text-red-700 mt-1">{errors.general}</p>
              </div>
            </div>
          )}

          <div className="space-y-5">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Mail className="w-4 h-4 inline mr-2" />
                Email Address *
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className={`w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.email ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="user@example.com"
                disabled={loading}
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email}</p>
              )}
            </div>

            {/* Company Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Building className="w-4 h-4 inline mr-2" />
                Company Name *
              </label>
              <input
                type="text"
                value={formData.company_name}
                onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                className={`w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.company_name ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Acme Corporation"
                disabled={loading}
              />
              {errors.company_name && (
                <p className="mt-1 text-sm text-red-600">{errors.company_name}</p>
              )}
            </div>

            {/* Phone Number */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Phone className="w-4 h-4 inline mr-2" />
                Phone Number *
              </label>
              <input
                type="tel"
                value={formData.phone_number}
                onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
                className={`w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.phone_number ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="+254712345678"
                disabled={loading}
              />
              {errors.phone_number && (
                <p className="mt-1 text-sm text-red-600">{errors.phone_number}</p>
              )}
              <p className="mt-1 text-xs text-gray-500">Format: +254XXXXXXXXX</p>
            </div>

            {/* Role */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Shield className="w-4 h-4 inline mr-2" />
                User Role *
              </label>
              <select
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                className={`w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.role ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={loading}
              >
                <option value="viewer">Viewer - Read-only access</option>
                <option value="accountant">Accountant - Financial records</option>
                <option value="manager">Manager - User & data management</option>
                <option value="owner">Owner - Full access</option>
                <option value="admin">Admin - System administrator</option>
              </select>
              {errors.role && (
                <p className="mt-1 text-sm text-red-600">{errors.role}</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Lock className="w-4 h-4 inline mr-2" />
                Password *
              </label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className={`w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.password ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Minimum 8 characters"
                disabled={loading}
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password}</p>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Lock className="w-4 h-4 inline mr-2" />
                Confirm Password *
              </label>
              <input
                type="password"
                value={formData.confirm_password}
                onChange={(e) => setFormData({ ...formData, confirm_password: e.target.value })}
                className={`w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.confirm_password ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Re-enter password"
                disabled={loading}
              />
              {errors.confirm_password && (
                <p className="mt-1 text-sm text-red-600">{errors.confirm_password}</p>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 mt-8 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={handleClose}
              disabled={loading}
              className="px-6 py-2.5 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Creating...
                </>
              ) : (
                <>
                  <User className="w-4 h-4" />
                  Create User
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
