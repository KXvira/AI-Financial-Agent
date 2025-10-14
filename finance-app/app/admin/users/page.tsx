'use client';

import React, { useState, useEffect } from 'react';
import {
  Users,
  Search,
  Plus,
  Edit,
  Trash2,
  RefreshCw,
  Mail,
  Phone,
  Shield,
  CheckCircle,
  XCircle,
} from 'lucide-react';
import Navbar from '@/components/Navbar';
import CreateUserModal from '@/components/CreateUserModal';
import EditUserModal from '@/components/EditUserModal';
import DeleteUserModal from '@/components/DeleteUserModal';

interface User {
  _id: string;
  email: string;
  company_name: string;
  phone_number: string;
  role: string;
  status: string;
  is_active: boolean;
  email_verified: boolean;
  phone_verified: boolean;
  created_at: string;
  updated_at: string;
  last_login?: string;
  failed_login_attempts: number;
}

interface UsersResponse {
  users: User[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export default function UserManagementPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [limit] = useState(10);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterRole, setFilterRole] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('');
  
  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchUsers();
  }, [page, filterRole, filterStatus]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('token');
      if (!token) {
        setError('Not authenticated');
        return;
      }

      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
      });

      if (filterRole) params.append('role', filterRole);
      if (filterStatus) params.append('status', filterStatus);
      if (searchQuery) params.append('search', searchQuery);

      const response = await fetch(`http://localhost:8000/admin/users?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error('Access denied. Admin privileges required.');
        }
        throw new Error('Failed to fetch users');
      }

      const data: UsersResponse = await response.json();
      setUsers(data.users);
      setTotal(data.total);
      setPages(data.pages);

    } catch (err) {
      console.error('Error fetching users:', err);
      setError(err instanceof Error ? err.message : 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    fetchUsers();
  };

  const roleColors: Record<string, string> = {
    admin: 'bg-purple-100 text-purple-800',
    owner: 'bg-blue-100 text-blue-800',
    manager: 'bg-green-100 text-green-800',
    accountant: 'bg-yellow-100 text-yellow-800',
    viewer: 'bg-gray-100 text-gray-800'
  };

  const statusColors: Record<string, string> = {
    active: 'bg-green-100 text-green-800',
    inactive: 'bg-gray-100 text-gray-800',
    suspended: 'bg-red-100 text-red-800',
    pending_verification: 'bg-yellow-100 text-yellow-800'
  };

  if (error && error.includes('Access denied')) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="flex items-center justify-center h-[calc(100vh-64px)]">
          <div className="text-center max-w-md">
            <Shield className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={() => window.location.href = '/admin'}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
              <p className="mt-2 text-gray-600">
                Manage system users and their permissions
              </p>
            </div>
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Plus className="w-5 h-5" />
              Add User
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6 border border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search Users
              </label>
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    placeholder="Search by email or company..."
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <button
                  onClick={handleSearch}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Search
                </button>
              </div>
            </div>

            {/* Role Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter by Role
              </label>
              <select
                value={filterRole}
                onChange={(e) => {
                  setFilterRole(e.target.value);
                  setPage(1);
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Roles</option>
                <option value="admin">Admin</option>
                <option value="owner">Owner</option>
                <option value="manager">Manager</option>
                <option value="accountant">Accountant</option>
                <option value="viewer">Viewer</option>
              </select>
            </div>

            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter by Status
              </label>
              <select
                value={filterStatus}
                onChange={(e) => {
                  setFilterStatus(e.target.value);
                  setPage(1);
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="suspended">Suspended</option>
                <option value="pending_verification">Pending</option>
              </select>
            </div>
          </div>

          {/* Results Count */}
          <div className="mt-4 flex items-center justify-between border-t border-gray-200 pt-4">
            <p className="text-sm text-gray-600">
              Showing <span className="font-medium">{users.length}</span> of{' '}
              <span className="font-medium">{total}</span> users
            </p>
            <button
              onClick={fetchUsers}
              className="flex items-center gap-2 px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh
            </button>
          </div>
        </div>

        {/* Users Table */}
        {loading ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center border border-gray-200">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading users...</p>
          </div>
        ) : users.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center border border-gray-200">
            <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No users found</h3>
            <p className="text-gray-600">
              {searchQuery || filterRole || filterStatus
                ? 'Try adjusting your filters'
                : 'Get started by creating your first user'}
            </p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Contact
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Role
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Verification
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user._id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {user.company_name}
                          </div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex flex-col gap-1">
                          <div className="flex items-center gap-2 text-sm text-gray-600">
                            <Mail className="w-4 h-4" />
                            <span>{user.email}</span>
                          </div>
                          <div className="flex items-center gap-2 text-sm text-gray-600">
                            <Phone className="w-4 h-4" />
                            <span>{user.phone_number}</span>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${roleColors[user.role] || 'bg-gray-100 text-gray-800'}`}>
                          {user.role.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[user.status] || 'bg-gray-100 text-gray-800'}`}>
                          {user.status.replace('_', ' ').toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex gap-2">
                          {user.email_verified ? (
                            <CheckCircle className="w-5 h-5 text-green-500" title="Email verified" />
                          ) : (
                            <XCircle className="w-5 h-5 text-gray-300" title="Email not verified" />
                          )}
                          {user.phone_verified ? (
                            <CheckCircle className="w-5 h-5 text-green-500" title="Phone verified" />
                          ) : (
                            <XCircle className="w-5 h-5 text-gray-300" title="Phone not verified" />
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => {
                              setSelectedUser({
                                id: user._id,
                                email: user.email,
                                company_name: user.company_name,
                                phone_number: user.phone_number,
                                role: user.role,
                                status: user.status
                              });
                              setShowEditModal(true);
                            }}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                            title="Edit user"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => {
                              setSelectedUser({
                                id: user._id,
                                email: user.email,
                                company_name: user.company_name,
                                phone_number: user.phone_number,
                                role: user.role,
                                status: user.status
                              });
                              setShowDeleteModal(true);
                            }}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                            title="Delete user"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {pages > 1 && (
              <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <button
                    onClick={() => setPage(Math.max(1, page - 1))}
                    disabled={page === 1}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-700">
                      Page <span className="font-medium">{page}</span> of{' '}
                      <span className="font-medium">{pages}</span>
                    </span>
                  </div>

                  <button
                    onClick={() => setPage(Math.min(pages, page + 1))}
                    disabled={page === pages}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Success Message Toast */}
      {successMessage && (
        <div className="fixed top-4 right-4 bg-green-50 border border-green-200 rounded-lg p-4 shadow-lg z-50 flex items-center gap-3">
          <CheckCircle className="w-5 h-5 text-green-600" />
          <p className="text-sm text-green-800">{successMessage}</p>
          <button
            onClick={() => setSuccessMessage(null)}
            className="ml-4 text-green-600 hover:text-green-800"
          >
            <XCircle className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Modals */}
      <CreateUserModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSuccess={() => {
          setSuccessMessage('User created successfully!');
          fetchUsers();
          setTimeout(() => setSuccessMessage(null), 5000);
        }}
      />

      <EditUserModal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false);
          setSelectedUser(null);
        }}
        onSuccess={() => {
          setSuccessMessage('User updated successfully!');
          fetchUsers();
          setTimeout(() => setSuccessMessage(null), 5000);
        }}
        user={selectedUser}
      />

      <DeleteUserModal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false);
          setSelectedUser(null);
        }}
        onSuccess={() => {
          setSuccessMessage('User deleted successfully!');
          fetchUsers();
          setTimeout(() => setSuccessMessage(null), 5000);
        }}
        user={selectedUser}
      />
    </div>
  );
}
