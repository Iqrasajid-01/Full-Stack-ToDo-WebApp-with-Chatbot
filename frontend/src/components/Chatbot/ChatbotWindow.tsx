'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useChatbot } from './useChatbot';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { Conversation } from '@/types/chatbot';

interface ChatbotWindowProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ChatbotWindow({ isOpen, onClose }: ChatbotWindowProps) {
  const {
    messages,
    conversations,
    currentConversation,
    isLoading,
    isSending,
    error,
    sendMessage,
    loadConversation,
    loadConversations,
    clearCurrentConversation,
    deleteConversation,
  } = useChatbot();

  const [showSidebar, setShowSidebar] = useState(false);
  const [hasSentGreeting, setHasSentGreeting] = useState(false);
  const [showDefaultGreeting, setShowDefaultGreeting] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversations on mount
  useEffect(() => {
    if (isOpen) {
      loadConversations();
    }
  }, [isOpen]);

  // Scroll to bottom when new messages arrive or greeting is shown
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, showDefaultGreeting]);

  const handleSend = async (message: string) => {
    await sendMessage(message, currentConversation?.id);
  };

  const handleInputFocus = async () => {
    // Show default greeting only if no messages and haven't shown greeting yet
    if (messages.length === 0 && !hasSentGreeting && !isLoading) {
      setHasSentGreeting(true);
      setShowDefaultGreeting(true);
    }
  };

  const handleNewChat = () => {
    clearCurrentConversation();
    setHasSentGreeting(false);
    setShowDefaultGreeting(false);
    setShowSidebar(false);
  };

  const handleSelectConversation = (conversation: Conversation) => {
    loadConversation(conversation.id);
    setHasSentGreeting(false);
    setShowDefaultGreeting(false);
    setShowSidebar(false);
  };

  const handleDeleteConversation = async (conversationId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      await deleteConversation(conversationId);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-20 right-4 w-[450px] h-[600px] bg-white dark:bg-gray-800 rounded-lg shadow-2xl border border-gray-200 dark:border-gray-700 flex flex-col z-50">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-t-lg">
        <div className="flex items-center gap-2">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <h3 className="font-semibold text-lg">AI Assistant</h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleNewChat}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            title="New Chat"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </button>
          <button
            onClick={() => setShowSidebar(!showSidebar)}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
            title="History"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/20 rounded-lg transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Sidebar - Conversation History */}
      {showSidebar && (
        <div className="absolute left-0 top-14 bottom-0 w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 shadow-lg z-10 overflow-y-auto">
          <div className="p-2">
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2 px-2">Recent Conversations</h4>
            {conversations.length === 0 ? (
              <p className="text-sm text-gray-600 dark:text-gray-400 px-2 py-4">No conversations yet</p>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => handleSelectConversation(conv)}
                  className={`w-full text-left p-2 rounded-lg mb-1 transition-colors flex items-center justify-between group cursor-pointer ${
                    currentConversation?.id === conv.id
                      ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-900 dark:text-blue-200'
                      : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-200'
                  }`}
                >
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium truncate">{conv.title}</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">
                      {conv.message_count || 0} messages
                    </div>
                  </div>
                  <button
                    onClick={(e) => handleDeleteConversation(conv.id, e)}
                    className="ml-2 p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-red-100 dark:hover:bg-red-900/30 text-gray-500 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-all"
                    title="Delete conversation"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 bg-gray-50 dark:bg-gray-900">
        {error && (
          <div className="mb-4 p-3 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700 text-red-700 dark:text-red-200 rounded-lg text-sm">
            {error}
          </div>
        )}

        {messages.length === 0 && !showDefaultGreeting ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-700 dark:text-gray-300">
            <svg className="w-16 h-16 mb-4 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            <p className="text-center">
              Start a conversation!<br />
              <span className="text-sm">Try: &quot;Create a task to buy groceries&quot;</span>
            </p>
          </div>
        ) : (
          <>
            {showDefaultGreeting && (
              <div className="flex justify-start mb-4">
                <div className="max-w-[80%] rounded-lg px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100">
                  <div className="text-sm whitespace-pre-wrap break-words">
                    👋 Hello! I&apos;m your AI task assistant. I can help you create, view, complete, or delete tasks. What would you like to do?
                  </div>
                </div>
              </div>
            )}
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isSending && (
              <div className="flex justify-start mb-4">
                <div className="bg-gray-200 dark:bg-gray-700 rounded-lg px-4 py-2">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      <ChatInput
        onSend={handleSend}
        onFocus={handleInputFocus}
        disabled={isSending}
        placeholder={isLoading ? "Loading..." : "Ask me to create or manage tasks..."}
      />
    </div>
  );
}
