'use client';

import React, { useState, useEffect } from 'react';
import {
  Activity,
  Search,
  RefreshCw,
  Calendar,
  User,
  CheckCircle,
  XCircle,
  Filter,
  Clock,
  Globe,
  Monitor,
  AlertCircle,
} from 'lucide-react';

interface ActivityLog {
  _id: string;
  user_id: string;
  email: string;
  action: string;
  ip_address: string;
  user_agent: string;
  timestamp: string;
  success: boolean;
  failure_reason?: string;
  metadata: Record<string, any>;
}

interface ActivityResponse {
  logs: ActivityLog[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export default function ActivityLogPage() {
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [limit] = useState(20);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [filterAction, setFilterAction] = useState<string>('');
  const [filterSuccess, setFilterSuccess] = useState<string>('');

  useEffect(() => {
    fetchLogs();
  }, [page, filterAction, filterSuccess]);

  const fetchLogs = async () => {
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

      if (filterAction) params.append('action', filterAction);
      if (filterSuccess) params.append('success', filterSuccess);
      if (searchQuery) params.append('search', searchQuery);

      const response = await fetch(`http://localhost:8000/admin/activity?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error('Access denied. Admin privileges required.');
        }
        throw new Error('Failed to fetch activity logs');
      }

      const data: ActivityResponse = await response.json();
      setLogs(data.logs);
      setTotal(data.total);
      setPages(data.pages);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchLogs();
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getActionBadgeColor = (action: string) => {
    const colors: Record<string, string> = {
      login: 'bg-green-100 text-green-800',
      logout: 'bg-gray-100 text-gray-800',
      register: 'bg-blue-100 text-blue-800',
      'password_reset': 'bg-yellow-100 text-yellow-800',
      'user_created': 'bg-purple-100 text-purple-800',
      'user_updated': 'bg-indigo-100 text-indigo-800',
      'user_deleted': 'bg-red-100 text-red-800',
      'permission_denied': 'bg-orange-100 text-orange-800',
    };
    return colors[action] || 'bg-gray-100 text-gray-800';
  };

  const getActionIcon = (action: string) => {
    switch (action) {
      case 'login':
      case 'register':
        return <User className="w-4 h-4" />;
      case 'logout':
        return <User className="w-4 h-4" />;
      case 'user_created':
      case 'user_updated':
      case 'user_deleted':
        return <User className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  // Access denied view
  if (error === 'Access denied. Admin privileges required.') {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <AlertCircle className="w-16 h-16 text-red-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
            <p className="text-gray-600 mb-6">
              You do not have permission to view activity logs. Admin or Owner role required.
            </p>
            <a
              href="/admin"
              className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Return to Dashboard
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Activity Logs</h1>
              <p className="mt-2 text-gray-600">
                Monitor system activity and user actions
              </p>
            </div>
            <button
              onClick={fetchLogs}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <form onSubmit={handleSearch} className="md:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search by email or IP address..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </form>

            {/* Action Filter */}
            <select
              value={filterAction}
              onChange={(e) => {
                setFilterAction(e.target.value);
                setPage(1);
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Actions</option>
              <option value="login">Login</option>
              <option value="logout">Logout</option>
              <option value="register">Register</option>
              <option value="password_reset">Password Reset</option>
              <option value="user_created">User Created</option>
              <option value="user_updated">User Updated</option>
              <option value="user_deleted">User Deleted</option>
            </select>

            {/* Success Filter */}
            <select
              value={filterSuccess}
              onChange={(e) => {
                setFilterSuccess(e.target.value);
                setPage(1);
              }}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Status</option>
              <option value="true">Successful</option>
              <option value="false">Failed</option>
            </select>
          </div>

          {/* Results count */}
          {!loading && (
            <div className="mt-4 text-sm text-gray-600">
              Showing {logs.length} of {total} activity logs
            </div>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading activity logs...</p>
          </div>
        )}

        {/* Error State */}
        {error && error !== 'Access denied. Admin privileges required.' && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center gap-3 text-red-600">
              <AlertCircle className="w-6 h-6" />
              <p className="font-medium">{error}</p>
            </div>
          </div>
        )}

        {/* Activity Logs */}
        {!loading && !error && (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            {logs.length === 0 ? (
              <div className="p-12 text-center">
                <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 font-medium">No activity logs found</p>
                <p className="text-sm text-gray-500 mt-2">
                  Try adjusting your filters or search query
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Timestamp
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        User
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Action
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        IP Address
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Details
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {logs.map((log, index) => (
                      <tr key={log._id || index} className="hover:bg-gray-50">
                        {/* Timestamp */}
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center gap-2 text-sm text-gray-900">
                            <Clock className="w-4 h-4 text-gray-400" />
                            {formatTimestamp(log.timestamp)}
                          </div>
                        </td>

                        {/* User */}
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center gap-2">
                            <User className="w-4 h-4 text-gray-400" />
                            <div className="text-sm text-gray-900">{log.email}</div>
                          </div>
                        </td>

                        {/* Action */}
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${getActionBadgeColor(log.action)}`}>
                            {getActionIcon(log.action)}
                            {log.action.replace('_', ' ').toUpperCase()}
                          </span>
                        </td>

                        {/* Status */}
                        <td className="px-6 py-4 whitespace-nowrap">
                          {log.success ? (
                            <div className="flex items-center gap-2 text-green-600">
                              <CheckCircle className="w-5 h-5" />
                              <span className="text-sm font-medium">Success</span>
                            </div>
                          ) : (
                            <div className="flex items-center gap-2 text-red-600">
                              <XCircle className="w-5 h-5" />
                              <span className="text-sm font-medium">Failed</span>
                            </div>
                          )}
                        </td>

                        {/* IP Address */}
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center gap-2 text-sm text-gray-600">
                            <Globe className="w-4 h-4 text-gray-400" />
                            {log.ip_address}
                          </div>
                        </td>

                        {/* Details */}
                        <td className="px-6 py-4">
                          <div className="text-sm text-gray-600">
                            {log.failure_reason && (
                              <div className="text-red-600 font-medium mb-1">
                                {log.failure_reason}
                              </div>
                            )}
                            {log.user_agent && (
                              <div className="flex items-center gap-2 text-xs text-gray-500">
                                <Monitor className="w-3 h-3" />
                                {log.user_agent.substring(0, 50)}
                                {log.user_agent.length > 50 && '...'}
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

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
    </div>
  );
}
