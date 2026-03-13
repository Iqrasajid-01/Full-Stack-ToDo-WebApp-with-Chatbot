'use client';

import { useState, useEffect, useCallback } from 'react';
import { Task } from '@/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/contexts/auth-context';
import { useTheme } from '@/contexts/theme-context';
import { apiService } from '@/lib/api';
import { taskEvents } from '@/lib/bus';
import { MoonIcon, SunIcon } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { DragDropContext, Droppable, Draggable, type DropResult, type DroppableProvided, type DraggableProvided } from 'react-beautiful-dnd';

export default function DashboardPage() {
  const { user, signOut, loading: authLoading } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [originalTasks, setOriginalTasks] = useState<Task[]>([]); // Store original tasks for filtering
  const [newTask, setNewTask] = useState({ title: '', description: '', priority: 'medium' as 'low' | 'medium' | 'high', dueDate: '', dueTime: '' });
  const [editingTask, setEditingTask] = useState<Task | null>(null); // Track the task being edited
  const [editForm, setEditForm] = useState({ title: '', description: '', priority: 'medium' as 'low' | 'medium' | 'high', dueDate: '', dueTime: '' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Memoize fetchTasks to avoid recreating it on every render
  const fetchTasks = useCallback(async () => {
    if (!user) {
      setError('User not authenticated. Please sign in.');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const response = await apiService.get('/api/');

      if (Array.isArray(response)) {
        // Map the response to match the Task interface
        const mappedTasks = response.map(task => ({
          id: String(task.id), // Convert to string to match interface
          userId: String(task.user_id), // Backend uses snake_case
          title: task.title,
          description: task.description || '',
          isCompleted: task.completed || false, // Backend uses 'completed'
          priority: task.priority || 'medium',
          dueDate: task.due_date ? new Date(task.due_date).toISOString() : undefined, // Backend uses snake_case
          createdAt: new Date(task.created_at).toISOString(), // Backend uses snake_case
          updatedAt: task.updated_at ? new Date(task.updated_at).toISOString() : new Date(task.created_at).toISOString(), // Backend uses snake_case
          completedAt: task.completed_at ? new Date(task.completed_at).toISOString() : undefined // Backend uses snake_case
        }));
        setTasks(mappedTasks);
        setOriginalTasks(mappedTasks); // Store original tasks for filtering
      } else {
        setTasks([]);
        setOriginalTasks([]); // Store original tasks for filtering
      }
    } catch (err: any) {
      console.error('Error fetching tasks:', err);
      // Don't show error for aborted requests (user navigated away or timeout)
      if (err.message?.includes('aborted') || err.message?.includes('timeout')) {
        console.warn('Task fetch was aborted or timed out');
        setTasks([]);
        setOriginalTasks([]);
      } else if (err.message.includes('Network error')) {
        setError(`Connection issue: ${err.message}`);
      } else {
        setError(err.message || 'Failed to load tasks. Please refresh the page.');
      }
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (user) {
      fetchTasks();
    }
  }, [user, fetchTasks]);

  // Listen for task refresh events from chatbot
  useEffect(() => {
    const unsubscribe = taskEvents.onRefresh(() => {
      console.log('Refreshing tasks after chatbot action');
      fetchTasks();
    });
    return unsubscribe;
  }, [fetchTasks]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setNewTask(prev => ({ ...prev, [name]: value }));
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!user) {
      setError('User not authenticated. Please sign in.');
      return;
    }

    setLoading(true); // Set loading state

    try {
      // Combine date and time into a single datetime string
      let combinedDateTime = null;
      if (newTask.dueDate && newTask.dueTime) {
        const dateTimeString = `${newTask.dueDate}T${newTask.dueTime}`;
        combinedDateTime = new Date(dateTimeString).toISOString();
      }

      const response = await apiService.post('/api/', {
        title: newTask.title,
        description: newTask.description,
        completed: false, // Default to not completed
        priority: newTask.priority, // Send the selected priority
        due_date: combinedDateTime // Send the combined date and time if both are provided
      });

      // Ensure the response matches the Task interface
      const newTaskItem = {
        id: String(response.id),
        userId: String(response.user_id),
        title: response.title,
        description: response.description || '',
        isCompleted: response.completed || false,
        priority: response.priority || 'medium',
        dueDate: response.due_date ? new Date(response.due_date).toISOString() : undefined,
        createdAt: new Date(response.created_at).toISOString(),
        updatedAt: response.updated_at ? new Date(response.updated_at).toISOString() : new Date(response.created_at).toISOString(),
        completedAt: response.completed_at ? new Date(response.completed_at).toISOString() : undefined
      };

      setTasks(prev => [newTaskItem, ...prev]);
      setOriginalTasks(prev => [newTaskItem, ...prev]); // Also update original tasks
      setNewTask({ title: '', description: '', priority: 'medium' as 'low' | 'medium' | 'high', dueDate: '', dueTime: '' });
      setError(null); // Clear any previous errors
    } catch (err: any) {
      console.error('Error creating task:', err);
      
      // Check if it's an authentication error (401)
      if (err.message && (err.message.includes('401') || err.message.includes('Unauthorized'))) {
        setError('Session expired. Please sign in again.');
        // Optionally, redirect to sign-in page
        setTimeout(() => {
          window.location.href = '/signin';
        }, 2000);
      } 
      // Check if it's a network error
      else if (err.message.includes('Network error')) {
        setError(`Connection issue: ${err.message}`);
      } else {
        setError(err.message || 'Failed to create task. Please try again.');
      }
    } finally {
      setLoading(false); // Reset loading state
    }
  };

  const toggleTaskCompletion = async (taskId: string) => {
    if (!user) {
      setError('User not authenticated. Please sign in.');
      return;
    }

    // Optimistic update: immediately update the UI before making the API call
    setTasks(prev =>
      prev.map(task =>
        task.id === taskId ? {
          ...task,
          isCompleted: !task.isCompleted, // Toggle the current status
          updatedAt: new Date().toISOString() // Use current time temporarily
        } : task
      )
    );

    // Also update the original tasks array
    setOriginalTasks(prev =>
      prev.map(task =>
        task.id === taskId ? {
          ...task,
          isCompleted: !task.isCompleted, // Toggle the current status
          updatedAt: new Date().toISOString() // Use current time temporarily
        } : task
      )
    );

    // If we're currently editing this task, update the editingTask state too
    if (editingTask && editingTask.id === taskId) {
      setEditingTask({
        ...editingTask,
        isCompleted: !editingTask.isCompleted, // Toggle the current status
        updatedAt: new Date().toISOString() // Use current time temporarily
      });
    }

    try {
      const response = await apiService.patch(`/api/${taskId}/complete`, {});
      const updatedTaskData = {
        ...response,
        isCompleted: response.completed, // Use the response value
        dueDate: response.due_date ? new Date(response.due_date).toISOString() : undefined,
        createdAt: new Date(response.created_at).toISOString(),
        updatedAt: new Date(response.updated_at).toISOString(),
        completedAt: response.completed_at ? new Date(response.completed_at).toISOString() : undefined
      };

      // Update with actual server response
      setTasks(prev =>
        prev.map(task =>
          task.id === taskId ? {
            ...task,
            isCompleted: updatedTaskData.isCompleted,
            updatedAt: updatedTaskData.updatedAt,
            dueDate: updatedTaskData.dueDate || task.dueDate
          } : task
        )
      );

      // Also update the original tasks array
      setOriginalTasks(prev =>
        prev.map(task =>
          task.id === taskId ? {
            ...task,
            isCompleted: updatedTaskData.isCompleted,
            updatedAt: updatedTaskData.updatedAt,
            dueDate: updatedTaskData.dueDate || task.dueDate
          } : task
        )
      );

      // If we're currently editing this task, update the editingTask state too
      if (editingTask && editingTask.id === taskId) {
        setEditingTask({
          ...editingTask,
          isCompleted: updatedTaskData.isCompleted,
          updatedAt: updatedTaskData.updatedAt,
          dueDate: updatedTaskData.dueDate || editingTask.dueDate
        });
      }
    } catch (err: any) {
      console.error('Error toggling task completion:', err);
      
      // Rollback the optimistic update on error
      setTasks(prev =>
        prev.map(task =>
          task.id === taskId ? {
            ...task,
            isCompleted: !task.isCompleted, // Revert the toggle
            updatedAt: task.updatedAt // Revert to previous time
          } : task
        )
      );

      // Also revert the original tasks array
      setOriginalTasks(prev =>
        prev.map(task =>
          task.id === taskId ? {
            ...task,
            isCompleted: !task.isCompleted, // Revert the toggle
            updatedAt: task.updatedAt // Revert to previous time
          } : task
        )
      );

      // If we were editing this task, revert that too
      if (editingTask && editingTask.id === taskId) {
        setEditingTask({
          ...editingTask,
          isCompleted: !editingTask.isCompleted, // Revert the toggle
          updatedAt: editingTask.updatedAt // Revert to previous time
        });
      }
      
      // Check if it's a rate limit error (429)
      if (err.message && err.message.includes('429')) {
        setError('Too many requests. Please slow down and try again later.');
      }
      // Check if it's an authentication error (401)
      else if (err.message && (err.message.includes('401') || err.message.includes('Unauthorized'))) {
        setError('Session expired. Please sign in again.');
        // Optionally, redirect to sign-in page
        setTimeout(() => {
          window.location.href = '/signin';
        }, 2000);
      } 
      // Check if it's a network error
      else if (err.message.includes('Network error')) {
        setError(`Connection issue: ${err.message}`);
      } else {
        setError(err.message || 'Failed to update task status. Please try again.');
      }
    }
  };

  const deleteTask = async (taskId: string) => {
    if (!user) {
      setError('User not authenticated. Please sign in.');
      return;
    }

    if (!confirm('Are you sure you want to delete this task?')) return;

    try {
      await apiService.delete(`/api/${taskId}`);
      setTasks(prev => prev.filter(task => task.id !== taskId));
      setOriginalTasks(prev => prev.filter(task => task.id !== taskId)); // Also update original tasks
    } catch (err: any) {
      console.error('Error deleting task:', err);
      
      // Check if it's an authentication error (401)
      if (err.message && (err.message.includes('401') || err.message.includes('Unauthorized'))) {
        setError('Session expired. Please sign in again.');
        // Optionally, redirect to sign-in page
        setTimeout(() => {
          window.location.href = '/signin';
        }, 2000);
      } 
      // Check if it's a network error
      else if (err.message.includes('Network error')) {
        setError(`Connection issue: ${err.message}`);
      } else {
        setError(err.message || 'Failed to delete task. Please try again.');
      }
    }
  };

  const startEditingTask = (task: Task) => {
    setEditingTask(task);
    // Parse the due date for the form
    let dateStr = '';
    let timeStr = '';
    if (task.dueDate) {
      const dueDate = new Date(task.dueDate);
      dateStr = dueDate.toISOString().split('T')[0]; // Format as YYYY-MM-DD
      timeStr = dueDate.toTimeString().substring(0, 5); // Format as HH:MM
    }
    
    setEditForm({
      title: task.title,
      description: task.description || '',
      priority: task.priority,
      dueDate: dateStr,
      dueTime: timeStr
    });
  };

  const handleEditChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setEditForm(prev => ({ ...prev, [name]: value }));
  };

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!user || !editingTask) {
      setError('User not authenticated or no task selected for editing.');
      return;
    }

    setLoading(true);

    try {
      // Combine date and time into a single datetime string
      let combinedDateTime = null;
      if (editForm.dueDate && editForm.dueTime) {
        const dateTimeString = `${editForm.dueDate}T${editForm.dueTime}`;
        combinedDateTime = new Date(dateTimeString).toISOString();
      }

      const response = await apiService.put(`/api/${editingTask.id}`, {
        title: editForm.title,
        description: editForm.description,
        priority: editForm.priority,
        due_date: combinedDateTime // Send the combined date and time if both are provided
      });

      // Update the task in the state
      const updatedTask = {
        id: String(response.id),
        userId: String(response.user_id),
        title: response.title,
        description: response.description || '',
        isCompleted: editingTask.isCompleted, // Use the status from the modal
        priority: response.priority || 'medium',
        dueDate: response.due_date ? new Date(response.due_date).toISOString() : undefined,
        createdAt: new Date(response.created_at).toISOString(),
        updatedAt: response.updated_at ? new Date(response.updated_at).toISOString() : new Date(response.created_at).toISOString(),
        completedAt: response.completed_at ? new Date(response.completed_at).toISOString() : undefined
      };

      setTasks(prev => prev.map(task => task.id === editingTask.id ? updatedTask : task));
      setOriginalTasks(prev => prev.map(task => task.id === editingTask.id ? updatedTask : task));

      // Reset editing state
      setEditingTask(null);
      setEditForm({ title: '', description: '', priority: 'medium' as 'low' | 'medium' | 'high', dueDate: '', dueTime: '' });
      setError(null);
    } catch (err: any) {
      console.error('Error updating task:', err);
      
      // Check if it's an authentication error (401)
      if (err.message && (err.message.includes('401') || err.message.includes('Unauthorized'))) {
        setError('Session expired. Please sign in again.');
        // Optionally, redirect to sign-in page
        setTimeout(() => {
          window.location.href = '/signin';
        }, 2000);
      } 
      // Check if it's a network error
      else if (err.message.includes('Network error')) {
        setError(`Connection issue: ${err.message}`);
      } else {
        setError(err.message || 'Failed to update task. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (taskId: string) => {
    if (!user) {
      setError('User not authenticated. Please sign in.');
      return;
    }

    // Optimistic update: immediately update the UI before making the API call
    setTasks(prev =>
      prev.map(task =>
        task.id === taskId ? {
          ...task,
          isCompleted: !task.isCompleted, // Toggle the current status
          updatedAt: new Date().toISOString() // Use current time temporarily
        } : task
      )
    );

    // Also update the original tasks array
    setOriginalTasks(prev =>
      prev.map(task =>
        task.id === taskId ? {
          ...task,
          isCompleted: !task.isCompleted, // Toggle the current status
          updatedAt: new Date().toISOString() // Use current time temporarily
        } : task
      )
    );

    // If we're currently editing this task, update the editingTask state too
    if (editingTask && editingTask.id === taskId) {
      setEditingTask({
        ...editingTask,
        isCompleted: !editingTask.isCompleted, // Toggle the current status
        updatedAt: new Date().toISOString() // Use current time temporarily
      });
    }

    try {
      const response = await apiService.patch(`/api/${taskId}/complete`, {});
      const updatedTaskData = {
        ...response,
        isCompleted: response.completed, // Use the response value
        dueDate: response.due_date ? new Date(response.due_date).toISOString() : undefined,
        createdAt: new Date(response.created_at).toISOString(),
        updatedAt: new Date(response.updated_at).toISOString(),
        completedAt: response.completed_at ? new Date(response.completed_at).toISOString() : undefined
      };

      // Update with actual server response
      setTasks(prev =>
        prev.map(task =>
          task.id === taskId ? {
            ...task,
            isCompleted: updatedTaskData.isCompleted,
            updatedAt: updatedTaskData.updatedAt,
            dueDate: updatedTaskData.dueDate || task.dueDate
          } : task
        )
      );

      // Also update the original tasks array
      setOriginalTasks(prev =>
        prev.map(task =>
          task.id === taskId ? {
            ...task,
            isCompleted: updatedTaskData.isCompleted,
            updatedAt: updatedTaskData.updatedAt,
            dueDate: updatedTaskData.dueDate || task.dueDate
          } : task
        )
      );

      // If we're currently editing this task, update the editingTask state too
      if (editingTask && editingTask.id === taskId) {
        setEditingTask({
          ...editingTask,
          isCompleted: updatedTaskData.isCompleted,
          updatedAt: updatedTaskData.updatedAt,
          dueDate: updatedTaskData.dueDate || editingTask.dueDate
        });
      }
    } catch (err: any) {
      console.error('Error toggling task completion:', err);
      
      // Rollback the optimistic update on error
      setTasks(prev =>
        prev.map(task =>
          task.id === taskId ? {
            ...task,
            isCompleted: !task.isCompleted, // Revert the toggle
            updatedAt: task.updatedAt // Revert to previous time
          } : task
        )
      );

      // Also revert the original tasks array
      setOriginalTasks(prev =>
        prev.map(task =>
          task.id === taskId ? {
            ...task,
            isCompleted: !task.isCompleted, // Revert the toggle
            updatedAt: task.updatedAt // Revert to previous time
          } : task
        )
      );

      // If we were editing this task, revert that too
      if (editingTask && editingTask.id === taskId) {
        setEditingTask({
          ...editingTask,
          isCompleted: !editingTask.isCompleted, // Revert the toggle
          updatedAt: editingTask.updatedAt // Revert to previous time
        });
      }
      
      // Check if it's a rate limit error (429)
      if (err.message && err.message.includes('429')) {
        setError('Too many requests. Please slow down and try again later.');
      }
      // Check if it's an authentication error (401)
      else if (err.message && (err.message.includes('401') || err.message.includes('Unauthorized'))) {
        setError('Session expired. Please sign in again.');
        // Optionally, redirect to sign-in page
        setTimeout(() => {
          window.location.href = '/signin';
        }, 2000);
      } 
      // Check if it's a network error
      else if (err.message.includes('Network error')) {
        setError(`Connection issue: ${err.message}`);
      } else {
        setError(err.message || 'Failed to update task status. Please try again.');
      }
    }
  };

  const cancelEditing = () => {
    setEditingTask(null);
    setEditForm({ title: '', description: '', priority: 'medium' as 'low' | 'medium' | 'high', dueDate: '', dueTime: '' });
  };

  if (authLoading || (loading && !user)) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-900">
        <p className="text-gray-900 dark:text-white">Loading...</p>
      </div>
    );
  }

  if (!user && !authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-900">
        <p className="text-gray-900 dark:text-white">Please sign in to view your dashboard.</p>
      </div>
    );
  }

  // Calculate task statistics
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(task => task.isCompleted).length;
  const pendingTasks = totalTasks - completedTasks;

  // Prepare data for the pie chart
  const pieChartData = [
    { name: 'Completed', value: completedTasks, color: '#10B981' }, // green
    { name: 'Pending', value: pendingTasks, color: '#FBBF24' },   // yellow
  ].filter(item => item.value > 0); // Only show items with values > 0

  // Handle drag end event
  const onDragEnd = (result: any) => {
    // Dropped outside the list
    if (!result.destination) {
      return;
    }

    const items = Array.from(tasks);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    setTasks(items);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-900">
      <header className="bg-white shadow-sm dark:bg-gray-800 dark:text-white">
        <div className="max-w-7xl mx-auto px-4 py-5 sm:px-6 lg:px-8 flex justify-between items-center">
          <div>
            <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">Todo Dashboard</h1>
            <p className="text-gray-600 mt-1 dark:text-gray-300">Manage your tasks efficiently</p>
          </div>
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              onClick={toggleTheme}
              className="bg-transparent border-0 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full p-2 min-w-[32px]"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? (
                <SunIcon className="h-5 w-5 text-yellow-500" />
              ) : (
                <MoonIcon className="h-5 w-5 text-gray-700" />
              )}
            </Button>
            <div className="text-right hidden sm:block">
              <p className="text-sm text-gray-500 dark:text-gray-300">Logged in as</p>
              <p className="text-gray-900 dark:text-white font-medium truncate max-w-[150px]">{user?.name || user?.email}</p>
            </div>
            <Button
              variant="danger"
              onClick={async () => {
                await signOut(); // Sign out via auth service
                localStorage.removeItem('auth-token'); // Also remove token from localStorage
                window.location.href = '/signin'; // Redirect to sign in
              }}
              className="flex items-center"
            >
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
              </svg>
              Logout
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 mt-6">
        {error && (
          <div className="rounded-md bg-red-50 p-4 mb-4 border border-red-200 dark:bg-red-900/30 dark:border-red-700">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800 dark:text-red-200">Error</h3>
                <div className="mt-2 text-sm text-red-700 dark:text-red-300">
                  <p>{error}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Create Task Form */}
        <div className="mb-8 bg-white p-6 rounded-lg shadow-md border border-gray-200 dark:bg-gray-800 dark:border-gray-700">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">Create New Task</h2>
          <form onSubmit={handleCreateTask} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Task Title
                </label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={newTask.title}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-black bg-white dark:text-white dark:bg-gray-700 dark:border-gray-600"
                  placeholder="Enter task title"
                />
              </div>
              <div>
                <label htmlFor="priority" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Priority
                </label>
                <select
                  id="priority"
                  name="priority"
                  value={newTask.priority}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-black bg-white dark:text-white dark:bg-gray-700 dark:border-gray-600"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
              <div>
                <label htmlFor="dueDate" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Due Date
                </label>
                <input
                  type="date"
                  id="dueDate"
                  name="dueDate"
                  value={newTask.dueDate}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-black bg-white dark:text-white dark:bg-gray-700 dark:border-gray-600"
                />
              </div>
              <div>
                <label htmlFor="dueTime" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Due Time
                </label>
                <input
                  type="time"
                  id="dueTime"
                  name="dueTime"
                  value={newTask.dueTime}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-black bg-white dark:text-white dark:bg-gray-700 dark:border-gray-600"
                />
              </div>
            </div>
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Description
              </label>
              <textarea
                id="description"
                name="description"
                value={newTask.description}
                onChange={handleInputChange}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-black bg-white dark:text-white dark:bg-gray-700 dark:border-gray-600"
                placeholder="Enter task description"
              />
            </div>
            <Button
              type="submit"
              className="w-full md:w-auto"
              disabled={!newTask.title.trim() || loading} // Disable if title is empty or loading
            >
              {loading ? 'Adding Task...' : 'Add Task'}
            </Button>
          </form>
        </div>

        {/* User Progress Cards - Positioned between "Create New Task" and "Your Tasks" */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Task Overview</h2>
            {/* Quick Action Buttons */}
            <div className="flex space-x-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setTasks(originalTasks.filter(t => !t.isCompleted))}
                className="border-gray-300 text-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:text-white dark:bg-gray-700 dark:hover:bg-gray-600"
              >
                Show Pending
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setTasks(originalTasks.filter(t => t.isCompleted))}
                className="border-gray-300 text-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:text-white dark:bg-gray-700 dark:hover:bg-gray-600"
              >
                Show Completed
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setTasks(originalTasks)}
                className="border-gray-300 text-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:text-white dark:bg-gray-700 dark:hover:bg-gray-600"
              >
                Show All
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Total Tasks Card */}
            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 dark:bg-gray-800 dark:border-gray-700 flex flex-col items-center text-center">
              <div className="p-3 rounded-lg bg-indigo-100 dark:bg-indigo-900/30 mb-3">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 text-indigo-600 dark:text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <div>
                <p className="text-xl font-medium text-gray-600 dark:text-gray-300 mb-1">Total Tasks</p>
                <p className="text-6xl font-bold text-gray-900 dark:text-white">{totalTasks}</p>
              </div>
            </div>

            {/* Completed Tasks Card */}
            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 dark:bg-gray-800 dark:border-gray-700 flex flex-col items-center text-center">
              <div className="p-3 rounded-lg bg-green-100 dark:bg-green-900/30 mb-3">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="text-xl font-medium text-gray-600 dark:text-gray-300 mb-1">Completed</p>
                <p className="text-6xl font-bold text-gray-900 dark:text-white">{completedTasks}</p>
              </div>
            </div>

            {/* Pending Tasks Card */}
            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 dark:bg-gray-800 dark:border-gray-700 flex flex-col items-center text-center">
              <div className="p-3 rounded-lg bg-yellow-100 dark:bg-yellow-900/30 mb-3">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 text-yellow-600 dark:text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="text-xl font-medium text-gray-600 dark:text-gray-300 mb-1">Pending</p>
                <p className="text-6xl font-bold text-gray-900 dark:text-white">{pendingTasks}</p>
              </div>
            </div>

            {/* Chart Card */}
            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 dark:bg-gray-800 dark:border-gray-700 flex flex-col items-center justify-center">
              <h3 className="text-xl font-medium text-gray-600 dark:text-gray-300 mb-2">Completion Rate</h3>
              <div className="w-32 h-32">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieChartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={30}
                      outerRadius={50}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {pieChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value) => [`${value}`, 'Tasks']}
                      labelFormatter={() => ''}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-2 text-center">
                {totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0}% completed
              </p>
            </div>
          </div>
        </div>

        {/* Tasks List */}
        <div>
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Your Tasks</h2>

          {tasks.length === 0 ? (
            <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-200 dark:bg-gray-800 dark:border-gray-700">
              <p className="text-gray-500 text-lg dark:text-gray-400">No tasks found. Create a new task to get started!</p>
            </div>
          ) : (
            <DragDropContext onDragEnd={onDragEnd}>
              <Droppable droppableId="tasks" isDropDisabled={false} direction="vertical" isCombineEnabled={false} ignoreContainerClipping={false}>
                {(provided: any) => (
                  <div
                    {...provided.droppableProps}
                    ref={provided.innerRef}
                    className="space-y-4"
                  >
                    {tasks.map((task, index) => (
                      <Draggable key={task.id} draggableId={task.id} index={index}>
                        {(provided: any) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                            className={`p-5 rounded-lg border transition-all duration-200 ${
                              task.isCompleted
                                ? 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800'
                                : 'bg-white border-gray-200 hover:shadow-md dark:bg-gray-800 dark:border-gray-700'
                            }`}
                          >
                            <div className="flex justify-between items-start">
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center">
                                  <h3 className={`text-lg font-medium truncate ${
                                    task.isCompleted ? 'line-through text-gray-500 dark:text-gray-400' : 'text-gray-900 dark:text-white'
                                  }`}>
                                    {task.title}
                                  </h3>
                                </div>
                                {task.description && (
                                  <p className="text-gray-600 mt-2 whitespace-pre-wrap dark:text-gray-300">{task.description}</p>
                                )}
                                <div className="flex flex-wrap items-center gap-3 mt-3">
                                  <span className={`px-2.5 py-0.5 text-xs font-medium rounded-full inline-flex items-center ${
                                    task.priority === 'high'
                                      ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200'
                                      : task.priority === 'medium'
                                        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200'
                                        : 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200'
                                  }`}>
                                    <span className={`w-2 h-2 rounded-full mr-1.5 ${
                                      task.priority === 'high'
                                        ? 'bg-red-500'
                                        : task.priority === 'medium'
                                          ? 'bg-yellow-500'
                                          : 'bg-green-500'
                                    }`}></span>
                                    {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)} Priority
                                  </span>
                                  {task.dueDate && (
                                    <span className="inline-flex items-center text-xs text-gray-500 dark:text-gray-400">
                                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                      </svg>
                                      Due {new Date(task.dueDate).toLocaleDateString()}
                                    </span>
                                  )}
                                  <span className="inline-flex items-center text-xs text-gray-500 dark:text-gray-400">
                                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                    </svg>
                                    Created {new Date(task.createdAt).toLocaleDateString()}
                                  </span>
                                </div>
                              </div>

                              <div className="flex items-center space-x-2 ml-4 flex-shrink-0">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => startEditingTask(task)}
                                  className="text-blue-600 hover:text-blue-800 hover:bg-blue-50 dark:text-blue-400 dark:hover:text-blue-200 dark:hover:bg-blue-900/30"
                                >
                                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                                  </svg>
                                  Edit
                                </Button>
                                <Button
                                  variant={task.isCompleted ? 'secondary' : 'primary'}
                                  size="sm"
                                  onClick={() => toggleTaskCompletion(task.id)}
                                  className={`min-w-[80px] ${task.isCompleted ? 'dark:text-gray-900 dark:hover:text-gray-900' : ''}`}
                                >
                                  {task.isCompleted ? 'Undo' : 'Complete'}
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => deleteTask(task.id)}
                                  className="text-red-600 hover:text-red-800 hover:bg-red-50 dark:text-red-400 dark:hover:text-red-200 dark:hover:bg-red-900/30"
                                >
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                                  </svg>
                                  Delete
                                </Button>
                              </div>
                            </div>
                          </div>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </div>
                )}
              </Droppable>
            </DragDropContext>
          )}
        </div>
      </main>

      {/* Edit Task Modal */}
      {editingTask && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-md p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Edit Task</h3>
              <button 
                onClick={cancelEditing}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label htmlFor="edit-title" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Title
                </label>
                <input
                  type="text"
                  id="edit-title"
                  name="title"
                  value={editForm.title}
                  onChange={handleEditChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-black bg-white dark:text-white dark:bg-gray-700 dark:border-gray-600"
                  placeholder="Task title"
                />
              </div>
              
              <div>
                <label htmlFor="edit-description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Description
                </label>
                <textarea
                  id="edit-description"
                  name="description"
                  value={editForm.description}
                  onChange={handleEditChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-black bg-white dark:text-white dark:bg-gray-700 dark:border-gray-600"
                  placeholder="Task description"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="edit-priority" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Priority
                  </label>
                  <select
                    id="edit-priority"
                    name="priority"
                    value={editForm.priority}
                    onChange={handleEditChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-black bg-white dark:text-white dark:bg-gray-700 dark:border-gray-600"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
                
                <div>
                  <label htmlFor="edit-status" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Status
                  </label>
                  <select
                    id="edit-status"
                    name="isCompleted"
                    value={editingTask.isCompleted ? 'completed' : 'pending'}
                    onChange={async (e) => {
                      const newStatus = e.target.value === 'completed';
                      // Update the local state immediately
                      setEditingTask({...editingTask, isCompleted: newStatus});
                      // Call the API to update the status
                      await handleStatusChange(editingTask.id);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-black bg-white dark:text-white dark:bg-gray-700 dark:border-gray-600"
                  >
                    <option value="pending">Pending</option>
                    <option value="completed">Completed</option>
                  </select>
                </div>
              </div>
              
              <div>
                <label htmlFor="edit-dueDate" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Due Date & Time
                </label>
                <div className="flex space-x-2">
                  <input
                    type="date"
                    id="edit-dueDate"
                    name="dueDate"
                    value={editForm.dueDate}
                    onChange={handleEditChange}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-black bg-white dark:text-white dark:bg-gray-700 dark:border-gray-600"
                  />
                  <input
                    type="time"
                    id="edit-dueTime"
                    name="dueTime"
                    value={editForm.dueTime}
                    onChange={handleEditChange}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-black bg-white dark:text-white dark:bg-gray-700 dark:border-gray-600"
                  />
                </div>
              </div>
            </div>
            
            <div className="mt-6 flex justify-end space-x-3">
              <Button
                variant="ghost"
                onClick={cancelEditing}
                className="px-4 py-2 text-sm"
              >
                Cancel
              </Button>
              <Button
                variant="primary"
                onClick={handleSaveEdit}
                className="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-700 text-white"
              >
                Save Changes
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}