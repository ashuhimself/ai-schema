import React, { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Database, Clock, Activity, Users, AlertCircle, CheckCircle } from 'lucide-react';
import { apiClient } from '../services/api';
import { cn } from '../utils/cn';

interface HealthStatus {
  status: string;
  timestamp: string;
  database_connection: boolean;
  vector_store_connection: boolean;
  ai_service: boolean;
}

const Dashboard: React.FC = () => {
  const [recentQueries, setRecentQueries] = useState<any[]>([]);

  // Health check query
  const { data: healthStatus, isLoading: healthLoading } = useQuery<HealthStatus>({
    queryKey: ['health'],
    queryFn: () => apiClient.healthCheck(),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Query history
  const { data: queryHistory } = useQuery({
    queryKey: ['query-history'],
    queryFn: () => apiClient.getQueryHistory(10, 0),
  });

  // Schema info
  const { data: schemaData } = useQuery({
    queryKey: ['schema'],
    queryFn: () => apiClient.getSchema(),
  });

  useEffect(() => {
    if (queryHistory) {
      setRecentQueries(queryHistory);
    }
  }, [queryHistory]);

  // Mock data for charts - replace with real data from your API
  const queryTypeData = [
    { name: 'Natural Language', value: 65, color: '#8884d8' },
    { name: 'SQL', value: 35, color: '#82ca9d' },
  ];

  const dailyQueryData = [
    { date: 'Mon', queries: 45 },
    { date: 'Tue', queries: 52 },
    { date: 'Wed', queries: 38 },
    { date: 'Thu', queries: 61 },
    { date: 'Fri', queries: 58 },
    { date: 'Sat', queries: 29 },
    { date: 'Sun', queries: 31 },
  ];

  const getStatusColor = (status: boolean) => {
    return status ? 'text-green-600' : 'text-red-600';
  };

  const getStatusIcon = (status: boolean) => {
    return status ? (
      <CheckCircle className="h-4 w-4 text-green-600" />
    ) : (
      <AlertCircle className="h-4 w-4 text-red-600" />
    );
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
        <p className="text-muted-foreground">
          Overview of your data warehouse activity and system health
        </p>
      </div>

      {/* System Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Database</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              {healthLoading ? (
                <div className="animate-pulse bg-muted h-4 w-16 rounded" />
              ) : (
                <>
                  {getStatusIcon(healthStatus?.database_connection ?? false)}
                  <span className={cn(
                    "text-sm font-medium",
                    getStatusColor(healthStatus?.database_connection ?? false)
                  )}>
                    {healthStatus?.database_connection ? 'Connected' : 'Disconnected'}
                  </span>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Vector Store</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              {healthLoading ? (
                <div className="animate-pulse bg-muted h-4 w-16 rounded" />
              ) : (
                <>
                  {getStatusIcon(healthStatus?.vector_store_connection ?? false)}
                  <span className={cn(
                    "text-sm font-medium",
                    getStatusColor(healthStatus?.vector_store_connection ?? false)
                  )}>
                    {healthStatus?.vector_store_connection ? 'Connected' : 'Disconnected'}
                  </span>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">AI Service</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              {healthLoading ? (
                <div className="animate-pulse bg-muted h-4 w-16 rounded" />
              ) : (
                <>
                  {getStatusIcon(healthStatus?.ai_service ?? false)}
                  <span className={cn(
                    "text-sm font-medium",
                    getStatusColor(healthStatus?.ai_service ?? false)
                  )}>
                    {healthStatus?.ai_service ? 'Available' : 'Unavailable'}
                  </span>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tables</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {schemaData?.schema ? Object.keys(schemaData.schema).length : '—'}
            </div>
            <p className="text-xs text-muted-foreground">
              Available in schema
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Query Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Daily Query Activity</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={dailyQueryData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="queries" fill="#8884d8" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Query Type Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Query Types</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={queryTypeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {queryTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recent Queries */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Recent Queries
            <Button variant="outline" size="sm">
              View All
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {recentQueries.length > 0 ? (
            <div className="space-y-4">
              {recentQueries.slice(0, 5).map((query, index) => (
                <div
                  key={query.id || index}
                  className="flex items-start justify-between p-3 bg-muted rounded-lg"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">
                      {query.query_text}
                    </p>
                    <div className="flex items-center space-x-4 mt-1">
                      <span className="text-xs text-muted-foreground">
                        {query.query_type === 'natural' ? 'Natural Language' : 'SQL'}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {query.execution_time_ms}ms
                      </span>
                      {query.row_count && (
                        <span className="text-xs text-muted-foreground">
                          {query.row_count} rows
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 ml-4">
                    {query.success ? (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    ) : (
                      <AlertCircle className="h-4 w-4 text-red-600" />
                    )}
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span className="text-xs text-muted-foreground">
                      {new Date(query.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Database className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No recent queries found</p>
              <p className="text-sm">Start by asking questions in the Chat or running SQL queries</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Button variant="outline" className="h-16 flex flex-col space-y-2">
              <Database className="h-5 w-5" />
              <span className="text-sm">Explore Schema</span>
            </Button>
            <Button variant="outline" className="h-16 flex flex-col space-y-2">
              <Users className="h-5 w-5" />
              <span className="text-sm">Start Chat</span>
            </Button>
            <Button variant="outline" className="h-16 flex flex-col space-y-2">
              <Activity className="h-5 w-5" />
              <span className="text-sm">SQL Editor</span>
            </Button>
            <Button variant="outline" className="h-16 flex flex-col space-y-2">
              <Clock className="h-5 w-5" />
              <span className="text-sm">Query History</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;