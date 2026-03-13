export interface Message {
  id: number;
  conversation_id: number;
  user_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  tool_calls?: Record<string, any>;
}

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

export interface ConversationWithMessages {
  conversation: Conversation;
  messages: Message[];
}

export interface ChatRequest {
  message: string;
  conversation_id?: number;
  metadata?: Record<string, any>;
}

export interface ChatResponse {
  reply: string;
  conversation_id: number;
  tool_calls?: ToolCall[];
  metadata?: Record<string, any>;
}

export interface ToolCall {
  tool: string;
  parameters: Record<string, any>;
  result?: Record<string, any>;
}
