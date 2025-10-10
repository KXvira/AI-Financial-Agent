// components/AIChat.tsx
"use client";

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { aiClient, AIResponse } from '../utils/aiApi';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  confidence?: number;
  insights?: string[];
}

export default function AIChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'error'>('connecting');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages update
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check connection status on mount
  useEffect(() => {
    const checkConnection = async () => {
      try {
        await aiClient.checkHealth();
        setConnectionStatus('connected');
        
        // Add welcome message
        setMessages([{
          id: Date.now().toString(),
          content: "Hello! I'm your AI Financial Assistant. I can help you analyze your financial data, provide insights about your transactions, invoices, and cash flow. What would you like to know?",
          sender: 'ai',
          timestamp: new Date(),
          confidence: 0.95,
          insights: [
            "Ask about your transaction patterns",
            "Inquire about invoice status",
            "Get cash flow analysis",
            "Request financial recommendations"
          ]
        }]);
      } catch (error) {
        setConnectionStatus('error');
        console.error('Failed to connect to AI service:', error);
      }
    };

    checkConnection();
  }, []);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response: AIResponse = await aiClient.askQuestion(inputMessage);
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.answer,
        sender: 'ai',
        timestamp: new Date(),
        confidence: response.confidence || 0.8,
        insights: response.sources || [],
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I'm sorry, I encountered an error while processing your request. Please make sure the AI service is running and try again.",
        sender: 'ai',
        timestamp: new Date(),
        confidence: 0,
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (connectionStatus === 'connecting') {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Connecting to AI service...</p>
        </div>
      </div>
    );
  }

  if (connectionStatus === 'error') {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="text-center">
          <div className="text-red-600 mb-2">⚠️ Connection Error</div>
          <p className="text-red-700 mb-4">Unable to connect to the AI service.</p>
          <p className="text-sm text-red-600">
            Please ensure the AI backend service is running on port 8000.
          </p>
          <button 
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md border h-[600px] flex flex-col">
      {/* Header */}
      <div className="border-b p-4 bg-gray-50 rounded-t-lg">
        <div className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-blue-600" />
          <h3 className="font-semibold text-gray-800">AI Financial Assistant</h3>
          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
            Connected
          </span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.sender === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {/* Message content */}
              <div className="flex items-start gap-2">
                {message.sender === 'ai' && (
                  <Bot className="h-4 w-4 mt-0.5 text-blue-600" />
                )}
                {message.sender === 'user' && (
                  <User className="h-4 w-4 mt-0.5 text-white" />
                )}
                <div className="flex-1">
                  <p className="text-sm leading-relaxed">{message.content}</p>
                  
                  {/* Insights */}
                  {message.insights && message.insights.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-200">
                      <p className="text-xs text-gray-600 mb-1">💡 Insights:</p>
                      <ul className="text-xs text-gray-600 space-y-1">
                        {message.insights.map((insight, idx) => (
                          <li key={idx}>• {insight}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {/* Confidence & Timestamp */}
                  <div className="flex items-center justify-between mt-2 text-xs opacity-70">
                    <span>
                      {message.timestamp.toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                    {message.confidence && (
                      <span>
                        Confidence: {Math.round(message.confidence * 100)}%
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-800 max-w-[80%] rounded-lg p-3">
              <div className="flex items-center gap-2">
                <Bot className="h-4 w-4 text-blue-600" />
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm">Thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4 bg-gray-50">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about your financial data..."
            className="flex-1 px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            title="Send message"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
