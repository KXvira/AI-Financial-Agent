'use client';

import { useState, useEffect } from 'react';
import { X, User, Phone, Building, Shield, AlertCircle, CheckCircle } from 'lucide-react';

interface EditUserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  user: {
    id: string;
    email: string;
    company_name: string;
    phone_number: string;
    role: string;
    status: string;
  } | null;
}

interface FormData {
  company_name: string;
  phone_number: string;
  role: string;
  status: string;
}

interface FormErrors {
  company_name?: string;
  phone_number?: string;
  role?: string;
  status?: string;
  general?: string;
}

export default function EditUserModal({ isOpen, onClose, onSuccess, user }: EditUserModalProps) {
  const [formData, setFormData] = useState<FormData>({
    company_name: '',
    phone_number: '',
    role: 'viewer',
    status: 'active'
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);

  // Update form when user prop changes
  useEffect(() => {
    if (user) {
      setFormData({
        company_name: user.company_name || '',
        phone_number: user.phone_number || '',
        role: user.role || 'viewer',
        status: user.status || 'active'
      });
    }
  }, [user]);

  if (!isOpen || !user) return null;

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

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

    // Status validation
    if (!formData.status) {
      newErrors.status = 'Status is required';
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

      const response = await fetch(`http://localhost:8000/admin/users/${user.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        
        if (response.status === 403) {
          setErrors({ general: 'You do not have permission to update users' });
        } else if (response.status === 404) {
          setErrors({ general: 'User not found' });
        } else {
          setErrors({ general: errorData.detail || 'Failed to update user' });
        }
        return;
      }

      // Success - close modal and refresh user list
      onSuccess();
      onClose();

    } catch (error) {
      console.error('Error updating user:', error);
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

  const getRoleBadgeColor = (role: string) => {
    const colors = {
      admin: 'bg-purple-100 text-purple-800',
      owner: 'bg-blue-100 text-blue-800',
      manager: 'bg-green-100 text-green-800',
      accountant: 'bg-yellow-100 text-yellow-800',
      viewer: 'bg-gray-100 text-gray-800'
    };
    return colors[role as keyof typeof colors] || 'bg-gray-100 text-gray-800';
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
              <h2 className="text-xl font-bold text-gray-900">Edit User</h2>
              <p className="text-sm text-gray-600">{user.email}</p>
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

        {/* Current Role Badge */}
        <div className="px-6 pt-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-600">Current Role:</span>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${getRoleBadgeColor(user.role)}`}>
              {user.role.toUpperCase()}
            </span>
          </div>
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
            {/* Email (Read-only) */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address (Cannot be changed)
              </label>
              <div className="w-full px-4 py-2.5 bg-gray-50 border border-gray-300 rounded-lg text-gray-600">
                {user.email}
              </div>
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

            {/* Status */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <CheckCircle className="w-4 h-4 inline mr-2" />
                Account Status *
              </label>
              <select
                value={formData.status}
                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                className={`w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.status ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={loading}
              >
                <option value="active">Active - Full access</option>
                <option value="inactive">Inactive - Cannot log in</option>
                <option value="suspended">Suspended - Temporarily blocked</option>
                <option value="pending">Pending - Awaiting verification</option>
              </select>
              {errors.status && (
                <p className="mt-1 text-sm text-red-600">{errors.status}</p>
              )}
            </div>
          </div>

          {/* Warning for status changes */}
          {formData.status !== user.status && (
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                ⚠️ Changing the account status will affect the user's ability to access the system.
              </p>
            </div>
          )}

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
                  Updating...
                </>
              ) : (
                <>
                  <CheckCircle className="w-4 h-4" />
                  Update User
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
