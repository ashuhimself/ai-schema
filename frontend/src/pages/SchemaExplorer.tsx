import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Table, Database, Eye, Info } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import GraphView from '../components/schema/GraphView';
import { apiClient } from '../services/api';
import { cn } from '../utils/cn';
import { TableSchema, ColumnInfo, Relationship } from '../types';

const SchemaExplorer: React.FC = () => {
  const [selectedTable, setSelectedTable] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [viewMode, setViewMode] = useState<'graph' | 'list'>('graph');

  // Fetch schema data
  const { data: schemaData, isLoading: schemaLoading, error: schemaError } = useQuery({
    queryKey: ['schema'],
    queryFn: () => apiClient.getSchema(),
  });

  // Fetch graph data for visualization
  const { data: graphData, isLoading: graphLoading } = useQuery({
    queryKey: ['schema-graph'],
    queryFn: () => apiClient.getSchemaGraph(),
  });

  // Fetch specific table info when selected
  const { data: tableInfo, isLoading: tableLoading } = useQuery({
    queryKey: ['table-info', selectedTable],
    queryFn: () => apiClient.getTableInfo(selectedTable),
    enabled: !!selectedTable,
  });

  const schema = schemaData?.schema || {};
  const relationships = schemaData?.relationships || [];
  const graphNodes = graphData?.graph?.nodes || [];
  const graphEdges = graphData?.graph?.edges || [];

  const filteredTables = Object.keys(schema).filter(tableName =>
    tableName.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleTableSelect = (tableName: string) => {
    setSelectedTable(tableName === selectedTable ? '' : tableName);
  };

  const getColumnTypeColor = (type: string) => {
    const typeColors: Record<string, string> = {
      'integer': 'text-blue-600',
      'varchar': 'text-green-600',
      'text': 'text-green-600',
      'boolean': 'text-purple-600',
      'timestamp': 'text-orange-600',
      'date': 'text-orange-600',
      'decimal': 'text-red-600',
      'float': 'text-red-600',
    };
    
    const normalizedType = type.toLowerCase();
    for (const [key, color] of Object.entries(typeColors)) {
      if (normalizedType.includes(key)) {
        return color;
      }
    }
    return 'text-muted-foreground';
  };

  if (schemaLoading) {
    return (
      <div className="p-6 space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-muted rounded w-1/4 mb-4"></div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="h-96 bg-muted rounded"></div>
            <div className="lg:col-span-2 h-96 bg-muted rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (schemaError) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <Database className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">Unable to Load Schema</h3>
          <p className="text-muted-foreground mb-4">
            There was an error connecting to the database or loading the schema.
          </p>
          <Button onClick={() => window.location.reload()}>
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Schema Explorer</h1>
          <p className="text-muted-foreground">
            Explore database tables, columns, and relationships
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant={viewMode === 'graph' ? 'default' : 'outline'}
            onClick={() => setViewMode('graph')}
            size="sm"
          >
            Graph View
          </Button>
          <Button
            variant={viewMode === 'list' ? 'default' : 'outline'}
            onClick={() => setViewMode('list')}
            size="sm"
          >
            List View
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tables Sidebar */}
        <div className="space-y-4">
          <Card>
            <CardHeader className="pb-4">
              <CardTitle className="text-lg flex items-center">
                <Table className="h-5 w-5 mr-2" />
                Tables ({Object.keys(schema).length})
              </CardTitle>
              <div className="relative">
                <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search tables..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </CardHeader>
            <CardContent className="max-h-96 overflow-y-auto scrollbar-thin">
              <div className="space-y-1">
                {filteredTables.map((tableName) => {
                  const tableSchema = schema[tableName] as TableSchema;
                  const isSelected = selectedTable === tableName;
                  
                  return (
                    <Button
                      key={tableName}
                      variant={isSelected ? 'default' : 'ghost'}
                      size="sm"
                      className="w-full justify-start text-left h-auto p-3"
                      onClick={() => handleTableSelect(tableName)}
                    >
                      <div className="w-full">
                        <div className="font-medium truncate">{tableName}</div>
                        <div className="text-xs text-muted-foreground mt-1">
                          {tableSchema?.columns?.length || 0} columns
                          {tableSchema?.row_count && (
                            <span className="ml-2">
                              • {tableSchema.row_count.toLocaleString()} rows
                            </span>
                          )}
                        </div>
                      </div>
                    </Button>
                  );
                })}
                
                {filteredTables.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    <Search className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No tables found</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {viewMode === 'graph' ? (
            <GraphView
              nodes={graphNodes}
              edges={graphEdges}
              selectedTable={selectedTable}
              onTableSelect={handleTableSelect}
              className="h-96"
            />
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Table Overview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(schema).map(([tableName, tableSchema]) => (
                    <div
                      key={tableName}
                      className={cn(
                        "p-4 border border-border rounded-lg cursor-pointer transition-colors hover:bg-accent",
                        selectedTable === tableName && "bg-accent"
                      )}
                      onClick={() => handleTableSelect(tableName)}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="font-semibold truncate">{tableName}</h3>
                        <Table className="h-4 w-4 text-muted-foreground flex-shrink-0 ml-2" />
                      </div>
                      <div className="text-sm text-muted-foreground space-y-1">
                        <div>{(tableSchema as TableSchema)?.columns?.length || 0} columns</div>
                        {(tableSchema as TableSchema)?.row_count && (
                          <div>{(tableSchema as TableSchema).row_count!.toLocaleString()} rows</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Table Details */}
          {selectedTable && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Info className="h-5 w-5 mr-2" />
                  {selectedTable}
                  {tableLoading && (
                    <div className="ml-2 animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {tableLoading ? (
                  <div className="animate-pulse space-y-2">
                    {[...Array(5)].map((_, i) => (
                      <div key={i} className="h-4 bg-muted rounded w-full"></div>
                    ))}
                  </div>
                ) : tableInfo ? (
                  <div className="space-y-4">
                    {/* Table Stats */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="bg-muted p-3 rounded-lg">
                        <div className="text-xs text-muted-foreground">Columns</div>
                        <div className="font-semibold">{tableInfo.columns?.length || 0}</div>
                      </div>
                      {tableInfo.row_count && (
                        <div className="bg-muted p-3 rounded-lg">
                          <div className="text-xs text-muted-foreground">Rows</div>
                          <div className="font-semibold">{tableInfo.row_count.toLocaleString()}</div>
                        </div>
                      )}
                      {tableInfo.size_bytes && (
                        <div className="bg-muted p-3 rounded-lg">
                          <div className="text-xs text-muted-foreground">Size</div>
                          <div className="font-semibold">
                            {(tableInfo.size_bytes / (1024 * 1024)).toFixed(1)} MB
                          </div>
                        </div>
                      )}
                      {tableInfo.created && (
                        <div className="bg-muted p-3 rounded-lg">
                          <div className="text-xs text-muted-foreground">Created</div>
                          <div className="font-semibold text-xs">
                            {new Date(tableInfo.created).toLocaleDateString()}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Columns Table */}
                    <div className="border border-border rounded-lg overflow-hidden">
                      <table className="w-full">
                        <thead className="bg-muted">
                          <tr>
                            <th className="px-4 py-2 text-left text-sm font-semibold">Column</th>
                            <th className="px-4 py-2 text-left text-sm font-semibold">Type</th>
                            <th className="px-4 py-2 text-left text-sm font-semibold">Nullable</th>
                            <th className="px-4 py-2 text-left text-sm font-semibold">Key</th>
                          </tr>
                        </thead>
                        <tbody>
                          {tableInfo.columns?.map((column: ColumnInfo, index: number) => (
                            <tr key={column.name} className={index % 2 === 0 ? 'bg-background' : 'bg-muted/50'}>
                              <td className="px-4 py-2 font-medium">{column.name}</td>
                              <td className={cn(
                                "px-4 py-2 font-mono text-sm",
                                getColumnTypeColor(column.type)
                              )}>
                                {column.type}
                              </td>
                              <td className="px-4 py-2 text-sm">
                                {column.nullable ? 'Yes' : 'No'}
                              </td>
                              <td className="px-4 py-2 text-sm">
                                {column.primary_key && (
                                  <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                                    PK
                                  </span>
                                )}
                                {column.foreign_keys && column.foreign_keys.length > 0 && (
                                  <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded ml-1">
                                    FK
                                  </span>
                                )}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* Relationships */}
                    {relationships.filter(rel => 
                      rel.from_table === selectedTable || rel.to_table === selectedTable
                    ).length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2">Relationships</h4>
                        <div className="space-y-2">
                          {relationships
                            .filter(rel => rel.from_table === selectedTable || rel.to_table === selectedTable)
                            .map((rel, index) => (
                              <div key={index} className="bg-muted p-3 rounded-lg text-sm">
                                <div className="font-medium">
                                  {rel.from_table === selectedTable ? (
                                    <>
                                      <span className="text-primary">{rel.from_column}</span>
                                      {' → '}
                                      <span>{rel.to_table}.{rel.to_column}</span>
                                    </>
                                  ) : (
                                    <>
                                      <span>{rel.from_table}.{rel.from_column}</span>
                                      {' → '}
                                      <span className="text-primary">{rel.to_column}</span>
                                    </>
                                  )}
                                </div>
                              </div>
                            ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <Eye className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">Select a table to view details</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default SchemaExplorer;