// components/AIChat.tsx
"use client";

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, TrendingUp, DollarSign, FileText, Users } from 'lucide-react';
import { aiClient, AIResponse } from '../utils/aiApi';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  confidence?: number;
  insights?: string[];
}

// Component to format AI responses with professional Markdown styling
function FormattedAIResponse({ content }: { content: string }) {
  return (
    <div className="markdown-content text-sm leading-relaxed">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Style headers
          h1: ({ node, ...props }) => (
            <h1 className="text-xl font-bold text-gray-900 mb-3 mt-4 pb-2 border-b border-gray-200" {...props} />
          ),
          h2: ({ node, ...props }) => (
            <h2 className="text-lg font-semibold text-gray-900 mb-2 mt-3 flex items-center gap-2" {...props} />
          ),
          h3: ({ node, ...props }) => (
            <h3 className="text-base font-semibold text-gray-800 mb-2 mt-2" {...props} />
          ),
          
          // Style paragraphs
          p: ({ node, ...props }) => (
            <p className="text-gray-700 mb-3" {...props} />
          ),
          
          // Style lists
          ul: ({ node, ...props }) => (
            <ul className="space-y-2 mb-3 ml-4" {...props} />
          ),
          ol: ({ node, ...props }) => (
            <ol className="space-y-2 mb-3 ml-4 list-decimal" {...props} />
          ),
          li: ({ node, ...props }) => (
            <li className="text-gray-700 pl-2" {...props} />
          ),
          
          // Style strong/bold text
          strong: ({ node, ...props }) => (
            <strong className="font-semibold text-gray-900" {...props} />
          ),
          
          // Style emphasis/italic text
          em: ({ node, ...props }) => (
            <em className="italic text-gray-800" {...props} />
          ),
          
          // Style code blocks
          code: ({ node, inline, ...props }: any) => 
            inline ? (
              <code className="bg-gray-100 text-red-600 px-1.5 py-0.5 rounded text-xs font-mono" {...props} />
            ) : (
              <code className="block bg-gray-900 text-gray-100 p-3 rounded-lg text-xs font-mono overflow-x-auto mb-3" {...props} />
            ),
          
          // Style tables
          table: ({ node, ...props }) => (
            <div className="overflow-x-auto mb-3">
              <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg" {...props} />
            </div>
          ),
          thead: ({ node, ...props }) => (
            <thead className="bg-gray-50" {...props} />
          ),
          tbody: ({ node, ...props }) => (
            <tbody className="bg-white divide-y divide-gray-200" {...props} />
          ),
          tr: ({ node, ...props }) => (
            <tr className="hover:bg-gray-50" {...props} />
          ),
          th: ({ node, ...props }) => (
            <th className="px-4 py-2 text-left text-xs font-semibold text-gray-900 uppercase tracking-wider" {...props} />
          ),
          td: ({ node, ...props }) => (
            <td className="px-4 py-2 text-sm text-gray-700" {...props} />
          ),
          
          // Style blockquotes
          blockquote: ({ node, ...props }) => (
            <blockquote className="border-l-4 border-blue-500 pl-4 py-2 italic text-gray-700 bg-blue-50 rounded-r mb-3" {...props} />
          ),
          
          // Style links
          a: ({ node, ...props }) => (
            <a className="text-blue-600 hover:text-blue-800 underline" {...props} />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
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
          content: "**Welcome to AI Financial Insights**\n\nHello! I'm your AI Financial Assistant powered by advanced analytics. I'm here to help you make data-driven decisions for your business.\n\n**I can assist you with:**\n* Analyzing transaction patterns and trends\n* Providing invoice status and payment insights\n* Generating comprehensive cash flow analysis\n* Offering strategic financial recommendations\n* Identifying opportunities for cost optimization\n\nWhat would you like to explore today?",
          sender: 'ai',
          timestamp: new Date(),
          confidence: 0.95,
          insights: []
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
              className={`max-w-[85%] rounded-lg p-4 shadow-sm ${
                message.sender === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white border border-gray-200 text-gray-800'
              }`}
            >
              {/* Message content */}
              <div className="flex items-start gap-2">
                {message.sender === 'ai' && (
                  <Bot className="h-4 w-4 mt-0.5 text-blue-600 flex-shrink-0" />
                )}
                {message.sender === 'user' && (
                  <User className="h-4 w-4 mt-0.5 text-white flex-shrink-0" />
                )}
                <div className="flex-1">
                  {message.sender === 'ai' ? (
                    <FormattedAIResponse content={message.content} />
                  ) : (
                    <p className="text-sm leading-relaxed">{message.content}</p>
                  )}
                  
                  {/* Insights */}
                  {message.insights && message.insights.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <div className="flex items-center gap-1 mb-2">
                        <span className="text-xs font-semibold text-blue-600">💡 Key Insights</span>
                      </div>
                      <ul className="text-xs text-gray-700 space-y-1.5">
                        {message.insights.map((insight, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <span className="text-blue-500 mt-0.5">•</span>
                            <span>{insight}</span>
                          </li>
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
                    {message.confidence && message.confidence > 0 && (
                      <span className="flex items-center gap-1">
                        <span className={`inline-block w-2 h-2 rounded-full ${
                          message.confidence > 0.8 ? 'bg-green-500' :
                          message.confidence > 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}></span>
                        {Math.round(message.confidence * 100)}%
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
