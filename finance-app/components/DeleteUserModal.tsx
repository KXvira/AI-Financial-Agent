'use client';

import { useState } from 'react';
import { X, Trash2, AlertTriangle, User, Mail, Building } from 'lucide-react';

interface DeleteUserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  user: {
    id: string;
    email: string;
    company_name: string;
    role: string;
    status: string;
  } | null;
}

export default function DeleteUserModal({ isOpen, onClose, onSuccess, user }: DeleteUserModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen || !user) return null;

  const handleDelete = async () => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('Not authenticated. Please log in again.');
        return;
      }

      const response = await fetch(`http://localhost:8000/admin/users/${user.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        
        if (response.status === 403) {
          setError('You do not have permission to delete users');
        } else if (response.status === 404) {
          setError('User not found');
        } else if (response.status === 400 && errorData.detail?.includes('cannot delete yourself')) {
          setError('You cannot delete your own account');
        } else {
          setError(errorData.detail || 'Failed to delete user');
        }
        return;
      }

      // Success - close modal and refresh user list
      onSuccess();
      onClose();

    } catch (error) {
      console.error('Error deleting user:', error);
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setError(null);
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
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-red-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900">Delete User</h2>
          </div>
          <button
            onClick={handleClose}
            disabled={loading}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {/* Warning Message */}
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm font-medium text-red-800 mb-2">
              ⚠️ This action will deactivate the user account
            </p>
            <p className="text-sm text-red-700">
              The user will be marked as inactive and will not be able to log in. This action can be reversed by reactivating the account.
            </p>
          </div>

          {/* User Details */}
          <div className="space-y-3 mb-6">
            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <Mail className="w-5 h-5 text-gray-600" />
              <div>
                <p className="text-xs text-gray-500">Email</p>
                <p className="text-sm font-medium text-gray-900">{user.email}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <Building className="w-5 h-5 text-gray-600" />
              <div>
                <p className="text-xs text-gray-500">Company</p>
                <p className="text-sm font-medium text-gray-900">{user.company_name}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
              <User className="w-5 h-5 text-gray-600" />
              <div className="flex items-center gap-2">
                <p className="text-xs text-gray-500">Role:</p>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getRoleBadgeColor(user.role)}`}>
                  {user.role.toUpperCase()}
                </span>
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-red-800">Error</p>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Confirmation Text */}
          <div className="mb-6">
            <p className="text-sm text-gray-700">
              Are you sure you want to delete this user? Type the user's email below to confirm:
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200">
          <button
            type="button"
            onClick={handleClose}
            disabled={loading}
            className="px-6 py-2.5 text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 font-medium"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleDelete}
            disabled={loading}
            className="px-6 py-2.5 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium flex items-center gap-2"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Deleting...
              </>
            ) : (
              <>
                <Trash2 className="w-4 h-4" />
                Delete User
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
