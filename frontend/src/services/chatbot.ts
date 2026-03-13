import { ChatRequest, ChatResponse, Conversation, ConversationWithMessages } from '@/types/chatbot';
import { taskEvents } from '@/lib/bus';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Get auth token from localStorage
 */
function getAuthToken(): string | null {
  return localStorage.getItem('auth-token');
}

/**
 * Get headers with authentication
 */
function getHeaders(): HeadersInit {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

/**
 * Send a message to the chatbot with streaming response
 */
export async function sendMessageStream(
  request: ChatRequest,
  onChunk: (chunk: string) => void,
  onToolCall?: (toolCalls: any[]) => void
): Promise<{ conversation_id: number; tool_calls?: any[] }> {
  const token = getAuthToken();
  
  try {
    const response = await fetch(`${API_URL}/api/chatbot/message/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Failed to send message' }));
      throw new Error(errorData.detail || `HTTP ${response.status}: Failed to send message`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('ReadableStream not supported');
    }

    const decoder = new TextDecoder();
    let conversationId = request.conversation_id || 0;
    let toolCalls: any[] = [];

    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        break;
      }

      const chunk = decoder.decode(value, { stream: true });
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));

            if (data.chunk) {
              onChunk(data.chunk);
            }

            if (data.tool_calls) {
              toolCalls = data.tool_calls;
              onToolCall?.(data.tool_calls);
            }

            if (data.done) {
              conversationId = data.conversation_id || request.conversation_id || 0;
            }

            if (data.error) {
              throw new Error(data.error);
            }
          } catch (error) {
            console.warn('Failed to parse SSE data:', error);
          }
        }
      }
    }

    return { conversation_id: conversationId, tool_calls: toolCalls.length > 0 ? toolCalls : undefined };
  } catch (error: any) {
    console.error('Streaming error:', error);
    throw error;
  }
}

/**
 * Send a message to the chatbot (non-streaming, for backwards compatibility)
 */
export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/api/chatbot/message`, {
    method: 'POST',
    headers: getHeaders(),
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to send message' }));
    throw new Error(error.detail || 'Failed to send message');
  }

  const result = await response.json();

  // Emit refresh event if task was modified
  if (result.tool_calls && result.tool_calls.length > 0) {
    const hasTaskModification = result.tool_calls.some((tc: any) =>
      ['add_task', 'complete_task', 'delete_task', 'update_task'].includes(tc.tool)
    );
    if (hasTaskModification) {
      // Delay refresh slightly to allow backend to commit
      setTimeout(() => taskEvents.emitRefresh(), 500);
    }
  }

  return result;
}

/**
 * Get all conversations for the current user
 */
export async function getConversations(limit = 20, offset = 0): Promise<Conversation[]> {
  const response = await fetch(
    `${API_URL}/api/chatbot/conversations?limit=${limit}&offset=${offset}`,
    {
      headers: getHeaders(),
    }
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to get conversations' }));
    throw new Error(error.detail || 'Failed to get conversations');
  }

  return response.json();
}

/**
 * Get a specific conversation with its messages
 */
export async function getConversation(conversationId: number): Promise<ConversationWithMessages> {
  const response = await fetch(`${API_URL}/api/chatbot/conversation/${conversationId}`, {
    headers: getHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to get conversation' }));
    throw new Error(error.detail || 'Failed to get conversation');
  }

  return response.json();
}

/**
 * Delete a conversation
 */
export async function deleteConversation(conversationId: number): Promise<{ message: string }> {
  const response = await fetch(`${API_URL}/api/chatbot/conversation/${conversationId}`, {
    method: 'DELETE',
    headers: getHeaders(),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Failed to delete conversation' }));
    throw new Error(error.detail || 'Failed to delete conversation');
  }

  return response.json();
}
