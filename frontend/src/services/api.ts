import {
  QueryRequest,
  QueryResponse,
  SchemaResponse,
  ChatMessage,
  QueryHistoryItem,
  ApiError,
  ApiClient
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiClientImpl implements ApiClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const config = { ...defaultOptions, ...options };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new ApiError({
          message: errorData?.detail || errorData?.error || `HTTP ${response.status}`,
          status: response.status,
          details: errorData
        });
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      // Network or other errors
      throw new ApiError({
        message: error instanceof Error ? error.message : 'Unknown error occurred',
        details: error
      });
    }
  }

  // Query execution
  async executeQuery(request: QueryRequest): Promise<QueryResponse> {
    return this.request<QueryResponse>('/api/query/execute', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Query validation
  async validateQuery(request: QueryRequest): Promise<{ is_valid: boolean; error_message?: string }> {
    return this.request('/api/query/validate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Query plan
  async getQueryPlan(request: QueryRequest): Promise<{ query: string; plan: string; estimated_cost?: any }> {
    return this.request('/api/query/plan', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Query history
  async getQueryHistory(limit = 50, offset = 0): Promise<QueryHistoryItem[]> {
    const response = await this.request<{ success: boolean; history: QueryHistoryItem[] }>(
      `/api/query/history?limit=${limit}&offset=${offset}`
    );
    return response.history;
  }

  // Schema operations
  async getSchema(includeRelationships = true): Promise<SchemaResponse> {
    return this.request<SchemaResponse>('/api/schema/', {
      method: 'POST',
      body: JSON.stringify({
        include_relationships: includeRelationships,
      }),
    });
  }

  async getTables(): Promise<{ success: boolean; tables: string[] }> {
    return this.request('/api/schema/tables');
  }

  async getTableInfo(tableName: string): Promise<any> {
    return this.request(`/api/schema/tables/${encodeURIComponent(tableName)}`);
  }

  async getSchemaGraph(): Promise<{ success: boolean; graph: { nodes: any[]; edges: any[] } }> {
    return this.request('/api/schema/graph');
  }

  async searchSchema(query: string, limit = 10): Promise<{ success: boolean; results: any[] }> {
    return this.request(`/api/schema/search?q=${encodeURIComponent(query)}&limit=${limit}`);
  }

  // Chat operations
  async createChatSession(): Promise<{ success: boolean; session_id: string }> {
    return this.request('/api/chat/sessions', {
      method: 'POST',
    });
  }

  async getChatSession(sessionId: string): Promise<{ success: boolean; session: any }> {
    return this.request(`/api/chat/sessions/${sessionId}`);
  }

  async sendChatMessage(sessionId: string, message: string): Promise<{ success: boolean; response: ChatMessage }> {
    return this.request(`/api/chat/sessions/${sessionId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  }

  async deleteChatSession(sessionId: string): Promise<{ success: boolean }> {
    return this.request(`/api/chat/sessions/${sessionId}`, {
      method: 'DELETE',
    });
  }

  // WebSocket connection for real-time chat
  connectWebSocket(sessionId: string): WebSocket {
    const wsUrl = this.baseURL.replace('http', 'ws');
    return new WebSocket(`${wsUrl}/api/chat/sessions/${sessionId}/ws`);
  }

  // Health check
  async healthCheck(): Promise<{
    status: string;
    timestamp: string;
    database_connection: boolean;
    vector_store_connection: boolean;
    ai_service: boolean;
  }> {
    return this.request('/health');
  }

  // Export functionality (client-side)
  exportToCSV(data: any[], filename: string = 'query_results.csv'): void {
    if (data.length === 0) return;

    const headers = Object.keys(data[0]);
    const csvContent = [
      headers.join(','),
      ...data.map(row => 
        headers.map(header => {
          const value = row[header];
          // Escape commas and quotes in CSV
          if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
            return `"${value.replace(/"/g, '""')}"`;
          }
          return value;
        }).join(',')
      )
    ].join('\n');

    this.downloadFile(csvContent, filename, 'text/csv');
  }

  exportToJSON(data: any[], filename: string = 'query_results.json'): void {
    const jsonContent = JSON.stringify(data, null, 2);
    this.downloadFile(jsonContent, filename, 'application/json');
  }

  private downloadFile(content: string, filename: string, mimeType: string): void {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
  }
}

// API Error class
class ApiError extends Error {
  public status?: number;
  public code?: string;
  public details?: any;

  constructor({ message, status, code, details }: {
    message: string;
    status?: number;
    code?: string;
    details?: any;
  }) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

// Export singleton instance
export const apiClient = new ApiClientImpl();
export { ApiError };