import { useState, useCallback, useEffect } from 'react';
import { Message, Conversation, ChatResponse } from '@/types/chatbot';
import { sendMessage, sendMessageStream, getConversations, getConversation, deleteConversation } from '@/services/chatbot';

interface UseChatbotReturn {
  messages: Message[];
  conversations: Conversation[];
  currentConversation: Conversation | null;
  isLoading: boolean;
  isSending: boolean;
  error: string | null;
  sendMessage: (message: string, conversationId?: number) => Promise<void>;
  loadConversation: (conversationId: number) => Promise<void>;
  loadConversations: () => Promise<void>;
  deleteConversation: (conversationId: number) => Promise<void>;
  clearCurrentConversation: () => void;
}

export function useChatbot(): UseChatbotReturn {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Load all conversations
   */
  const loadConversations = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    // Add timeout to prevent infinite loading (10 seconds)
    const timeoutId = setTimeout(() => {
      setIsLoading(false);
      setConversations([]);
    }, 10000);
    
    try {
      const data = await getConversations();
      clearTimeout(timeoutId);
      setConversations(data);
    } catch (err: any) {
      console.error('Failed to load conversations:', err);
      // Don't show error for aborted requests (timeout or navigation)
      if (err.message?.includes('aborted') || err.message?.includes('timeout')) {
        console.warn('Request timed out, showing empty conversations');
      }
      setError(err.message?.includes('aborted') ? 'Loading timed out' : err.message || 'Failed to load conversations');
      setConversations([]); // Set empty array on error
    } finally {
      clearTimeout(timeoutId);
      setIsLoading(false);
    }
  }, []);

  /**
   * Load a specific conversation with its messages
   */
  const loadConversation = useCallback(async (conversationId: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getConversation(conversationId);
      setCurrentConversation(data.conversation);
      setMessages(data.messages);
    } catch (err: any) {
      setError(err.message || 'Failed to load conversation');
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Send a message to the chatbot with streaming
   */
  const handleSendMessage = useCallback(async (message: string, conversationId?: number) => {
    // Don't send empty messages
    if (!message || !message.trim()) {
      console.warn('Attempted to send empty message - ignoring');
      return;
    }

    setIsSending(true);
    setError(null);

    // Add user message to the list immediately (optimistic update)
    const userMessage: Message = {
      id: Date.now(),
      conversation_id: conversationId || 0,
      user_id: 'current-user',
      role: 'user',
      content: message,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);

    // Create assistant message placeholder for streaming
    const assistantMessageId = Date.now() + 1;
    const assistantMessage: Message = {
      id: assistantMessageId,
      conversation_id: conversationId || 0,
      user_id: 'current-user',
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString(),
    };

    // Add empty assistant message to show streaming starts
    setMessages((prev) => [...prev, assistantMessage]);

    try {
      let fullResponse = '';
      let responseConversationId = conversationId || 0;

      try {
        // Use streaming endpoint
        const result = await sendMessageStream(
          {
            message,
            conversation_id: conversationId,
            metadata: {
              api_url: process.env.NEXT_PUBLIC_API_URL,
            },
          },
          // On chunk received
          (chunk: string) => {
            fullResponse += chunk;
            // Update the assistant message with the accumulated response
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMessageId
                  ? { ...msg, content: fullResponse }
                  : msg
              )
            );
          },
          // On tool call (optional)
          (toolCalls: any[]) => {
            console.log('Tool calls:', toolCalls);
          }
        );

        responseConversationId = result.conversation_id;
      } catch (streamError: any) {
        console.warn('Streaming failed, falling back to regular endpoint:', streamError.message);
        
        // Fallback to non-streaming endpoint
        const response = await sendMessage({
          message,
          conversation_id: conversationId,
          metadata: {
            api_url: process.env.NEXT_PUBLIC_API_URL,
          },
        });

        fullResponse = response.reply;
        responseConversationId = response.conversation_id;
        
        // Update message with full response
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessageId
              ? { ...msg, content: fullResponse, conversation_id: responseConversationId }
              : msg
          )
        );
      }

      // Update final message with conversation ID
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMessageId
            ? { ...msg, conversation_id: responseConversationId }
            : msg
        )
      );

      // Update current conversation if needed
      if (!currentConversation || currentConversation.id !== responseConversationId) {
        await loadConversation(responseConversationId);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
      console.error('Send message error:', err);
      // Remove the optimistic messages on error
      setMessages((prev) => prev.filter((m) => m.id !== userMessage.id && m.id !== assistantMessageId));
    } finally {
      setIsSending(false);
    }
  }, [currentConversation, loadConversation, sendMessage]);

  /**
   * Delete a conversation
   */
  const handleDeleteConversation = useCallback(async (conversationId: number) => {
    setIsLoading(true);
    setError(null);
    try {
      await deleteConversation(conversationId);
      setConversations((prev) => prev.filter((c) => c.id !== conversationId));
      if (currentConversation?.id === conversationId) {
        setCurrentConversation(null);
        setMessages([]);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to delete conversation');
    } finally {
      setIsLoading(false);
    }
  }, [currentConversation]);

  /**
   * Clear current conversation
   */
  const clearCurrentConversation = useCallback(() => {
    setCurrentConversation(null);
    setMessages([]);
  }, []);

  return {
    messages,
    conversations,
    currentConversation,
    isLoading,
    isSending,
    error,
    sendMessage: handleSendMessage,
    loadConversation,
    loadConversations,
    deleteConversation: handleDeleteConversation,
    clearCurrentConversation,
  };
}
