import React, { useState, useEffect, useRef } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { apiClient } from '../services/api';
import { ChatMessage } from '../types';
import { cn } from '../utils/cn';

const ChatPage: React.FC = () => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const websocketRef = useRef<WebSocket | null>(null);

  // Initialize chat session
  useEffect(() => {
    initializeSession();
    return () => {
      if (websocketRef.current) {
        websocketRef.current.close();
      }
    };
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initializeSession = async () => {
    try {
      const response = await apiClient.createChatSession();
      if (response.success) {
        setSessionId(response.session_id);
        connectWebSocket(response.session_id);
        
        // Add welcome message
        const welcomeMessage: ChatMessage = {
          role: 'assistant',
          content: "Hello! I'm your Warehouse Copilot. I can help you explore your data, write SQL queries, and analyze results. What would you like to know about your data?",
          timestamp: new Date().toISOString(),
        };
        setMessages([welcomeMessage]);
      }
    } catch (error) {
      console.error('Failed to create chat session:', error);
    }
  };

  const connectWebSocket = (sessionId: string) => {
    try {
      const ws = apiClient.connectWebSocket(sessionId);
      websocketRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'message') {
            setMessages(prev => [...prev, data.data]);
          } else if (data.error) {
            console.error('WebSocket error:', data.error);
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        } finally {
          setIsLoading(false);
        }
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
        setIsLoading(false);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !sessionId || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
        // Send via WebSocket for real-time response
        websocketRef.current.send(JSON.stringify({
          message: inputMessage
        }));
      } else {
        // Fallback to HTTP if WebSocket not available
        const response = await apiClient.sendChatMessage(sessionId, inputMessage);
        if (response.success) {
          setMessages(prev => [...prev, response.response]);
        }
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: "I'm sorry, I encountered an error while processing your message. Please try again.",
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const formatMessage = (content: string) => {
    // Basic formatting - replace with proper markdown renderer in production
    return content
      .split('\n')
      .map((line, index) => (
        <div key={index}>
          {line.startsWith('**') && line.endsWith('**') ? (
            <strong>{line.slice(2, -2)}</strong>
          ) : line.startsWith('```sql') ? (
            <pre className="bg-muted p-2 rounded-md mt-2 overflow-x-auto">
              <code className="text-sm">{line.replace('```sql', '')}</code>
            </pre>
          ) : line === '```' ? null : (
            <span>{line}</span>
          )}
        </div>
      ));
  };

  return (
    <div className="flex h-full">
      {/* Chat Messages */}
      <div className="flex-1 flex flex-col">
        <Card className="flex-1 m-4 mb-0 flex flex-col">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Chat with Warehouse Copilot
              <div className="flex items-center space-x-2 text-sm">
                <div className={cn(
                  "w-2 h-2 rounded-full",
                  isConnected ? "bg-green-500" : "bg-red-500"
                )} />
                <span className="text-muted-foreground">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </CardTitle>
          </CardHeader>
          
          <CardContent className="flex-1 flex flex-col min-h-0">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2 scrollbar-thin">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={cn(
                    "flex",
                    message.role === 'user' ? "justify-end" : "justify-start"
                  )}
                >
                  <div
                    className={cn(
                      "max-w-[70%] rounded-lg p-3",
                      message.role === 'user'
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-muted-foreground"
                    )}
                  >
                    <div className="whitespace-pre-wrap break-words">
                      {formatMessage(message.content)}
                    </div>
                    <div className="text-xs opacity-70 mt-2">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
              
              {/* Loading indicator */}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-muted text-muted-foreground rounded-lg p-3 flex items-center space-x-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Thinking...</span>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <div className="flex space-x-2">
              <Input
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything about your data..."
                disabled={isLoading || !sessionId}
                className="flex-1"
              />
              <Button
                onClick={sendMessage}
                disabled={isLoading || !inputMessage.trim() || !sessionId}
                size="icon"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sidebar with examples and tips */}
      <div className="w-80 p-4 border-l border-border">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Quick Examples</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="text-sm">
              <p className="font-medium mb-2">Try asking:</p>
              <div className="space-y-2">
                {[
                  "Show me all tables in the database",
                  "What are the top 10 customers by revenue?",
                  "How many orders were placed last month?",
                  "Show me the schema for the users table",
                  "Find all columns containing 'email'",
                ].map((example, index) => (
                  <button
                    key={index}
                    onClick={() => setInputMessage(example)}
                    className="w-full text-left p-2 text-xs bg-muted hover:bg-accent rounded-md transition-colors"
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="mt-4">
          <CardHeader>
            <CardTitle className="text-lg">Tips</CardTitle>
          </CardHeader>
          <CardContent className="text-sm space-y-2">
            <div>
              <p className="font-medium">Natural Language Queries</p>
              <p className="text-muted-foreground text-xs">
                Ask questions in plain English. I'll convert them to SQL automatically.
              </p>
            </div>
            <div>
              <p className="font-medium">Schema Exploration</p>
              <p className="text-muted-foreground text-xs">
                Ask about table structures, relationships, and column details.
              </p>
            </div>
            <div>
              <p className="font-medium">Data Analysis</p>
              <p className="text-muted-foreground text-xs">
                Request summaries, trends, and insights from your data.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ChatPage;