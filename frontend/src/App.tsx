import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from './components/ui/toaster';
import { ThemeProvider } from './components/theme-provider';
import Layout from './components/layout';
import Dashboard from './pages/Dashboard';
import ChatPage from './pages/Chat';
import SchemaExplorer from './pages/SchemaExplorer';
import SQLEditor from './pages/SQLEditor';
import QueryHistory from './pages/QueryHistory';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultTheme="light">
        <Router>
          <div className="min-h-screen bg-background">
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/chat" element={<ChatPage />} />
                <Route path="/schema" element={<SchemaExplorer />} />
                <Route path="/sql" element={<SQLEditor />} />
                <Route path="/history" element={<QueryHistory />} />
              </Routes>
            </Layout>
            <Toaster />
          </div>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;