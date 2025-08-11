// Core API types
export interface QueryRequest {
  query: string;
  query_type: 'natural' | 'sql';
  limit?: number;
  database_type?: string;
}

export interface QueryResponse {
  success: boolean;
  query_id?: string;
  generated_sql?: string;
  results?: QueryResults;
  metadata?: Record<string, any>;
  insights?: string;
  error?: string;
  execution_time_ms?: number;
  row_count?: number;
}

export interface QueryResults {
  columns: string[];
  data: Record<string, any>[];
  total_rows: number;
}

export interface SchemaResponse {
  success: boolean;
  schema?: Record<string, TableSchema>;
  relationships?: Relationship[];
  error?: string;
}

export interface TableSchema {
  columns: ColumnInfo[];
  row_count?: number;
  table_type?: string;
  size_bytes?: number;
  created?: string;
  modified?: string;
  indexes?: string[];
  foreign_keys?: ForeignKey[];
}

export interface ColumnInfo {
  name: string;
  type: string;
  nullable?: boolean;
  primary_key?: boolean;
  foreign_keys?: string[];
  description?: string;
}

export interface ForeignKey {
  column: string;
  references: string;
}

export interface Relationship {
  from_table: string;
  from_column: string;
  to_table: string;
  to_column: string;
}

// Chat types
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  query_id?: string;
  metadata?: Record<string, any>;
}

export interface ChatSession {
  session_id: string;
  messages: ChatMessage[];
  created_at: string;
  updated_at: string;
}

// Graph types for schema visualization
export interface GraphNode {
  id: string;
  label: string;
  type: 'table' | 'column';
  columns?: number;
  metadata?: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  type: 'foreign_key' | 'relationship';
}

export interface SchemaGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

// Query history types
export interface QueryHistoryItem {
  id: string;
  user_id?: string;
  query_text: string;
  generated_sql?: string;
  query_type: string;
  execution_time_ms?: number;
  row_count?: number;
  success: boolean;
  error_message?: string;
  timestamp: string;
}

// Application state types
export interface AppState {
  currentSession?: string;
  isConnected: boolean;
  isLoading: boolean;
  error?: string;
  theme: 'light' | 'dark';
}

// UI component types
export interface TableProps {
  columns: string[];
  data: Record<string, any>[];
  loading?: boolean;
  onSort?: (column: string, direction: 'asc' | 'desc') => void;
  onExport?: (format: 'csv' | 'excel' | 'json') => void;
}

export interface ChatProps {
  sessionId: string;
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
}

export interface SchemaExplorerProps {
  schema: Record<string, TableSchema>;
  relationships: Relationship[];
  onTableSelect?: (tableName: string) => void;
  selectedTable?: string;
}

export interface SQLEditorProps {
  value: string;
  onChange: (value: string) => void;
  onExecute?: () => void;
  onValidate?: () => void;
  readOnly?: boolean;
  language?: string;
}

// Export types
export type ExportFormat = 'csv' | 'excel' | 'json';

export interface ExportOptions {
  format: ExportFormat;
  filename?: string;
  includeHeaders?: boolean;
}

// API client types
export interface ApiClient {
  executeQuery: (request: QueryRequest) => Promise<QueryResponse>;
  getSchema: () => Promise<SchemaResponse>;
  createChatSession: () => Promise<{ session_id: string }>;
  sendChatMessage: (sessionId: string, message: string) => Promise<ChatMessage>;
  getQueryHistory: (limit?: number, offset?: number) => Promise<QueryHistoryItem[]>;
}

// Error types
export interface ApiError {
  message: string;
  status?: number;
  code?: string;
  details?: any;
}

// Theme types
export type Theme = 'light' | 'dark';

export interface ThemeConfig {
  theme: Theme;
  toggleTheme: () => void;
}