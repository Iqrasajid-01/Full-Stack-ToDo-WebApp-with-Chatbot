// Frontend-specific data types

export interface User {
  id: string;
  email: string;
  name: string | null;
  emailVerified: boolean;
  createdAt: Date;
  updatedAt: Date | null;
  isActive: boolean;
}

export interface Task {
  id: string;
  userId: string;
  title: string;
  description?: string;
  isCompleted: boolean;
  priority: 'low' | 'medium' | 'high';
  dueDate?: string;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
}

export interface Session {
  id: string;
  userId: string;
  token: string;
  expiresAt: string;
  createdAt: string;
  lastAccessedAt: string;
  deviceInfo?: string;
  isActive: boolean;
}

export interface TaskFilter {
  status: 'all' | 'pending' | 'completed';
  priority?: 'low' | 'medium' | 'high';
  page?: number;
  limit?: number;
}

export interface LoadingState {
  isLoading: boolean;
  isSubmitting?: boolean;
}

export interface ErrorState {
  hasError: boolean;
  errorMessage?: string;
}

export interface FormState {
  isValid: boolean;
  errors: { [field: string]: string };
}

export interface ApiResponse<T> {
  status: 'success' | 'error';
  data?: T;
  message?: string;
  errors?: Array<{ field: string; message: string }>;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    currentPage: number;
    totalPages: number;
    totalItems: number;
    hasNext: boolean;
    hasPrevious: boolean;
  };
}

export interface ValidationError {
  field: string;
  message: string;
}