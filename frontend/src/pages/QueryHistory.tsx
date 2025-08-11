import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Clock, Search, Filter, Download, Play, AlertCircle, CheckCircle, Trash2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { apiClient } from '../services/api';
import { QueryHistoryItem } from '../types';
import { cn } from '../utils/cn';

const QueryHistory: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'success' | 'failed'>('all');
  const [selectedQueries, setSelectedQueries] = useState<Set<string>>(new Set());
  const [page, setPage] = useState(0);
  const pageSize = 20;

  // Fetch query history
  const { data: queryHistory = [], isLoading, refetch } = useQuery({
    queryKey: ['query-history', page, pageSize],
    queryFn: () => apiClient.getQueryHistory(pageSize, page * pageSize),
  });

  const filteredQueries = queryHistory.filter(query => {
    const matchesSearch = query.query_text.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (query.generated_sql && query.generated_sql.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesFilter = filterType === 'all' || 
                         (filterType === 'success' && query.success) ||
                         (filterType === 'failed' && !query.success);

    return matchesSearch && matchesFilter;
  });

  const handleSelectQuery = (queryId: string) => {
    const newSelection = new Set(selectedQueries);
    if (newSelection.has(queryId)) {
      newSelection.delete(queryId);
    } else {
      newSelection.add(queryId);
    }
    setSelectedQueries(newSelection);
  };

  const handleSelectAll = () => {
    if (selectedQueries.size === filteredQueries.length) {
      setSelectedQueries(new Set());
    } else {
      setSelectedQueries(new Set(filteredQueries.map(q => q.id)));
    }
  };

  const exportQueries = () => {
    const queriesToExport = filteredQueries.filter(q => selectedQueries.has(q.id));
    const exportData = queriesToExport.map(query => ({
      timestamp: query.timestamp,
      query_type: query.query_type,
      query_text: query.query_text,
      generated_sql: query.generated_sql,
      success: query.success,
      execution_time_ms: query.execution_time_ms,
      row_count: query.row_count,
      error_message: query.error_message
    }));
    
    apiClient.exportToJSON(exportData, `query_history_${new Date().toISOString().split('T')[0]}.json`);
  };

  const formatDuration = (ms?: number) => {
    if (!ms) return '—';
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  const formatRowCount = (count?: number) => {
    if (!count) return '—';
    return count.toLocaleString();
  };

  const getQueryTypeColor = (type: string) => {
    return type === 'natural' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800';
  };

  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-muted rounded w-1/4 mb-4"></div>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-20 bg-muted rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Query History</h1>
          <p className="text-muted-foreground">
            View and manage your previous queries and results
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {selectedQueries.size > 0 && (
            <>
              <Button variant="outline" onClick={exportQueries}>
                <Download className="h-4 w-4 mr-2" />
                Export ({selectedQueries.size})
              </Button>
              <Button variant="outline">
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </Button>
            </>
          )}
          <Button variant="outline" onClick={() => refetch()}>
            Refresh
          </Button>
        </div>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="py-4">
          <div className="flex items-center justify-between space-x-4">
            <div className="flex items-center space-x-4 flex-1">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search queries..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              
              <div className="flex items-center space-x-2">
                <Filter className="h-4 w-4 text-muted-foreground" />
                <Button
                  variant={filterType === 'all' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilterType('all')}
                >
                  All
                </Button>
                <Button
                  variant={filterType === 'success' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilterType('success')}
                >
                  Success
                </Button>
                <Button
                  variant={filterType === 'failed' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilterType('failed')}
                >
                  Failed
                </Button>
              </div>
            </div>

            <div className="flex items-center space-x-2 text-sm text-muted-foreground">
              <span>{filteredQueries.length} queries</span>
              {selectedQueries.size > 0 && (
                <span>• {selectedQueries.size} selected</span>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Query List */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle>Query History</CardTitle>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={selectedQueries.size === filteredQueries.length && filteredQueries.length > 0}
                onChange={handleSelectAll}
                className="rounded"
              />
              <span className="text-sm text-muted-foreground">Select All</span>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {filteredQueries.length > 0 ? (
            <div className="space-y-4">
              {filteredQueries.map((query) => (
                <div
                  key={query.id}
                  className={cn(
                    "border border-border rounded-lg p-4 transition-colors",
                    selectedQueries.has(query.id) && "bg-accent"
                  )}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3 flex-1">
                      <input
                        type="checkbox"
                        checked={selectedQueries.has(query.id)}
                        onChange={() => handleSelectQuery(query.id)}
                        className="mt-1 rounded"
                      />
                      
                      <div className="flex-1 min-w-0">
                        {/* Query header */}
                        <div className="flex items-center space-x-3 mb-2">
                          <span className={cn(
                            "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
                            getQueryTypeColor(query.query_type)
                          )}>
                            {query.query_type === 'natural' ? 'Natural Language' : 'SQL'}
                          </span>
                          
                          <div className="flex items-center space-x-2">
                            {query.success ? (
                              <CheckCircle className="h-4 w-4 text-green-600" />
                            ) : (
                              <AlertCircle className="h-4 w-4 text-red-600" />
                            )}
                            <span className={cn(
                              "text-sm font-medium",
                              query.success ? "text-green-600" : "text-red-600"
                            )}>
                              {query.success ? 'Success' : 'Failed'}
                            </span>
                          </div>
                          
                          <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                            <span className="flex items-center">
                              <Clock className="h-3 w-3 mr-1" />
                              {formatDuration(query.execution_time_ms)}
                            </span>
                            {query.row_count !== undefined && (
                              <span>{formatRowCount(query.row_count)} rows</span>
                            )}
                            <span>{new Date(query.timestamp).toLocaleString()}</span>
                          </div>
                        </div>

                        {/* Query text */}
                        <div className="mb-2">
                          <p className="text-sm font-medium text-foreground mb-1">Query:</p>
                          <code className="text-xs bg-muted p-2 rounded block overflow-x-auto">
                            {query.query_text}
                          </code>
                        </div>

                        {/* Generated SQL (if different from query) */}
                        {query.generated_sql && query.generated_sql !== query.query_text && (
                          <div className="mb-2">
                            <p className="text-sm font-medium text-foreground mb-1">Generated SQL:</p>
                            <code className="text-xs bg-muted p-2 rounded block overflow-x-auto">
                              {query.generated_sql}
                            </code>
                          </div>
                        )}

                        {/* Error message */}
                        {query.error_message && (
                          <div className="mb-2">
                            <p className="text-sm font-medium text-red-600 mb-1">Error:</p>
                            <p className="text-xs text-red-600 bg-red-50 p-2 rounded">
                              {query.error_message}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center space-x-2 ml-4">
                      <Button variant="outline" size="sm">
                        <Play className="h-3 w-3 mr-1" />
                        Re-run
                      </Button>
                      <Button variant="outline" size="sm">
                        <Download className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <Clock className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Query History</h3>
              <p className="text-muted-foreground mb-4">
                {searchTerm || filterType !== 'all' 
                  ? "No queries match your current filters"
                  : "You haven't run any queries yet"
                }
              </p>
              {searchTerm || filterType !== 'all' ? (
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setSearchTerm('');
                    setFilterType('all');
                  }}
                >
                  Clear Filters
                </Button>
              ) : (
                <Button>
                  Start Querying
                </Button>
              )}
            </div>
          )}

          {/* Pagination */}
          {filteredQueries.length >= pageSize && (
            <div className="flex items-center justify-between mt-6 pt-4 border-t border-border">
              <p className="text-sm text-muted-foreground">
                Showing {page * pageSize + 1} to {Math.min((page + 1) * pageSize, filteredQueries.length)} of {filteredQueries.length} queries
              </p>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(Math.max(0, page - 1))}
                  disabled={page === 0}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(page + 1)}
                  disabled={filteredQueries.length < pageSize}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default QueryHistory;