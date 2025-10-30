'use client';

import { useState, useEffect, useRef } from 'react';
import { TrendingUp, DollarSign, FileText, Users, Activity, Wifi, WifiOff, Bell } from 'lucide-react';

interface DashboardMetrics {
  today_revenue: number;
  today_transactions: number;
  pending_invoices: number;
  total_customers: number;
}

interface Alert {
  type: string;
  message: string;
  severity: 'info' | 'warning' | 'error' | 'success';
  timestamp: string;
}

interface Transaction {
  id: string;
  amount: number;
  type: string;
  timestamp: string;
}

export default function RealtimeDashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    today_revenue: 0,
    today_transactions: 0,
    pending_invoices: 0,
    total_customers: 0,
  });
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [connected, setConnected] = useState(false);
  const [connectionCount, setConnectionCount] = useState(0);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  const clientId = useRef(`client-${Math.random().toString(36).substr(2, 9)}`);

  useEffect(() => {
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket(`ws://localhost:8000/automation/ws/${clientId.current}`);
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          handleWebSocketMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setConnected(false);
        
        // Attempt to reconnect after 5 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Attempting to reconnect...');
          connectWebSocket();
        }, 5000);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Error connecting WebSocket:', error);
      setConnected(false);
    }
  };

  const handleWebSocketMessage = (message: any) => {
    setLastUpdate(new Date());

    switch (message.type) {
      case 'connected':
        console.log('Connected to real-time dashboard');
        break;

      case 'dashboard_update':
        if (message.data && message.data.metrics) {
          setMetrics(message.data.metrics);
        }
        break;

      case 'metric_update':
        if (message.data) {
          setMetrics(prev => ({
            ...prev,
            [message.data.metric]: message.data.value,
          }));
        }
        break;

      case 'alert':
        if (message.data) {
          const newAlert: Alert = {
            type: message.data.type || 'info',
            message: message.data.message || 'New alert',
            severity: message.data.severity || 'info',
            timestamp: message.timestamp || new Date().toISOString(),
          };
          setAlerts(prev => [newAlert, ...prev].slice(0, 10)); // Keep last 10 alerts
        }
        break;

      case 'new_transaction':
        if (message.data) {
          const newTransaction: Transaction = {
            id: message.data.id || Math.random().toString(),
            amount: message.data.amount || 0,
            type: message.data.type || 'unknown',
            timestamp: message.timestamp || new Date().toISOString(),
          };
          setTransactions(prev => [newTransaction, ...prev].slice(0, 20)); // Keep last 20
        }
        break;

      case 'report_complete':
        const reportAlert: Alert = {
          type: 'report',
          message: `Report "${message.data?.report_type}" is ready`,
          severity: 'success',
          timestamp: message.timestamp || new Date().toISOString(),
        };
        setAlerts(prev => [reportAlert, ...prev].slice(0, 10));
        break;

      case 'heartbeat':
        // Keep connection alive
        break;

      default:
        console.log('Unknown message type:', message.type);
    }
  };

  const fetchConnectionStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/automation/realtime/stats');
      const data = await response.json();
      setConnectionCount(data.total_connections || 0);
    } catch (error) {
      console.error('Error fetching connection stats:', error);
    }
  };

  useEffect(() => {
    fetchConnectionStats();
    const interval = setInterval(fetchConnectionStats, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const getSeverityColor = (severity: string) => {
    const colors = {
      info: 'bg-blue-100 text-blue-800 border-blue-200',
      warning: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      error: 'bg-red-100 text-red-800 border-red-200',
      success: 'bg-green-100 text-green-800 border-green-200',
    };
    return colors[severity as keyof typeof colors] || colors.info;
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES',
    }).format(amount);
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header with Connection Status */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Real-time Dashboard</h1>
            <p className="text-gray-600 mt-2">Live metrics and updates via WebSocket</p>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Connection Status */}
            <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
              connected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {connected ? <Wifi size={20} /> : <WifiOff size={20} />}
              <span className="font-medium">{connected ? 'Connected' : 'Disconnected'}</span>
            </div>

            {/* Active Connections */}
            <div className="bg-white px-4 py-2 rounded-lg shadow flex items-center gap-2">
              <Activity size={20} className="text-blue-600" />
              <span className="text-gray-900 font-medium">{connectionCount} active</span>
            </div>
          </div>
        </div>

        {/* Last Update */}
        {lastUpdate && (
          <div className="mb-6 text-sm text-gray-600">
            Last update: {lastUpdate.toLocaleTimeString()}
          </div>
        )}

        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Today's Revenue */}
          <div className="bg-white p-6 rounded-lg shadow-lg border-l-4 border-green-500">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-gray-600 text-sm font-medium">Today's Revenue</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {formatCurrency(metrics.today_revenue)}
                </p>
                <div className="flex items-center gap-1 mt-2">
                  <TrendingUp size={16} className="text-green-600" />
                  <span className="text-sm text-green-600 font-medium">Live</span>
                </div>
              </div>
              <div className="bg-green-100 p-3 rounded-lg">
                <DollarSign className="text-green-600" size={24} />
              </div>
            </div>
          </div>

          {/* Today's Transactions */}
          <div className="bg-white p-6 rounded-lg shadow-lg border-l-4 border-blue-500">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-gray-600 text-sm font-medium">Today's Transactions</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {metrics.today_transactions}
                </p>
                <div className="flex items-center gap-1 mt-2">
                  <Activity size={16} className="text-blue-600" />
                  <span className="text-sm text-blue-600 font-medium">Live</span>
                </div>
              </div>
              <div className="bg-blue-100 p-3 rounded-lg">
                <TrendingUp className="text-blue-600" size={24} />
              </div>
            </div>
          </div>

          {/* Pending Invoices */}
          <div className="bg-white p-6 rounded-lg shadow-lg border-l-4 border-yellow-500">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-gray-600 text-sm font-medium">Pending Invoices</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {metrics.pending_invoices}
                </p>
                <div className="flex items-center gap-1 mt-2">
                  <Activity size={16} className="text-yellow-600" />
                  <span className="text-sm text-yellow-600 font-medium">Live</span>
                </div>
              </div>
              <div className="bg-yellow-100 p-3 rounded-lg">
                <FileText className="text-yellow-600" size={24} />
              </div>
            </div>
          </div>

          {/* Total Customers */}
          <div className="bg-white p-6 rounded-lg shadow-lg border-l-4 border-purple-500">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-gray-600 text-sm font-medium">Total Customers</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {metrics.total_customers}
                </p>
                <div className="flex items-center gap-1 mt-2">
                  <Activity size={16} className="text-purple-600" />
                  <span className="text-sm text-purple-600 font-medium">Live</span>
                </div>
              </div>
              <div className="bg-purple-100 p-3 rounded-lg">
                <Users className="text-purple-600" size={24} />
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Alerts Feed */}
          <div className="bg-white rounded-lg shadow-lg">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center gap-2">
                <Bell className="text-blue-600" size={24} />
                <h2 className="text-xl font-semibold text-gray-900">Live Alerts</h2>
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm font-medium ml-auto">
                  {alerts.length}
                </span>
              </div>
            </div>
            <div className="p-6 max-h-96 overflow-y-auto">
              {alerts.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Bell className="mx-auto mb-2 text-gray-400" size={40} />
                  <p>No alerts yet</p>
                  <p className="text-sm">Alerts will appear here in real-time</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {alerts.map((alert, index) => (
                    <div
                      key={index}
                      className={`p-4 rounded-lg border ${getSeverityColor(alert.severity)}`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <p className="font-medium">{alert.message}</p>
                          <p className="text-sm opacity-75 mt-1">
                            {formatTime(alert.timestamp)}
                          </p>
                        </div>
                        <span className="text-xs px-2 py-1 rounded bg-white bg-opacity-50">
                          {alert.type}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Recent Transactions */}
          <div className="bg-white rounded-lg shadow-lg">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center gap-2">
                <TrendingUp className="text-green-600" size={24} />
                <h2 className="text-xl font-semibold text-gray-900">Recent Transactions</h2>
                <span className="bg-green-100 text-green-800 px-2 py-1 rounded-full text-sm font-medium ml-auto">
                  {transactions.length}
                </span>
              </div>
            </div>
            <div className="p-6 max-h-96 overflow-y-auto">
              {transactions.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <TrendingUp className="mx-auto mb-2 text-gray-400" size={40} />
                  <p>No transactions yet</p>
                  <p className="text-sm">New transactions will appear here in real-time</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {transactions.map((transaction) => (
                    <div
                      key={transaction.id}
                      className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="font-medium text-gray-900">
                            {transaction.type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                          </p>
                          <p className="text-sm text-gray-600">
                            {formatTime(transaction.timestamp)}
                          </p>
                        </div>
                        <p className="text-lg font-bold text-green-600">
                          {formatCurrency(transaction.amount)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Info Box */}
        <div className="mt-8 bg-blue-50 border-l-4 border-blue-500 p-6 rounded">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">🚀 Real-time Updates</h3>
          <p className="text-blue-800">
            This dashboard uses WebSocket technology to provide live updates without page refreshes.
            Metrics, alerts, and transactions are pushed to your browser automatically as they occur.
            The connection status indicator shows whether you're receiving live updates.
          </p>
        </div>
      </div>
    </div>
  );
}
