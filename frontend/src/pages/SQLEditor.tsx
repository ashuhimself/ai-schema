import React, { useState, useRef } from 'react';
import { Play, Save, FileText, Clock, Download, Eye, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { apiClient } from '../services/api';
import { QueryResponse, QueryRequest } from '../types';
import { cn } from '../utils/cn';

const SQLEditor: React.FC = () => {
  const [sqlQuery, setSqlQuery] = useState('-- Enter your SQL query here\nSELECT * FROM users LIMIT 10;');
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<any>(null);
  const [fileName, setFileName] = useState('untitled.sql');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const executeQuery = async () => {
    if (!sqlQuery.trim()) return;

    setIsExecuting(true);
    setQueryResult(null);
    
    try {
      const request: QueryRequest = {
        query: sqlQuery,
        query_type: 'sql',
        limit: 1000
      };
      
      const result = await apiClient.executeQuery(request);
      setQueryResult(result);
    } catch (error) {
      console.error('Query execution failed:', error);
      setQueryResult({
        success: false,
        error: error instanceof Error ? error.message : 'Query execution failed',
        execution_time_ms: 0,
        row_count: 0
      });
    } finally {
      setIsExecuting(false);
    }
  };

  const validateQuery = async () => {
    if (!sqlQuery.trim()) return;

    setIsValidating(true);
    
    try {
      const request: QueryRequest = {
        query: sqlQuery,
        query_type: 'sql'
      };
      
      const result = await apiClient.validateQuery(request);
      setValidationResult(result);
    } catch (error) {
      console.error('Query validation failed:', error);
      setValidationResult({
        is_valid: false,
        error_message: error instanceof Error ? error.message : 'Validation failed'
      });
    } finally {
      setIsValidating(false);
    }
  };

  const getQueryPlan = async () => {
    if (!sqlQuery.trim()) return;

    try {
      const request: QueryRequest = {
        query: sqlQuery,
        query_type: 'sql'
      };
      
      const result = await apiClient.getQueryPlan(request);
      console.log('Query plan:', result);
      // You could show this in a modal or separate panel
    } catch (error) {
      console.error('Failed to get query plan:', error);
    }
  };

  const saveQuery = () => {
    const blob = new Blob([sqlQuery], { type: 'text/sql' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const exportResults = (format: 'csv' | 'json') => {
    if (!queryResult?.results?.data) return;

    if (format === 'csv') {
      apiClient.exportToCSV(queryResult.results.data, `query_results_${Date.now()}.csv`);
    } else if (format === 'json') {
      apiClient.exportToJSON(queryResult.results.data, `query_results_${Date.now()}.json`);
    }
  };

  const insertSampleQuery = () => {
    const sampleQueries = [
      "-- Show all tables\nSHOW TABLES;",
      "-- Table information\nDESCRIBE users;",
      "-- Basic SELECT with conditions\nSELECT id, name, email\nFROM users\nWHERE created_at > '2023-01-01'\nORDER BY created_at DESC\nLIMIT 20;",
      "-- Aggregation query\nSELECT \n  EXTRACT(MONTH FROM created_at) as month,\n  COUNT(*) as user_count,\n  COUNT(DISTINCT email) as unique_emails\nFROM users\nWHERE created_at >= '2023-01-01'\nGROUP BY EXTRACT(MONTH FROM created_at)\nORDER BY month;",
      "-- JOIN example\nSELECT \n  u.name,\n  u.email,\n  COUNT(o.id) as order_count,\n  SUM(o.total) as total_spent\nFROM users u\nLEFT JOIN orders o ON u.id = o.user_id\nWHERE u.created_at > '2023-01-01'\nGROUP BY u.id, u.name, u.email\nHAVING COUNT(o.id) > 0\nORDER BY total_spent DESC\nLIMIT 10;"
    ];
    
    const randomQuery = sampleQueries[Math.floor(Math.random() * sampleQueries.length)];
    setSqlQuery(randomQuery);
  };

  const formatSQL = () => {
    // Basic SQL formatting - in production, use a proper SQL formatter
    const formatted = sqlQuery
      .replace(/\bSELECT\b/gi, 'SELECT')
      .replace(/\bFROM\b/gi, '\nFROM')
      .replace(/\bWHERE\b/gi, '\nWHERE')
      .replace(/\bGROUP BY\b/gi, '\nGROUP BY')
      .replace(/\bORDER BY\b/gi, '\nORDER BY')
      .replace(/\bLIMIT\b/gi, '\nLIMIT');
    
    setSqlQuery(formatted);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">SQL Editor</h1>
          <p className="text-muted-foreground">
            Write and execute SQL queries directly against your database
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Input
            value={fileName}
            onChange={(e) => setFileName(e.target.value)}
            className="w-48"
            placeholder="Filename..."
          />
          <Button variant="outline" onClick={saveQuery}>
            <Save className="h-4 w-4 mr-2" />
            Save
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* SQL Editor */}
        <div className="lg:col-span-3 space-y-4">
          <Card>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Query Editor</CardTitle>
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={insertSampleQuery}
                  >
                    <FileText className="h-4 w-4 mr-2" />
                    Sample
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={formatSQL}
                  >
                    Format
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={validateQuery}
                    disabled={isValidating}
                  >
                    {isValidating ? (
                      <div className="h-4 w-4 animate-spin rounded-full border-b-2 border-current" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                    Validate
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={getQueryPlan}
                  >
                    <Clock className="h-4 w-4 mr-2" />
                    Plan
                  </Button>
                  <Button
                    onClick={executeQuery}
                    disabled={isExecuting}
                    size="sm"
                  >
                    {isExecuting ? (
                      <div className="h-4 w-4 animate-spin rounded-full border-b-2 border-primary-foreground" />
                    ) : (
                      <Play className="h-4 w-4" />
                    )}
                    Run
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <textarea
                ref={textareaRef}
                value={sqlQuery}
                onChange={(e) => setSqlQuery(e.target.value)}
                className="w-full h-64 p-4 font-mono text-sm bg-background border-0 resize-none focus:outline-none focus:ring-0"
                placeholder="-- Enter your SQL query here..."
                spellCheck={false}
              />
            </CardContent>
          </Card>

          {/* Validation Results */}
          {validationResult && (
            <Card className={cn(
              "border-l-4",
              validationResult.is_valid ? "border-l-green-500" : "border-l-red-500"
            )}>
              <CardContent className="pt-4">
                <div className="flex items-start space-x-2">
                  {validationResult.is_valid ? (
                    <div className="flex-shrink-0 w-5 h-5 rounded-full bg-green-100 flex items-center justify-center">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    </div>
                  ) : (
                    <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
                  )}
                  <div>
                    <p className={cn(
                      "font-medium",
                      validationResult.is_valid ? "text-green-700" : "text-red-700"
                    )}>
                      {validationResult.is_valid ? "Query is valid" : "Query has errors"}
                    </p>
                    {validationResult.error_message && (
                      <p className="text-sm text-muted-foreground mt-1">
                        {validationResult.error_message}
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Query Results */}
          {queryResult && (
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-lg">
                    Results
                    {queryResult.success && queryResult.row_count !== undefined && (
                      <span className="ml-2 text-sm font-normal text-muted-foreground">
                        ({queryResult.row_count} rows)
                      </span>
                    )}
                  </CardTitle>
                  {queryResult.success && queryResult.results && (
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-muted-foreground">
                        {queryResult.execution_time_ms}ms
                      </span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => exportResults('csv')}
                      >
                        <Download className="h-4 w-4 mr-2" />
                        CSV
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => exportResults('json')}
                      >
                        <Download className="h-4 w-4 mr-2" />
                        JSON
                      </Button>
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                {queryResult.success && queryResult.results ? (
                  <div className="overflow-auto max-h-96 border border-border rounded-lg">
                    <table className="w-full text-sm">
                      <thead className="bg-muted sticky top-0">
                        <tr>
                          {queryResult.results.columns.map((column, index) => (
                            <th
                              key={index}
                              className="px-3 py-2 text-left font-semibold border-r border-border last:border-r-0"
                            >
                              {column}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {queryResult.results.data.map((row, rowIndex) => (
                          <tr
                            key={rowIndex}
                            className={rowIndex % 2 === 0 ? 'bg-background' : 'bg-muted/50'}
                          >
                            {queryResult.results!.columns.map((column, colIndex) => (
                              <td
                                key={colIndex}
                                className="px-3 py-2 border-r border-border last:border-r-0 font-mono text-xs"
                              >
                                {row[column] === null ? (
                                  <span className="text-muted-foreground italic">NULL</span>
                                ) : (
                                  String(row[column])
                                )}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className={cn(
                    "p-4 rounded-lg border",
                    queryResult.success ? "bg-green-50 border-green-200" : "bg-red-50 border-red-200"
                  )}>
                    <div className="flex items-start space-x-2">
                      {queryResult.success ? (
                        <div className="flex-shrink-0 w-5 h-5 rounded-full bg-green-100 flex items-center justify-center">
                          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        </div>
                      ) : (
                        <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
                      )}
                      <div>
                        <p className={cn(
                          "font-medium",
                          queryResult.success ? "text-green-700" : "text-red-700"
                        )}>
                          {queryResult.success ? "Query executed successfully" : "Query failed"}
                        </p>
                        {queryResult.error && (
                          <p className="text-sm text-red-600 mt-1">
                            {queryResult.error}
                          </p>
                        )}
                        {queryResult.execution_time_ms !== undefined && (
                          <p className="text-sm text-muted-foreground mt-1">
                            Execution time: {queryResult.execution_time_ms}ms
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="outline" size="sm" className="w-full justify-start">
                <FileText className="h-4 w-4 mr-2" />
                New Query
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start">
                <FileText className="h-4 w-4 mr-2" />
                Open File
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start" onClick={saveQuery}>
                <Save className="h-4 w-4 mr-2" />
                Save Query
              </Button>
              <Button variant="outline" size="sm" className="w-full justify-start">
                <Clock className="h-4 w-4 mr-2" />
                History
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Keyboard Shortcuts</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Run Query</span>
                <code className="bg-muted px-1 rounded">Ctrl+Enter</code>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Save</span>
                <code className="bg-muted px-1 rounded">Ctrl+S</code>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Format</span>
                <code className="bg-muted px-1 rounded">Ctrl+Shift+F</code>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">New Query</span>
                <code className="bg-muted px-1 rounded">Ctrl+N</code>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">SQL Tips</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <div>
                <p className="font-medium">Limit Results</p>
                <p className="text-muted-foreground">Always use LIMIT when exploring data</p>
              </div>
              <div>
                <p className="font-medium">Use Indexes</p>
                <p className="text-muted-foreground">Filter on indexed columns for better performance</p>
              </div>
              <div>
                <p className="font-medium">Validate First</p>
                <p className="text-muted-foreground">Check query syntax before execution</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default SQLEditor;